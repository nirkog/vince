import argparse
import tqdm
from threading import Thread

from watchlists import WATCHLISTS
from movie_platforms import MOVIE_PLATFORMS
from movie_platforms.movie_platform import SearchThread
from translators.ktuvit import KtuvitTranslator
from translators.translator import TranslationException, TranslateThread

def parse_arguments():
    parser = argparse.ArgumentParser() 

    parser.add_argument("-w", "--watchlist-type", type=str, required=True, dest="watchlist_type", help="Watchlist type")
    parser.add_argument("-lc", "--letterboxd-csv", type=str, required=False, dest="letterboxd_csv_filename", help="Letterboxd generated watchlist csv file, required if the letterboxd watchlist is chosen")
    parser.add_argument("-lu", "--letterboxd-username", type=str, required=False, dest="letterboxd_username", help="Letterboxd username to retrieve the watchlist")
    parser.add_argument("-o", "--output-file", type=str, required=False, dest="output_filename", help="If specified, the search results will be saved to this path")
    parser.add_argument("-p", "--platforms", type=str, required=False, dest="platforms", help="A comma separated list of streaming platforms to search")

    args = parser.parse_args()

    return args

def main():
    args = parse_arguments()

    if not args.watchlist_type in WATCHLISTS:
        print("BAD WATCHLIST TYPE")

    print("Loading watchlist...")
    watchlist = WATCHLISTS[args.watchlist_type](args)
    watchlist.load()

    translator = KtuvitTranslator()

    print("Translating...")
    threads = []
    for i, movie in enumerate(watchlist.movies):
        threads.append((i, TranslateThread(translator, movie)))
        threads[-1][1].start() 

    for thread in threads:
        translation = thread[1].join()
        if watchlist.movies[thread[0]].translations == None:
            watchlist.movies[thread[0]].translations = dict()
        watchlist.movies[thread[0]].translations["heb"] = translation 

    # No threading version
    # for movie in tqdm.tqdm(watchlist.movies):
    #     try:
    #         translation = translator.translate_movie_name(movie)
    #         if movie.translations == None:
    #             movie.translations = dict()
    #         movie.translations["heb"] = translation 
    #     except TranslationException:
    #         pass

    user_platforms = None
    if args.platforms != None:
        user_platforms = [platform.lower() for platform in args.platforms.split(",")]

    platforms = dict()
    for platform in MOVIE_PLATFORMS:
        if user_platforms != None:
            if not platform.lower() in user_platforms:
                continue
        platforms[platform] = MOVIE_PLATFORMS[platform]()

    print("Searching availability...")
    threads = []
    for i, movie in enumerate(watchlist.movies):
        for platform in platforms:
            threads.append((
                i,
                platform,
                SearchThread(platforms[platform], movie)))
            threads[-1][-1].start()

    for thread in tqdm.tqdm(threads):
        if watchlist.movies[thread[0]].available_platforms == None:
            watchlist.movies[thread[0]].available_platforms = dict()
        link = thread[-1].join(timeout=20)
        watchlist.movies[thread[0]].available_platforms[thread[1]] = link

    print("Finished...")

    if args.output_filename != None:
        print("Saving results...")

        data = "Movie," + ",".join([platform for platform in platforms]) + "\n"

        for movie in watchlist.movies:
            data += f"{movie.name},"
            for platform in platforms:
                if platform in movie.available_platforms:
                    data += f"{movie.available_platforms[platform]},"
            data = data[:-1] + "\n"

        with open(args.output_filename, "w") as f:
            f.write(data)

if __name__ == "__main__":
    main()
