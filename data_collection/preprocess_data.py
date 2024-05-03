import pandas as pd
from pandas import json_normalize
import requests
from lxml import html
import numpy as np
import ast
import time
from get_data import get_rankings, get_players, get_events, get_matches_results
from valid_params import REGIONS

def get_ranking_df(region):
    """
    This method returns a pandas DataFrame with the rankings
    """
    rankings = get_rankings(region)
    df = pd.DataFrame(rankings[region])

    # Convert the 'teams' column from a string to a dictionary if it's a string
    if df['teams'].dtype == 'object':
        df['teams'] = df['teams'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)
    
    # Expand the dictionary into separate columns 
    teams_df = df['teams'].apply(pd.Series)
    df = pd.concat([df.drop('teams', axis=1), teams_df], axis=1)

    # turn df`total_winnings` dictionary column into separate columns
    recent_match_df = json_normalize(df['recent_match'])
    df = df.join(recent_match_df)
    df = df.drop(columns=['recent_match'])

    return df


def get_players_df():
    """
    This method returns a pandas DataFrame with the players
    """
    players = get_players()
    df = pd.DataFrame(players)

    # deserialize the players column
    players_df = json_normalize(df['players'])
    df = df.join(players_df)
    df = df.drop(columns=['players'])

    df = expand_team_name(df)

    return df


def get_events_df():
    """
    This method returns a pandas DataFrame with the events
    """
    events = get_events()
    df = pd.DataFrame(events)

    # deserialize events column
    events_df = json_normalize(df['events'])
    df = df.join(events_df)
    df = df.drop(columns=['events'])

    return df


def get_matches_results_df():
    """
    This method returns a pandas DataFrame with the results matches
    """
    matches_results = get_matches_results()
    df = pd.DataFrame(matches_results)

    # deserialize matches
    matches_df = json_normalize(df['matches'])
    df = df.join(matches_df)
    df = df.drop(columns=['matches'])

    return df


def preprocess_all_data():
    """
    This method preprocesses all the data and returns a dictionary with the rankings, players, events, upcoming matches and results matches
    """
    rankings = []
    players = get_players_df()
    events = get_events_df()
    matches_results = get_matches_results_df()
    for region in REGIONS:
        ranking = get_ranking_df(region)
        rankings.append(ranking)
    return {
        "rankings": rankings,
        "players": players,
        "events": events,
        "matches_results": matches_results
    }


def combine_data():
    """
    This method combines all the data into a single DataFrame
    """
    data = preprocess_all_data()
    rankings = pd.concat(data["rankings"])
    return {
        "rankings": rankings,
        "players": data["players"],
        "events": data["events"],
        "matches_results": data["matches_results"]
    }


def expand_team_name(df, user_agent="Mozilla/5.0"):
    """
    This method uses web scraping to get the full team name for a given player and ensures proper data type handling.
    """
    if 'team_name' not in df.columns:
        df['team_name'] = np.nan
    df['team_name'] = df['team_name'].astype(str)

    headers = {'User-Agent': user_agent}
    
    for index, row in df.iterrows():
        try:
            time.sleep(0.1)
            url = f"https://{row['player_link']}"
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                tree = html.fromstring(response.content)
                xpath = '//*[@id="wrapper"]/div[1]/div/div[2]/div[1]/div[4]/a/div[2]/div[1]'
                team_name_elements = tree.xpath(xpath)
                if team_name_elements:
                    team_name = team_name_elements[0].text_content().strip()
                    print(f"Team name: {team_name} processed")
                    # Explicitly cast the team name to string before assignment
                    df.loc[index, 'team_name'] = str(team_name)
                else:
                    df.loc[index, 'team_name'] = np.nan
            else:
                df.loc[index, 'team_name'] = np.nan
        except Exception as e:
            df.loc[index, 'team_name'] = np.nan
            print(f"Failed to process row {index}: {e}")

    return df


def final_cleaning():
    """
    Performs the final cleaning of the data
    """
    players_df = pd.read_csv("../data/processed/players.csv")
    rankings_df = pd.read_csv("../data/processed/rankings.csv")
    events_df = pd.read_csv("../data/processed/events.csv")  # not used for now
    matches_results_df = pd.read_csv("../data/processed/matches_results.csv")
    
    # Cleaning Players dataset
    if players_df['headshot_percentage'].dtype == object:
        players_df['headshot_percentage'] = players_df['headshot_percentage'].str.rstrip('%').astype(float) / 100
    if players_df['clutch_success_percentage'].dtype == object:
        players_df['clutch_success_percentage'] = players_df['clutch_success_percentage'].str.rstrip('%').astype(float) / 100
    players_df['rating'] = players_df['rating'].fillna(players_df['rating'].mean())
    for col in players_df.columns:
        if players_df[col].dtype == 'float64':
            players_df[col] = players_df[col].fillna(players_df[col].mean())

    # Cleaning Rankings dataset
    rankings_df[['wins', 'losses']] = rankings_df['record'].str.extract('(\d+)–(\d+)').astype(int)
    rankings_df['win_streak_count'] = rankings_df['win_streak'].str.extract('(\d+)').fillna(0).astype(int)
    rankings_df['is_winning_streak'] = rankings_df['win_streak'].str.contains('W')

    # Cleaning Matches Results dataset
    if matches_results_df['match_time'].dtype == object:
        matches_results_df['match_time'] = pd.to_datetime(matches_results_df['match_time'], errors='coerce')

    # Match result (*relative to team one)
    def determine_match_result(row):
        if row['team_one_score'] > row['team_two_score']:
            return 'Win'
        elif row['team_one_score'] < row['team_two_score']:
            return 'Lose'
        else:
            return 'Draw'
    matches_results_df['match_result'] = matches_results_df.apply(determine_match_result, axis=1)
    
    # Write back
    players_df.to_csv("../data/processed/players.csv", index=False)
    rankings_df.to_csv("../data/processed/rankings.csv", index=False)
    events_df.to_csv("../data/processed/events.csv", index=False)
    matches_results_df.to_csv("../data/processed/matches_results.csv", index=False)



def main():
    data = combine_data()
    print(data["rankings"].head())
    print(data["players"].head())
    print(data["events"].head())
    print(data["matches_results"].head())

    data["rankings"].to_csv("../data/processed/rankings.csv", index=False)
    data["players"].to_csv("../data/processed/players.csv", index=False)
    data["events"].to_csv("../data/processed/events.csv", index=False)
    data["matches_results"].to_csv("../data/processed/matches_results.csv", index=False)
    
    final_cleaning()  # not very efficient but idrc
    
if __name__ == '__main__':
    main()