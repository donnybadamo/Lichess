## Overall goal of project: find the opening that the player most recently lost to.

import berserk


# bullshit that allows me to do things
api_token = "EXAMPLE"
session = berserk.TokenSession(api_token)
client = berserk.Client(session=session)

#welcome and username grabbing
print("Welcome to the chess cheater, where you can find information on what to play against your opponent.\n\n")

my_un = input("Enter dude's username: ")

# getting information about my account
my_account = client.account.get()
# my_un = my_account['id']

#grabs the game data of the last x games, game_data is good for getting the 'id' of a game and determining the winner
number_of_games = 40
game_data = list(client.games.export_by_player(my_un, max = number_of_games))

#gets the id of each game
id_list = []
for game in game_data:            
    id_list.append(game['id'])

#gets the id of each lost game
lost_id_list = []
for game in game_data:
    try: ##need this for draws
        winner = game['winner']
        black_player_id = game['players']['black']['user']['id']
        white_player_id = game['players']['white']['user']['id']
        if (winner == 'black' and black_player_id == my_un) or (winner == 'white' and white_player_id == my_un):
            continue  
        else:
            lost_id_list.append(game['id'])
    except:
        pass

#grabs the opening name for the each of the games and puts it in a sorted dictionary
all_openings = []

for i in id_list:
    all_openings.append(client.games.export(i)['opening']['name'])

all_opening_counts = {}

for opening in all_openings:
    try: #need this for games that don't have openings
        if opening in all_opening_counts:
            all_opening_counts[opening] += 1
        else:
            all_opening_counts[opening] = 1
    except:
        pass

sorted_all_openings = sorted(all_opening_counts.items(), key=lambda item: item[1], reverse=True)

real_games_played = len(sorted_all_openings)

#grabs the opening name for the each of the lost games and puts it in a sorted dictionary
lost_openings = []

for i in lost_id_list:
    lost_openings.append(client.games.export(i)['opening']['name'])

lost_opening_counts = {}

for opening in lost_openings:
    if opening in lost_opening_counts:
        lost_opening_counts[opening] += 1
    else:
        lost_opening_counts[opening] = 1

sorted_lost_openings = sorted(lost_opening_counts.items(), key=lambda item: item[1], reverse=True)

# Compare the two dictionaries, calculate the loss percentage
opening_percentages = {}

for opening, total_count in all_opening_counts.items():
    lost_count = lost_opening_counts.get(opening, 0)  
    percentage = round((lost_count / total_count) * 100, 2)  
    opening_percentages[opening] = (lost_count, total_count, percentage)

# Sort the percentages by most played openings (or any other sorting criteria)
sorted_opening_percentages = sorted(opening_percentages.items(), key=lambda item: item[1][1], reverse=True)

# Output the results
games_lost = len(lost_id_list)
print(f"{my_un} lost {games_lost} out of {real_games_played} games. Here's a breakdown of the lost vs played openings percentage: \n")

count = 0

for opening, (lost_count, total_count, percentage) in sorted_opening_percentages:
    if count >=5:
        break
    print(f"{opening}: Lost {lost_count} out of {total_count} games (Loss Percentage: {percentage}%)")
    count += 1

print('\n\n')
