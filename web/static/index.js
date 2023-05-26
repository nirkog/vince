async function handle_click(e) {
	const loading_ring = document.querySelector("#loading_ring");
	const input = document.querySelector("#username_input");
	const result_table = document.querySelector("#result_table");
	const use_availability_cache_checkbox = document.querySelector("#use_availability_cache");

	result_table.style.display = "none";
	while (result_table.firstChild) {
		result_table.removeChild(result_table.firstChild);
	}

	loading_ring.style.display = "inline-block";
		
	let response = await fetch(`/get_availability/${input.value}?availability_cache=${Number(use_availability_cache_checkbox.checked)}`);
	response = await response.json();

	loading_ring.style.display = "none";
	
	let head_row = document.createElement("tr");
	let movie_name_header = document.createElement("th");
	movie_name_header.innerHTML = "Movie name";
	head_row.appendChild(movie_name_header);

	for (let i = 0; i < response.platforms.length; i++) {
		let header = document.createElement("th");
		header.innerHTML = response.platforms[i];
		head_row.appendChild(header);
	}
	result_table.appendChild(head_row);

	let movies = Object.keys(response.movies);

	movies.forEach((movie) => {
		let row = document.createElement("tr");

		let name_cell = document.createElement("td");
		name_cell.innerHTML = movie;
		row.appendChild(name_cell);

		for (let j = 0; j < response.platforms.length; j++) {
			let cell = document.createElement("td");

			if (response.movies[movie][j] == "None") {
				cell.innerHTML = "❌";
			} else {
				let link = document.createElement("a");
				link.href = response.movies[movie][j];
				link.innerHTML = "✔️";
				link.rel = "noreferrer noopener";
				link.target = "_blank";
				cell.appendChild(link);
			}

			row.appendChild(cell);
		}

		result_table.appendChild(row);
	});

	result_table.style.display = "inline-block";
}

const button = document.querySelector("#submit_button");
const input = document.querySelector("#username_input");

/* Add enter to submit */
input.onkeypress = (e) => {
	if (e.key == "Enter") {
		e.preventDefault();
		button.click();
	}
};

button.onclick = handle_click;
