import json
from valid_params import REGIONS, URLS

f_ranking = "../data/rankings_{}.json"

def get_rankings(region):
    """
    This method reads the rankings json files and returns a dictionary with the rankings
    """
    if region not in REGIONS:
        raise ValueError("Invalid region")

    rankings = {}        
    with open (f_ranking.format(region), "r") as f:
        data = json.load(f)
        rankings[region] = data
    return rankings


def get_players():
    """
    This method reads the players json file and returns a dictionary with the players
    """
    with open ("../data/unprocessed/players.json", "r") as f:
        data = json.load(f)
    return data


def get_events():
    """
    This method reads the events json file and returns a dictionary with the events
    """
    with open ("../data/unprocessed/events.json", "r") as f:
        data = json.load(f)
    return data


def get_matches_upcoming():
    """
    This method reads the upcoming matches json file and returns a dictionary with the upcoming matches
    """
    with open ("../data/unprocessed/matches_upcoming.json", "r") as f:
        data = json.load(f)
    return data


def get_matches_results():
    """
    This method reads the results matches json file and returns a dictionary with the results matches
    """
    with open ("../data/unprocessed/matches_results.json", "r") as f:
        data = json.load(f)
    return data


def get_data():
    """
    This method returns a dictionary with the rankings, players, events, upcoming matches and results matches
    """
    return {
        "rankings": get_rankings(),
        "players": get_players(),
        "events": get_events(),
        "matches_upcoming": get_matches_upcoming(),
        "matches_results": get_matches_results()
    }
