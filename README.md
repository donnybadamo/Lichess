# Lichess
Collection of projects utilizing the Lichess API

## Getting Started

This project uses the uv package resolver and installer. To install the necessary packages, run the following command:

```bash
uv install
```

You may need to install `uv` first. You can do so by running the following command:

```bash
# install to macos packages (homebrew)
brew install uv

# install to windows packages
choco install uv

# install to python global packages, but isolated from a specific version
pipx install uv
```




## Project 1: Opening Finder

- Project Goal - determine the best opening to play against an opponent.
- Project Methodology -

**Files**
- opening_finder.py is the initial attempt to find the best opening to play by sorting through all of the lost games out of the last 50 games and returning the most played openings with their percentage lost. Eventually I'll update this to some weighted average but I didn't sort by percentage because I thought outliers would be a problem.
- chess_cheater.py is the 2nd attempt, taking the exact code from opening_finder but making a *very* simple locally hosted web app using flask, port 9000
