# Lichess
Collection of projects utilizing the Lichess API


**Opening Finder**

- Project Goal - determine the best opening to play against an opponent.
- Project Methodology -
  
*Files*
- opening_finder.py is the initial attempt to find the best opening to play by sorting through all of the lost games out of the last 50 games and returning the most played openings with their percentage lost. Eventually I'll update this to some weighted average but I didn't sort by percentage because I thought outliers would be a problem.
- chess_cheater.py is the 2nd attempt, taking the exact code from opening_finder but making a *very* simple locally hosted web app using flask, port 9000
