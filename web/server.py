import sys
import tqdm
import json
import time
import pickle
from threading import Thread
from flask import Flask, render_template, request

sys.path.append("../")

from vince.watchlists import WATCHLISTS
from vince.movie_platforms import MOVIE_PLATFORMS
from vince.movie_platforms.movie_platform import SearchThread
from vince.translators.ktuvit import KtuvitTranslator
from vince.translators.translator import TranslationException, TranslateThread

DEFAULT_CACHE_PATH = "./.vince_cache"

app = Flask(__name__)
app.jinja_env.auto_reload = True
app.config['TEMPLATES_AUTO_RELOAD'] = True

class ArgsObject():
    def __init__(self, username):
        self.letterboxd_username = username

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/get_availability/<username>")
def get_availability(username):
    start = time.time()

    args = ArgsObject(username)

    use_availability_cache = bool(int(request.args.get("availability_cache")))

    print("Loading cache...")
    cache = dict()
    try:
        with open(DEFAULT_CACHE_PATH, "rb") as f:
            cache = pickle.load(f)
    except Exception:
        pass
    
    print("Loading watchlist...")
    watchlist = WATCHLISTS["letterboxd"](args)
    watchlist.load()

    translator = KtuvitTranslator()

    print("Translating...")
    threads = []
    for i, movie in enumerate(watchlist.movies):
        if movie.name in cache:
            if "heb" in cache[movie.name]["movie"].translations:
                if watchlist.movies[i].translations == None:
                    watchlist.movies[i].translations = dict()
                watchlist.movies[i].translations["heb"] = cache[movie.name]["movie"].translations["heb"]
                continue
        threads.append((i, TranslateThread(translator, movie)))
        threads[-1][1].start() 

    for thread in threads:
        translation = thread[1].join()
        if watchlist.movies[thread[0]].translations == None:
            watchlist.movies[thread[0]].translations = dict()
        watchlist.movies[thread[0]].translations["heb"] = translation 

    user_platforms = ["yes", "mubi"]
    platforms = dict()
    for platform in MOVIE_PLATFORMS:
        if platform.lower() in user_platforms:
            platforms[platform] = MOVIE_PLATFORMS[platform]()

    print("Searching availability...")
    threads = []
    for i, movie in enumerate(watchlist.movies):
        for platform in platforms:
            if use_availability_cache:
                if movie.name in cache:
                    if time.time() - cache[movie.name]["metadata"]["time"] < cache[movie.name]["metadata"]["valid_for"]:
                        if platform in cache[movie.name]["movie"].available_platforms:
                            if watchlist.movies[i].available_platforms == None:
                                watchlist.movies[i].available_platforms = dict()
                            watchlist.movies[i].available_platforms[platform] = cache[movie.name]["movie"].available_platforms[platform]
                            continue

            threads.append((
                i,
                platform,
                SearchThread(platforms[platform], movie)))
            threads[-1][-1].start()

    for thread in tqdm.tqdm(threads):
        if watchlist.movies[thread[0]].available_platforms == None:
            watchlist.movies[thread[0]].available_platforms = dict()

        link = None
        try:
            link = thread[-1].join(timeout=20)
        except Exception:
            print("Search exception")
        watchlist.movies[thread[0]].available_platforms[thread[1]] = link

    response = dict()

    response["platforms"] = []
    for platform in platforms:
        response["platforms"].append(platform)

    response["movies"] = dict()
    for movie in watchlist.movies:
        platform_list = []
        for platform in response["platforms"]:
            platform_list.append(str(movie.available_platforms[platform]))
        response["movies"][movie.name] = platform_list

    print("Saving cache...")
    for movie in watchlist.movies:
        cache[movie.name] = dict()
        cache[movie.name]["movie"] = movie
        cache[movie.name]["metadata"] = { "time": time.time(), "valid_for": 60*60*24 }

    with open(DEFAULT_CACHE_PATH, "wb") as f:
        pickle.dump(cache, f)

    print(f"Processing took {time.time() - start}s")
    
    return json.dumps(response)
