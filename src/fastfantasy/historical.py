import time
from typing import Callable
from pathlib import Path
from csv import DictWriter
from concurrent.futures import ThreadPoolExecutor
import path_config
from historical_data import fetch_scorecard_data, get_espn_tournaments, \
    missing_round, scoring_data, handle_bad_page
from historical_data import TournamentParticipants
    

import requests
from bs4 import BeautifulSoup

tournaments_df = get_espn_tournaments(2018)

base_url = "https://www.espn.com/golf/leaderboard?tournamentId="
tournaments_df["url"] = tournaments_df["tournament_id"].apply(lambda x: base_url + str(x))
urls = tournaments_df["url"].tolist()

def _player_scorecard(scorecard_url):
    """Get espn player scorecard for a specific tournament.

    Args:
        scorecard_url (str) : espn url
    
    Returns:
        player scoring data for tournament

    """
    with requests.Session() as session:
            
        page = session.get(scorecard_url)

        if page.status_code != 200:
            page.raise_for_status()

        if page.status_code == 200:

            soup = BeautifulSoup(page.content, "html.parser")
            base = soup.find_all("div", class_="roundSwap active")
            
            if base is not None:
                id_data = {}

                p_id_start = scorecard_url.find("id") + 3
                p_id_end = scorecard_url.rfind("tournamentId") - 1

                id_data["player_id"] = scorecard_url[p_id_start:p_id_end]
                id_data["tournament_id"] = scorecard_url[scorecard_url.rfind("/") + 1:]

                scorecard_data = scoring_data(base)
                player_data = {**id_data, **scorecard_data}

                assert len(player_data) == 146
                
                return player_data
        else:
            id_data = {}

            p_id_start = scorecard_url.find("id") + 3
            p_id_end = scorecard_url.rfind("tournamentId") - 1

            id_data["player_id"] = scorecard_url[p_id_start:p_id_end]
            id_data["tournament_id"] = scorecard_url[scorecard_url.rfind("/") + 1:]

            scorecard_data = {}

            if id_data["player_id"] == "4686086" and id_data["tournament_id"] == "401155472":
                scorecard_data = handle_bad_page(id_data)

            if id_data["player_id"] == "4686087" and id_data["tournament_id"] == "401155472":
                scorecard_data = handle_bad_page(id_data)


            if scorecard_data:

                player_data = {**id_data, **scorecard_data}
            else:
                rd_1_data, rd_1_data_pts = missing_round("round_1")
        
                rd_2_data, rd_2_data_pts = missing_round("round_2")

                rd_3_data, rd_3_data_pts = missing_round("round_3")
                
                rd_4_data, rd_4_data_pts = missing_round("round_4")

                rds_data = {**rd_1_data, **rd_2_data, **rd_3_data, **rd_4_data,
                            **rd_1_data_pts, **rd_2_data_pts, **rd_3_data_pts, **rd_4_data_pts}

                assert len(rds_data) == 144

                player_data = {**id_data, **rds_data}

            assert len(player_data) == 146
                
            return player_data

def fetch_scorecard_data(url):

    tournament = TournamentParticipants()
    tournament.run_tournament_scorecards(url)

    player_urls = tournament.player_scorecards
    print(len(player_urls))
    player_data = [_player_scorecard(player) for player in player_urls]
    print("\nNumber of players: ", len(player_data))
    return player_data


def write_tournament_data(cc: str):
    """Write historical tournament data to disk

    Args:
        tournament_url (str) : espn tournament

    """

    # Get data for file
    tourn_data = fetch_scorecard_data(cc)

    # Create columns for csv file
    tournament_ids = ["player_id", "tournament_id"]
    rd_nums = ["1_", "2_", "3_", "4_"]
    rd_ids = ["round_" + rd_num + str(i) for rd_num in rd_nums for i in range(1,19)]
    rd_pt_ids = [ids + "_pts" for ids in rd_ids]

    tournament_ids.extend(rd_ids)
    tournament_ids.extend(rd_pt_ids)

    fields = tournament_ids

    # Create unique file path from tournament id
    t_id = cc[cc.rfind("=")+1:]
    fn = t_id + ".csv"
    f_path = Path(path_config.DATA_RAW, fn)
    
    with open (f_path, "w", newline="") as csvfile:
        writer = DictWriter(csvfile, fieldnames=fields)
        writer.writeheader()
         
        if tourn_data is not None:

            writer.writerows(tourn_data)
        else:
            print(f"The tourn data is None: {tourn_data}")
    
    
    
def write_many_tournaments(cc_list: list[str]) -> int:

    for idx, cc in enumerate(cc_list):
        if idx % 2 == 0:
            cc_list.append("https://www.espn.com")
    
    for cc in cc_list:
        write_tournament_data(cc)
        print(cc, end=" ", flush=True)
    return len(cc_list)


def main(downloader: Callable[[list[str]], int]) -> None:
    t0 = time.perf_counter()
    count = downloader(urls)
    elapsed = time.perf_counter() - t0
    print(f"\n{count} downloads in {elapsed:.2f}s")

if __name__ == "__main__":
    main(write_many_tournaments)
