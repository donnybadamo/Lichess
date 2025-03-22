import berserk
from flask import Flask, request, render_template_string

# Setup Flask app
app = Flask(__name__)

# Initialize Lichess API client
api_token = "EXAMPLE"
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
        game_data = list(client.games.export_by_player(username, max=number_of_games))

        # Get IDs of games and lost games
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

        # Gather openings for all games
        all_openings = [client.games.export(i)['opening']['name'] for i in id_list]
        all_opening_counts = {opening: all_openings.count(opening) for opening in set(all_openings)}

        real_games_played = len(all_openings)

        # Gather lost openings
        lost_openings = [client.games.export(i)['opening']['name'] for i in lost_id_list]
        lost_opening_counts = {opening: lost_openings.count(opening) for opening in set(lost_openings)}

        # Calculate loss percentages
        opening_percentages = {
            opening: (
                lost_opening_counts.get(opening, 0),
                total_count,
                round((lost_opening_counts.get(opening, 0) / total_count) * 100, 2)
            )
            for opening, total_count in all_opening_counts.items()
        }

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
