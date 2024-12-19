import berserk
from flask import Flask, request, render_template_string
import timeit
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import partial

# Setup Flask app
app = Flask(__name__)

# Initialize Lichess API client
api_token = "lip_sQkKF391gXxDeGRoqGRi"
session = berserk.TokenSession(api_token)
client = berserk.Client(session=session)

# Define the HTML template
html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chess Cheater</title>
    <style>
        /* Setting the black background */
        body {
            background-color: black;
            color: white; /* Ensures text is visible on black background */
            font-family: Arial, sans-serif;
        }
    </style>
</head>
<body>
    <h1>Chess Cheater</h1>
    <form method="POST" action="/">
        <label for="username">Enter opponent's username:</label>
        <input type="text" id="username" name="username" required>
        <button type="submit">Submit</button>
    </form>

    {% if results %}
    <h2>Results for {{ username }}</h2>
    <p>{{ username }} lost {{ games_lost }} out of {{ real_games_played }} games.</p>
    <p>Here's the top 5 played openings, with percentage lost:</p>
    <ul>
        {% for opening, lost_count, total_count, percentage in results %}
        <li>{{ opening }}: Lost {{ lost_count }} out of {{ total_count }} games (Loss Percentage: {{ percentage }}%)</li>
        {% endfor %}
    </ul>
    {% endif %}
</body>
</html>
"""

# Define the Flask route for the form submission
@app.route("/", methods=["GET", "POST"])
def index():
    results = None
    username = None
    games_lost = 0
    number_of_games = 50
    real_games_played = 0

    if request.method == "POST":
        username = request.form["username"]

        # Get game data from Lichess
        # start timeit

        # Code under measurement
        # timeit is used to measure the time taken to get the game data
        # partial is used to pass the username and number of games to the function, akin to a lambda
        # list is used to convert the timeit object to a list
        partial_export = partial(client.games.export_by_player, username, max=number_of_games)
        game_data = list(timeit.timeit(partial_export, number=1))

        # end timeit

        # Get IDs of games and lost games
        def get_lost_id_list(game_data):
            id_list = [game['id'] for game in game_data]
            lost_id_list = []
            for game in game_data:
                try:
                    winner = game['winner']
                    black_player_id = game['players']['black']['user']['id']
                    white_player_id = game['players']['white']['user']['id']
                    if (winner == 'black' and black_player_id == username) or (winner == 'white' and white_player_id == username):
                        continue
                    else:
                        lost_id_list.append(game['id'])
                except:
                    pass

            return lost_id_list, id_list

        lost_id_list, id_list = get_lost_id_list(game_data)
        print(f"Time taken to get game data: {end - start}")

        # slow code zone
        # Gather openings for all games
        def gather_openings(game_data):
            # use a set for opening names to avoid duplicates
            all_openings = [
                game['opening']['name']
                for game in game_data
                if 'opening' in game and 'name' in game['opening']
            ]
            return all_openings

        # benchmark this code
        # time = timeit.timeit(lambda: Counter(gather_openings(game_data)), number=1)
        # print(f"Time taken to gather openings: {time}")

        all_opening_counts = Counter(gather_openings(game_data))
        real_games_played = all_opening_counts.elements()
        # code pretty slow above here?

        # Gather lost openings
        def gather_lost_openings(lost_id_list):
            lost_openings = []
            with ThreadPoolExecutor(max_workers=3) as executor:
                futures = {executor.submit(client.games.export, game_id): game_id for game_id in lost_id_list}
                for future in as_completed(futures):
                    try:
                        game = future.result()
                        opening = game.get('opening', {}).get('name')
                        if opening:
                            lost_openings.append(opening)
                    except Exception:
                        pass
            return lost_openings

        # time to get lost openings
        # time = timeit.timeit(lambda: gather_lost_openings(lost_id_list), number=1)
        # print(f"Time taken to gather lost openings: {time}")

        lost_openings = gather_lost_openings(lost_id_list)
        lost_opening_counts = {opening: lost_openings.count(opening) for opening in set(lost_openings)}

        # Calculate loss percentages

        def get_opening_percentages(datum):
            all_opening_counts, lost_opening_counts = datum
            opening_percentages = {
                opening: (
                    lost_count := lost_opening_counts.get(opening, 0),
                    total_count,
                    round((lost_count / total_count) * 100, 2) if total_count > 0 else 0
                )
                for opening, total_count in all_opening_counts.items()
            }
            return opening_percentages
        # here I pack the data needed into a tuple since a lambda can only take one argument
        datum = (all_opening_counts, lost_opening_counts)

        time = timeit.timeit(lambda: get_opening_percentages(datum), number=1)
        print(f"Time taken to get opening percentages: {time}")

        opening_percentages = get_opening_percentages(datum)

        # opening_percentages = {
        #     opening: (
        #         lost_opening_counts.get(opening, 0),
        #         total_count,
        #         round((lost_opening_counts.get(opening, 0) / total_count) * 100, 2)
        #     )
        #     for opening, total_count in all_opening_counts.items()
        # }

        # Sort by most played
        sorted_opening_percentages = sorted(opening_percentages.items(), key=lambda item: item[1][1], reverse=True)

        # Limit results to top 5
        results = [
            (opening, lost_count, total_count, percentage)
            for opening, (lost_count, total_count, percentage) in sorted_opening_percentages[:5]
        ]

        # Number of lost games
        games_lost = len(lost_id_list)

    return render_template_string(html_template, results=results, username=username, games_lost=games_lost, number_of_games=number_of_games, real_games_played=real_games_played)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9000, debug=True)
