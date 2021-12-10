import os
from pathlib import Path, PurePath
import sys
from csv import DictWriter
import time
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import fnmatch
import path_config

import requests
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd

class TournamentParticipants():

    def __init__(self) -> None:
        self.player_ids = []
        self.player_scorecards = []

    def find_player_id(self, player):
        """Find player id

        Args:
            player (str) : tournament participant

        Returns:
            player id
        """
        id_ = "id/"
        beg = player.find(id_) + len(id_)
        end = player.rfind("/")

        return player[beg:end]

    def set_player_ids(self, t_body):
        """Get player ids from tournament body
        
        """
        player_ids = []
        players = t_body.find_all("tr")
        if players is not None:
            for player in players:
                p_id_link = player.find("a")
                # ensure that espn has player links on page
                # if not, there is no player information
                if p_id_link is not None:
                    p_id = self.find_player_id(p_id_link["href"])
                    player_ids.append(p_id)

        self.player_ids = player_ids

    def set_scorecard_urls(self, t_id):
        
        if self.player_ids is not None:
            scorecard_front = "https://www.espn.com/golf/player/scorecards/_/id/"
            scorecard_back = "/tournamentId/"
            self.player_scorecards = [scorecard_front + player + scorecard_back + t_id
                                    for player in self.player_ids]
    
    def run_tournament_scorecards(self, url):

        espn_home_url = "https://www.espn.com/golf/"

        t_id = url[url.rfind("=")+1:]
        base_url = url

        if (t_id != "1155") and (t_id != "995"):
            with requests.Session() as session:

                time.sleep(3)
                
                # home_page = session.get(espn_home_url)

                page = session.get(base_url)

                if page.status_code == 200: 
                    print("good url: ", url)
                
                    soup = BeautifulSoup(page.content, "html.parser")
                    # Table's on webpage. index with -1 in case of playoff table
                    tourn_tables = soup.select("div.ResponsiveTable")

                    if tourn_tables is not None:
                        
                        if len(tourn_tables) == 1 or len(tourn_tables) == 2:
            
                            tourn_table = tourn_tables[-1]
                            tourn_body = tourn_table.find("tbody", class_="Table__TBODY")
                            self.set_player_ids(tourn_body)
                            self.set_scorecard_urls(t_id)
                            
                            
                        elif len(tourn_tables) == 0:

                            print(f"error with {url}")

                            page = session.get(espn_home_url)
                            return url

                        else:
                            print(f"Number of tables {len(tourn_tables)} in url {url}")

                else:
                    h_page = session.get(espn_home_url)


def p_scorecard(scorecard_url):

    with requests.Session() as session:
            
        page = session.get(scorecard_url)

        if page.status_code == 200:

            soup = BeautifulSoup(page.content, "lxml")
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

class GolfRound():

    def __init__(self) -> None:
        self.data = {}
        self.data_pts = {}

    def set_round_data(self, rd_base, rd_name):
        """Get player data for specific round in tournament

        Args:
            round_base (element.Tag) : tournament round data
        
        Returns:
            data (dict) : tournament round shot score data. item entries 
                        contain ints to reflect scoring data

            data_pts (dict) : tournament round hole score data. item entries
                        contain strs to reflect scoring data

        """
        front_hole_ids = [rd_name + "_" + str(hn) for hn in range(1,10)]
        back_hole_ids = [rd_name + "_" + str(hn) for hn in range(10, 19)]
        
        front_pts_id = [h_id + "_pts" for h_id in front_hole_ids]
        back_pts_id = [h_id + "_pts" for h_id in back_hole_ids]
        
        rd_body = rd_base.find_all("tr", class_="oddrow")
        
        rd_front_total = rd_body[-2].find_all("td", class_="textcenter")
        
        rd_back_total = rd_body[-1].find_all("td", class_="textcenter")
        
        if len(rd_front_total) == 10:
            # Disregard totals
            rd_front = rd_front_total[:-1]
            
            front_shot_data, front_hole_data = self.set_nine_holes(rd_front)

            f_labeled_data = dict(zip(front_hole_ids, front_shot_data)) 
            f_labeled_data_pts = dict(zip(front_pts_id, front_hole_data))
            
        else:
            rd_front = rd_front_total
            front_shot_data, front_hole_data = self.set_nine_holes(rd_front)
            
            f_labeled_data = dict(zip(front_hole_ids, front_shot_data))
            f_labeled_data_pts = dict(zip(front_pts_id, front_hole_data))

        if len(rd_back_total) == 10:
            rd_back = rd_back_total[:-1]
            
            back_shot_data, back_hole_data = self.set_nine_holes(rd_back)

            b_labeled_data = dict(zip(back_hole_ids, back_shot_data))
            b_labeled_data_pts = dict(zip(back_pts_id, back_hole_data))
            
        else:
            rd_back = rd_back_total
            back_shot_data, back_hole_data = self.set_nine_holes(rd_back)
            
            b_labeled_data = dict(zip(back_hole_ids, back_shot_data))
            b_labeled_data_pts = dict(zip(back_pts_id, back_hole_data))
        
        
        data = {**f_labeled_data, **b_labeled_data}
        data_pts = {**f_labeled_data_pts, **b_labeled_data_pts}

        self.data = data
        self.data_pts = data_pts
        # return data, data_pts

    def set_nine_holes(self, rd_scores):
        """Get player scores, both shot and hole data, for 9 holes

        Args:
            rd (list) : player 9 hole scoring data
        
        Returns:
            shot_data (list) : shot data for 9 holes

            hole_data (list) : hole data for 9 holes 

        """
        
        shot_data = [int(score.text) if score.text else None for score in rd_scores]
        hole_data = [score["class"][0] if score["class"][0] != "textcenter" else None for score in rd_scores]

        if len(shot_data) != 9:
            
            shot_data = self.missing_data(shot_data)
        
        if len(hole_data) != 9:

            hole_data = self.missing_data(hole_data)

        return shot_data, hole_data

    def missing_data(self, scoring_data):
        """Fill missing hole entries

        Args:
            scoring_data (list) : round data with missing entries

        Returns:
            scoring_data (list) : round data filled
        """
        missing_holes = 9 - len(scoring_data)
        missing_entries = [None] * missing_holes
        scoring_data.extend(missing_entries)
        assert len(scoring_data) == 9

        return scoring_data

    def missing_round(self, rd_name):
        """Fills missing round for player with None entires.

        Args:
            rd_name (str) : tournament round number
        
        Returns:
            data (dict) : tournament round shot score data.

            data_pts (dict) : tournament round hole score data.
        
        """
        hole_ids = [rd_name + "_" + str(hn) for hn in range(1,19)]
        hole_pts_id = [h_id + "_pts" for h_id in hole_ids]

        hole_data = [None] * 18
        hole_data_pts = [None] * 18

        data = dict(zip(hole_ids, hole_data))
        data_pts = dict(zip(hole_pts_id, hole_data_pts))
        
        self.data = data
        self.data_pts = data_pts

    def find_rd_number(self, rd):
        """Find round number for scorecard
    
        Args:
            rd (element.Tag) : div.roundSwap active. id attr
                            includes round number

        Returns:
            tournament round number
        """
        rd_name = rd["id"]
        rd_name = rd_name[:rd_name.rfind("-")]
        rd_name = rd_name.replace("-", "_")
        return rd_name

    def missing_round_number(self, scoring_base):
        """Find missing round number(s) of player during tournament.
        Ensures that same round number is not used twice.

        Args:

            scoring_base (ResultSet) :  set of player tournament rounds

        Returns:

            m_rx : missing round name (x - dependent of number of rounds missed)

        """
        rd_check = np.array(["round_1", "round_2", "round_3", "round_4"])

        if len(scoring_base) == 1:
            rd_z = np.array([self.find_rd_number(scoring_base[0])])
            missing_rds = np.setdiff1d(rd_check, rd_z)
            
            assert len(missing_rds) == 3
            m_r1 = missing_rds[0]
            m_r2 = missing_rds[1]
            m_r3 = missing_rds[2]

            return m_r1, m_r2, m_r3

        elif len(scoring_base) == 2:
            rd_z = self.find_rd_number(scoring_base[0])
            rd_y = self.find_rd_number(scoring_base[1])
            
            rds = np.array([rd_z, rd_y])

            missing_rds = np.setdiff1d(rd_check, rds)

            assert len(missing_rds) == 2
            m_r1 = missing_rds[0]
            m_r2 = missing_rds[1]

            return m_r1, m_r2
            

        elif len(scoring_base) == 3:
            rd_z = self.find_rd_number(scoring_base[0])
            rd_y = self.find_rd_number(scoring_base[1])
            rd_x = self.find_rd_number(scoring_base[2])

            rds = np.array([rd_z, rd_y, rd_x])

            missing_rds = np.setdiff1d(rd_check, rds)

            assert len(missing_rds) == 1
            m_r1 = missing_rds[0]
            
            return m_r1

        else:
            print("Incorrect number of rounds given.\n")

    
        


class Scorecard():

    def __init__(self) -> None:
        self.rds_data = {}

def handle_bad_page(player_info):
    """Handle page errors
    
    Args:
        player_info (dict) : player information

        player_scores (dict) : player scoring data

    Returns:
        Updated player data to handle espn server error
    """
    new_player_info = player_info

    
    if new_player_info["player_id"] == "4686087" and new_player_info["tournament_id"] == "401155472":

        new_shot_scores = {"round_1_1": 4,
                        "round_1_2": 5,
                        "round_1_3": 5,
                        "round_1_4": 4,
                        "round_1_5": 5,
                        "round_1_6": 7,
                        "round_1_7": 4,
                        "round_1_8": 4,
                        "round_1_9": 4,
                        "round_1_10": 4,
                        "round_1_11": 4,
                        "round_1_12": 4,
                        "round_1_13": 3,
                        "round_1_14": 4,
                        "round_1_15": 4,
                        "round_1_16": 4,
                        "round_1_17": 3,
                        "round_1_18": 6,
                        
                        "round_2_1": 4,
                        "round_2_2": 4,
                        "round_2_3": 3,
                        "round_2_4": 4,
                        "round_2_5": 4,
                        "round_2_6": 4,
                        "round_2_7": 4,
                        "round_2_8": 3,
                        "round_2_9": 5,
                        "round_2_10": 4,
                        "round_2_11": 4,
                        "round_2_12": 5,
                        "round_2_13": 5,
                        "round_2_14": 5,
                        "round_2_15": 3,
                        "round_2_16": 3,
                        "round_2_17": 3,
                        "round_2_18": 4,
                        
                        "round_3_1": None,
                        "round_3_2": None,
                        "round_3_3": None,
                        "round_3_4": None,
                        "round_3_5": None,
                        "round_3_6": None,
                        "round_3_7": None,
                        "round_3_8": None,
                        "round_3_9": None,
                        "round_3_10": None,
                        "round_3_11": None,
                        "round_3_12": None,
                        "round_3_13": None,
                        "round_3_14": None,
                        "round_3_15": None,
                        "round_3_16": None,
                        "round_3_17": None,
                        "round_3_18": None,
                        
                        "round_4_1": None,
                        "round_4_2": None,
                        "round_4_3": None,
                        "round_4_4": None,
                        "round_4_5": None,
                        "round_4_6": None,
                        "round_4_7": None,
                        "round_4_8": None,
                        "round_4_9": None,
                        "round_4_10": None,
                        "round_4_11": None,
                        "round_4_12": None,
                        "round_4_13": None,
                        "round_4_14": None,
                        "round_4_15": None,
                        "round_4_16": None,
                        "round_4_17": None,
                        "round_4_18": None,}

        new_hole_scores = {"round_1_1_pts": "par",
                        "round_1_2_pts": "bogey",
                        "round_1_3_pts": "bogey",
                        "round_1_4_pts": "bogey",
                        "round_1_5_pts": "bogey",
                        "round_1_6_pts": "double",
                        "round_1_7_pts": "par",
                        "round_1_8_pts": "bogey",
                        "round_1_9_pts": "par",
                        "round_1_10_pts": "par",
                        "round_1_11_pts": "par",
                        "round_1_12_pts": "birdie",
                        "round_1_13_pts": "par",
                        "round_1_14_pts": "par",
                        "round_1_15_pts": "par",
                        "round_1_16_pts": "par",
                        "round_1_17_pts": "par",
                        "round_1_18_pts": "bogey",
                        
                        "round_2_1_pts": "par",
                        "round_2_2_pts": "par",
                        "round_2_3_pts": "birdie",
                        "round_2_4_pts": "bogey",
                        "round_2_5_pts": "par",
                        "round_2_6_pts": "birdie",
                        "round_2_7_pts": "par",
                        "round_2_8_pts": "par",
                        "round_2_9_pts": "bogey",
                        "round_2_10_pts": "par",
                        "round_2_11_pts": "par",
                        "round_2_12_pts": "par",
                        "round_2_13_pts": "double",
                        "round_2_14_pts": "bogey",
                        "round_2_15_pts": "birdie",
                        "round_2_16_pts": "birdie",
                        "round_2_17_pts": "par",
                        "round_2_18_pts": "birdie",
                        
                        "round_3_1_pts": None,
                        "round_3_2_pts": None,
                        "round_3_3_pts": None,
                        "round_3_4_pts": None,
                        "round_3_5_pts": None,
                        "round_3_6_pts": None,
                        "round_3_7_pts": None,
                        "round_3_8_pts": None,
                        "round_3_9_pts": None,
                        "round_3_10_pts": None,
                        "round_3_11_pts": None,
                        "round_3_12_pts": None,
                        "round_3_13_pts": None,
                        "round_3_14_pts": None,
                        "round_3_15_pts": None,
                        "round_3_16_pts": None,
                        "round_3_17_pts": None,
                        "round_3_18_pts": None,
                        
                        "round_4_1_pts": None,
                        "round_4_2_pts": None,
                        "round_4_3_pts": None,
                        "round_4_4_pts": None,
                        "round_4_5_pts": None,
                        "round_4_6_pts": None,
                        "round_4_7_pts": None,
                        "round_4_8_pts": None,
                        "round_4_9_pts": None,
                        "round_4_10_pts": None,
                        "round_4_11_pts": None,
                        "round_4_12_pts": None,
                        "round_4_13_pts": None,
                        "round_4_14_pts": None,
                        "round_4_15_pts": None,
                        "round_4_16_pts": None,
                        "round_4_17_pts": None,
                        "round_4_18_pts": None,}

        new_player_scores = {**new_shot_scores, **new_hole_scores}

    if new_player_info["player_id"] == "4686086" and new_player_info["tournament_id"] == "401155472":
        new_shot_scores = {"round_1_1": 4,
                        "round_1_2": 3,
                        "round_1_3": 3,
                        "round_1_4": 2,
                        "round_1_5": 4,
                        "round_1_6": 5,
                        "round_1_7": 4,
                        "round_1_8": 2,
                        "round_1_9": 5,
                        "round_1_10": 4,
                        "round_1_11": 5,
                        "round_1_12": 5,
                        "round_1_13": 3,
                        "round_1_14": 4,
                        "round_1_15": 4,
                        "round_1_16": 4,
                        "round_1_17": 3,
                        "round_1_18": 5,
                        
                        "round_2_1": 4,
                        "round_2_2": 4,
                        "round_2_3": 4,
                        "round_2_4": 3,
                        "round_2_5": 4,
                        "round_2_6": 5,
                        "round_2_7": 4,
                        "round_2_8": 3,
                        "round_2_9": 4,
                        "round_2_10": 5,
                        "round_2_11": 5,
                        "round_2_12": 5,
                        "round_2_13": 3,
                        "round_2_14": 4,
                        "round_2_15": 4,
                        "round_2_16": 4,
                        "round_2_17": 3,
                        "round_2_18": 6,
                        
                        "round_3_1": None,
                        "round_3_2": None,
                        "round_3_3": None,
                        "round_3_4": None,
                        "round_3_5": None,
                        "round_3_6": None,
                        "round_3_7": None,
                        "round_3_8": None,
                        "round_3_9": None,
                        "round_3_10": None,
                        "round_3_11": None,
                        "round_3_12": None,
                        "round_3_13": None,
                        "round_3_14": None,
                        "round_3_15": None,
                        "round_3_16": None,
                        "round_3_17": None,
                        "round_3_18": None,
                        
                        "round_4_1": None,
                        "round_4_2": None,
                        "round_4_3": None,
                        "round_4_4": None,
                        "round_4_5": None,
                        "round_4_6": None,
                        "round_4_7": None,
                        "round_4_8": None,
                        "round_4_9": None,
                        "round_4_10": None,
                        "round_4_11": None,
                        "round_4_12": None,
                        "round_4_13": None,
                        "round_4_14": None,
                        "round_4_15": None,
                        "round_4_16": None,
                        "round_4_17": None,
                        "round_4_18": None,}

        new_hole_scores = {"round_1_1_pts": "par",
                        "round_1_2_pts": "par",
                        "round_1_3_pts": "par",
                        "round_1_4_pts": "par",
                        "round_1_5_pts": "par",
                        "round_1_6_pts": "par",
                        "round_1_7_pts": "par",
                        "round_1_8_pts": "par",
                        "round_1_9_pts": "par",
                        "round_1_10_pts": "bogey",
                        "round_1_11_pts": "bogey",
                        "round_1_12_pts": "par",
                        "round_1_13_pts": "par",
                        "round_1_14_pts": "par",
                        "round_1_15_pts": "par",
                        "round_1_16_pts": "par",
                        "round_1_17_pts": "par",
                        "round_1_18_pts": "bogey",
                        
                        "round_2_1_pts": "par",
                        "round_2_2_pts": "birdie",
                        "round_2_3_pts": "birdie",
                        "round_2_4_pts": "birdie",
                        "round_2_5_pts": "par",
                        "round_2_6_pts": "par",
                        "round_2_7_pts": "par",
                        "round_2_8_pts": "birdie",
                        "round_2_9_pts": "bogey",
                        "round_2_10_pts": "par",
                        "round_2_11_pts": "bogey",
                        "round_2_12_pts": "par",
                        "round_2_13_pts": "par",
                        "round_2_14_pts": "par",
                        "round_2_15_pts": "par",
                        "round_2_16_pts": "par",
                        "round_2_17_pts": "par",
                        "round_2_18_pts": "par",
                        
                        "round_3_1_pts": None,
                        "round_3_2_pts": None,
                        "round_3_3_pts": None,
                        "round_3_4_pts": None,
                        "round_3_5_pts": None,
                        "round_3_6_pts": None,
                        "round_3_7_pts": None,
                        "round_3_8_pts": None,
                        "round_3_9_pts": None,
                        "round_3_10_pts": None,
                        "round_3_11_pts": None,
                        "round_3_12_pts": None,
                        "round_3_13_pts": None,
                        "round_3_14_pts": None,
                        "round_3_15_pts": None,
                        "round_3_16_pts": None,
                        "round_3_17_pts": None,
                        "round_3_18_pts": None,
                        
                        "round_4_1_pts": None,
                        "round_4_2_pts": None,
                        "round_4_3_pts": None,
                        "round_4_4_pts": None,
                        "round_4_5_pts": None,
                        "round_4_6_pts": None,
                        "round_4_7_pts": None,
                        "round_4_8_pts": None,
                        "round_4_9_pts": None,
                        "round_4_10_pts": None,
                        "round_4_11_pts": None,
                        "round_4_12_pts": None,
                        "round_4_13_pts": None,
                        "round_4_14_pts": None,
                        "round_4_15_pts": None,
                        "round_4_16_pts": None,
                        "round_4_17_pts": None,
                        "round_4_18_pts": None,}


        new_player_scores = {**new_shot_scores, **new_hole_scores}

    new_player_data = {**new_player_info, **new_player_scores}
    
    return new_player_data


def missing_data(scoring_data):
    """Fill missing hole entries

    Args:
        scoring_data (list) : round data with missing entries

    Returns:
        scoring_data (list) : round data filled
    """
    missing_holes = 9 - len(scoring_data)
    missing_entries = [None] * missing_holes
    scoring_data.extend(missing_entries)
    assert len(scoring_data) == 9

    return scoring_data


def get_round_scores(rd):
    """Get player scores, both shot and hole data, for 9 holes

    Args:
        rd (list) : player 9 hole scoring data
    
    Returns:
        shot_data (list) : shot data for 9 holes

        hole_data (list) : hole data for 9 holes 

    """

    shot_data = [int(score.text) if score.text else None for score in rd ]
    hole_data = [score["class"][0] if score["class"][0] != "textcenter" else None for score in rd]

    if len(shot_data) != 9:
        
        shot_data = missing_data(shot_data)
    
    if len(hole_data) != 9:

        hole_data = missing_data(hole_data)

    return shot_data, hole_data


def round_data(round_base, rd_name):
    """Get player data for specific round in tournament

    Args:
        round_base (element.Tag) : tournament round data
    
    Returns:
        data (dict) : tournament round shot score data. item entries 
                    contain ints to reflect scoring data

        data_pts (dict) : tournament round hole score data. item entries
                    contain strs to reflect scoring data

    """
    front_hole_ids = [rd_name + "_" + str(hn) for hn in range(1,10)]
    back_hole_ids = [rd_name + "_" + str(hn) for hn in range(10, 19)]
    
    front_pts_id = [h_id + "_pts" for h_id in front_hole_ids]
    back_pts_id = [h_id + "_pts" for h_id in back_hole_ids]
    
    rd_body = round_base.find_all("tr", class_="oddrow")
    
    rd_front_total = rd_body[-2].find_all("td", class_="textcenter")
    
    rd_back_total = rd_body[-1].find_all("td", class_="textcenter")
    
    if len(rd_front_total) == 10:
        # Disregard totals
        rd_front = rd_front_total[:-1]
        
        front_shot_data, front_hole_data = get_round_scores(rd_front)

        f_labeled_data = dict(zip(front_hole_ids, front_shot_data)) 
        f_labeled_data_pts = dict(zip(front_pts_id, front_hole_data))
        
    else:
        rd_front = rd_front_total
        front_shot_data, front_hole_data = get_round_scores(rd_front)
        
        f_labeled_data = dict(zip(front_hole_ids, front_shot_data))
        f_labeled_data_pts = dict(zip(front_pts_id, front_hole_data))

    if len(rd_back_total) == 10:
        rd_back = rd_back_total[:-1]
        
        back_shot_data, back_hole_data = get_round_scores(rd_back)

        b_labeled_data = dict(zip(back_hole_ids, back_shot_data))
        b_labeled_data_pts = dict(zip(back_pts_id, back_hole_data))
        
    else:
        rd_back = rd_back_total
        back_shot_data, back_hole_data = get_round_scores(rd_back)
        
        b_labeled_data = dict(zip(back_hole_ids, back_shot_data))
        b_labeled_data_pts = dict(zip(back_pts_id, back_hole_data))
    
    
    data = {**f_labeled_data, **b_labeled_data}
    data_pts = {**f_labeled_data_pts, **b_labeled_data_pts}

    return data, data_pts


def find_rd_number(rd):
    """Find round number for scorecard
    
    Args:
        rd (element.Tag) : div.roundSwap active. id attr
                        includes round number

    Returns:
        tournament round number
    """
    rd_name = rd["id"]
    rd_name = rd_name[:rd_name.rfind("-")]
    rd_name = rd_name.replace("-", "_")
    return rd_name

def missing_round_number(scoring_base):
    """Find missing round number(s) of player during tournament.
    Ensures that same round number is not used twice.

    Args:

        scoring_base (ResultSet) :  set of player tournament rounds

    Returns:

        m_rx : missing round name (x - dependent of number of rounds missed)

    """
    rd_check = np.array(["round_1", "round_2", "round_3", "round_4"])

    if len(scoring_base) == 1:
        rd_z = np.array([find_rd_number(scoring_base[0])])
        missing_rds = np.setdiff1d(rd_check, rd_z)
        
        assert len(missing_rds) == 3
        m_r1 = missing_rds[0]
        m_r2 = missing_rds[1]
        m_r3 = missing_rds[2]

        return m_r1, m_r2, m_r3

    elif len(scoring_base) == 2:
        rd_z = find_rd_number(scoring_base[0])
        rd_y = find_rd_number(scoring_base[1])
        
        rds = np.array([rd_z, rd_y])

        missing_rds = np.setdiff1d(rd_check, rds)

        assert len(missing_rds) == 2
        m_r1 = missing_rds[0]
        m_r2 = missing_rds[1]

        return m_r1, m_r2
        

    elif len(scoring_base) == 3:
        rd_z = find_rd_number(scoring_base[0])
        rd_y = find_rd_number(scoring_base[1])
        rd_x = find_rd_number(scoring_base[2])

        rds = np.array([rd_z, rd_y, rd_x])

        missing_rds = np.setdiff1d(rd_check, rds)

        assert len(missing_rds) == 1
        m_r1 = missing_rds[0]
        
        return m_r1

    else:
        print("Incorrect number of rounds given.\n")


def missing_round(rd_name):
    """Fills missing round for player with None entires.

    Args:
        rd_name (str) : tournament round number
    
    Returns:
        data (dict) : tournament round shot score data.

        data_pts (dict) : tournament round hole score data.
    
    """
    hole_ids = [rd_name + "_" + str(hn) for hn in range(1,19)]
    hole_pts_id = [h_id + "_pts" for h_id in hole_ids]

    hole_data = [None] * 18
    hole_data_pts = [None] * 18

    data = dict(zip(hole_ids, hole_data))
    data_pts = dict(zip(hole_pts_id, hole_data_pts))
    
    return data, data_pts

def scoring_data(scoring_base):
    """Get player scoring data for each round in tournament

    Args:
        scoring_base (ResultSet) : set of player tournament rounds. Length
                            reflects number of rounds played in tournament.
    
    Returns:
        round data containing player id, tourn id, and tourn scoring data
 
    """

  
    if len(scoring_base) == 0:
        
        rd_1_data, rd_1_data_pts = missing_round("round_1")
        
        rd_2_data, rd_2_data_pts = missing_round("round_2")

        rd_3_data, rd_3_data_pts = missing_round("round_3")
        
        rd_4_data, rd_4_data_pts = missing_round("round_4")

        rds_data = {**rd_1_data, **rd_2_data, **rd_3_data, **rd_4_data,
                    **rd_1_data_pts, **rd_2_data_pts, **rd_3_data_pts, **rd_4_data_pts}

        assert len(rds_data) == 144
        return rds_data

    elif len(scoring_base) == 1:
        
        round_1 = find_rd_number(scoring_base[0])
        m_rd1, m_rd2, m_rd3 = missing_round_number(scoring_base)

        

        rd_1 = scoring_base[0]
        rd_1_data, rd_1_data_pts = round_data(rd_1, round_1)

        rd_2_data, rd_2_data_pts = missing_round(m_rd1)
        rd_3_data, rd_3_data_pts = missing_round(m_rd2)
        rd_4_data, rd_4_data_pts = missing_round(m_rd3)
        

        rds_data = {**rd_1_data, **rd_2_data, **rd_3_data, **rd_4_data,
                    **rd_1_data_pts, **rd_2_data_pts, **rd_3_data_pts, **rd_4_data_pts}

        
        assert len(rds_data) == 144
        return rds_data

    elif len(scoring_base) == 2:
        # missed cut

        round_1 = find_rd_number(scoring_base[1])
        round_2 = find_rd_number(scoring_base[0])

        m_rd1, m_rd2 = missing_round_number(scoring_base)
        

        rd_1 = scoring_base[1]
        rd_1_data, rd_1_data_pts = round_data(rd_1, round_1)
        
        rd_2 = scoring_base[0]
        rd_2_data, rd_2_data_pts = round_data(rd_2, round_2)

        rd_3_data, rd_3_data_pts = missing_round(m_rd1)
        rd_4_data, rd_4_data_pts = missing_round(m_rd2)

        rds_data = {**rd_1_data, **rd_2_data, **rd_3_data, **rd_4_data,
                    **rd_1_data_pts, **rd_2_data_pts, **rd_3_data_pts, **rd_4_data_pts}
        
        assert len(rds_data) == 144
        return rds_data

    elif len(scoring_base) == 3:

        m_rd = missing_round_number(scoring_base)

        round_1 = find_rd_number(scoring_base[2])
        round_2 = find_rd_number(scoring_base[1])
        round_3 = find_rd_number(scoring_base[0])


        rd_1 = scoring_base[2]
        rd_1_data, rd_1_data_pts = round_data(rd_1, round_1)

        rd_2 = scoring_base[1]
        rd_2_data, rd_2_data_pts = round_data(rd_2, round_2)

        rd_3 = scoring_base[0]
        rd_3_data, rd_3_data_pts = round_data(rd_3, round_3)

        rd_4_data, rd_4_data_pts = missing_round(m_rd)

        rds_data = {**rd_1_data, **rd_2_data, **rd_3_data, **rd_4_data,
                    **rd_1_data_pts, **rd_2_data_pts, **rd_3_data_pts, **rd_4_data_pts}

        assert len(rds_data) == 144
        return rds_data

    elif len(scoring_base) == 4:
        
        round_1 = find_rd_number(scoring_base[3])
        round_2 = find_rd_number(scoring_base[2])
        round_3 = find_rd_number(scoring_base[1])
        round_4 = find_rd_number(scoring_base[0])

        rd_1 = scoring_base[3]
        rd_1_data, rd_1_data_pts = round_data(rd_1, round_1)
        
        rd_2 = scoring_base[2]
        rd_2_data, rd_2_data_pts = round_data(rd_2, round_2)

        rd_3 = scoring_base[1]
        rd_3_data, rd_3_data_pts = round_data(rd_3, round_3)

        rd_4 = scoring_base[0]
        rd_4_data, rd_4_data_pts = round_data(rd_4, round_4)

        

        rds_data = {**rd_1_data, **rd_2_data, **rd_3_data, **rd_4_data,
                    **rd_1_data_pts, **rd_2_data_pts, **rd_3_data_pts, **rd_4_data_pts}
        
        assert len(rds_data) == 144
        return rds_data

    elif len(scoring_base) == 5:
        # playoff round
        round_1 = find_rd_number(scoring_base[4])
        round_2 = find_rd_number(scoring_base[3])
        round_3 = find_rd_number(scoring_base[2])
        round_4 = find_rd_number(scoring_base[1])
        
        rd_1 = scoring_base[4]
        rd_1_data, rd_1_data_pts = round_data(rd_1, round_1)
        
        rd_2 = scoring_base[3]
        rd_2_data, rd_2_data_pts = round_data(rd_2, round_2)

        
        rd_3 = scoring_base[2]
        rd_3_data, rd_3_data_pts = round_data(rd_3, round_3)

        rd_4 = scoring_base[1]
        rd_4_data, rd_4_data_pts = round_data(rd_4, round_4)


        rds_data = {**rd_1_data, **rd_2_data, **rd_3_data, **rd_4_data,
                    **rd_1_data_pts, **rd_2_data_pts, **rd_3_data_pts, **rd_4_data_pts}
        
        
        assert len(rds_data) == 144
        return rds_data

    else:
        print(len(scoring_base), " incorrect number of rounds\n")


def player_scorecard(scorecard_url):
    """Get espn player scorecard for a specific tournament.

    Args:
        scorecard_url (str) : espn url
    
    Returns:
        player scoring data for tournament

    """
    with requests.Session() as session:
            
        page = session.get(scorecard_url)

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

    player_data = [player_scorecard(player) for player in player_urls]
    print("\nNumber of players: ", len(player_data))
    return player_data


def write_tournament_data(tournament_url, f_path="raw"):
    """Write historical tournament data to disk

    Args:
        tournament_url (str) : espn tournament

    """
    # Get data for file
    tourn_data = fetch_scorecard_data(tournament_url)

    # Create columns for csv file
    tournament_ids = ["player_id", "tournament_id"]
    rd_nums = ["1_", "2_", "3_", "4_"]
    rd_ids = ["round_" + rd_num + str(i) for rd_num in rd_nums for i in range(1,19)]
    rd_pt_ids = [ids + "_pts" for ids in rd_ids]

    tournament_ids.extend(rd_ids)
    tournament_ids.extend(rd_pt_ids)

    fields = tournament_ids

    # Create unique file path from tournament id
    t_id = tournament_url[tournament_url.rfind("=")+1:]
    fn = t_id + ".csv"
    f_path = Path(path_config.DATA_RAW, fn)
    
    with open (f_path, "w", newline="") as csvfile:
        writer = DictWriter(csvfile, fieldnames=fields)
        writer.writeheader()
         
        if tourn_data is not None:

            writer.writerows(tourn_data)
        else:
            print(f"The tourn data is None: {tourn_data}")
    
    msg = f"Finished {t_id}"
    return msg

def parallel_tournament_data(tournament_urls):
    futures_list = []
    results = []
    MAX_WORKERS = 8
    m_workers = min(MAX_WORKERS, len(tournament_urls))
    with ProcessPoolExecutor(max_workers=m_workers) as executor:
        for url in tournament_urls:
            futures = executor.submit(write_tournament_data, url)
            futures_list.append(futures)

        for future in futures_list:
            try:
                result = future.result()
                results.append(result)
            except Exception as exc:
                # print(f"{result} generated an excpetion {exc}")
                results.append(None)
        return results

def get_espn_tournaments(start, end=None, all_tournaments=False):
    """Get espn tournaments for given season(s).

    Notes:
    if all_tournaments is left as False, the dataframe of tournaments
    will contain only valid tournamets. Otherwise tournaments that have
    not been cancelled will be given (this includes tournaments of match play,
    charity events, etc.)

    Args:
        start (int) : starting pga season
        end (int) : ending pga season, optional
        all_tournaments (bool) : get all or valid tournaments

    Returns:
        dataframe of tournaments for specified season(s)
    """
    if all_tournaments:
        pass
    else:
        # Create check for valid file / search for file with given start and end input.
        valid_tournaments_path = (Path(path_config, "valid_tournaments_2018.csv"))
        df = pd.read_csv(valid_tournaments_path,  date_parser=["date"])

    if end is not None:
        season_df = df[(df.season_id >= start) & (df.season_id <= end)]

    else:
        season_df = df[df.season_id == start]

    return season_df


def parallel_historical_runner(start, end=None):
    """Get historical data over given pga season(s)
    
    Args:
        start (int) : beginning pga season

        end (int) : ending pga season, optional arg

        f_path (str) : historical data directory to store data

    Returns:
        missed tournaments from to many server requests and failed connections
    """
    if end is not None:

        tournaments_df = get_espn_tournaments(start, end)
    else:
        tournaments_df = get_espn_tournaments(start)

    print(f"Number of tournaments: {tournaments_df.shape[0]}")

    base_url = "https://www.espn.com/golf/leaderboard?tournamentId="

    tournaments_df["url"] = tournaments_df["tournament_id"].apply(lambda x: base_url + str(x))

    urls = tournaments_df["url"].tolist()

    results = parallel_tournament_data(urls)
    
    missed_tourns = []
    tourn_counter = 0
    for result in results:
        if result is None:
            missed_tourns.append(urls[tourn_counter])
            print(f"URL:{urls[tourn_counter]} TYPE: {(type(urls[tourn_counter]))}")
            print(f"Length of URL : {len(urls[tourn_counter])}")
        else:
            print(result)
        tourn_counter += 1

    return missed_tourns

def clean_up_runner(tournaments):

    for tourn in tournaments:
        missed_result = write_tournament_data(tourn)
        print(missed_result)

def combine_files(root, pattern=None):
    """Combine all files in root path directory

    Parameters:
        root (str) : file path to directory of files
        pattern (str) : optional file pattern to search for in directory

    Returns:
        combined files
    """
    if pattern is not None:
        files = [PurePath(path, name) for path, subdirs, files in os.walk(root) for name in files if fnmatch(name, pattern)]
        combined_files = pd.concat([pd.read_csv(f) for f in files])

    else:
        files = [PurePath(path, name) for path, subdirs, files in os.walk(root) for name in files]
        combined_files = pd.concat([pd.read_csv(f) for f in files])

    return combined_files

def run_date_transformation(df):
    """Run and save date transformations for historical player data
    
    Args:
        df (pd.DataFrame) : historical player data
    """
    # f_path = str(Path(config.PROCESSED_HISTORICAL_DIR, "hpd_2017_2020.csv"))
    # historical_data_df = pd.read_csv(f_path)

    espn_tourn_path = (Path(path_config.DATA_RAW, "espn_tournaments_2018.csv"))
    espn_tourns_df = pd.read_csv(espn_tourn_path, parse_dates=["date"])

    tournament_date_col(df, espn_tourns_df)

    # historical_data_df.to_csv(f_path)

def tournament_date_col(df, tournament_df):
    """Create date column through tournament id mapping

    Parameters:
        df (pd.Dataframe)
        tournament_df (pd.Dataframe)
    """
    date_col = df["tournament_id"].apply(lambda x: tournament_df["date"][tournament_df["tournament_id"] == x].values[0])

    idx = 2
    df.insert(loc=idx, column="date", value=date_col)

def merge_tournaments(f_pattern, f_name):
    """Merge espn tournmants
    
    Args:
        f_pattern (str) : pattern criteria to match for files
        
        f_name (str) : file name for merged tournaments
        
    """
    f_path = Path(path_config.DATA_RAW)
    merged_data = combine_files(f_path, f_pattern)

    merged_path = Path(path_config.DATA_PROCESSED, f_name)
    if os.path.isfile(merged_path):
        # file exists so no need for headers
        merged_data.to_csv(merged_path, mode="a", header=False, index=False, date_format="%Y-%m-%d")
    else:
        merged_data.to_csv(merged_path, mode="a", header=True, index=False, date_format="%Y-%m-%d")

def main():

    t_url = "https://www.espn.com/golf/leaderboard?tournamentId=3742"
    t2_url = "https://www.espn.com/golf/leaderboard?tournamentId=3763"
    scorecard_url = "https://www.espn.com/golf/player/scorecards/_/id/3448/tournamentId/3742"
    # run_player_scorecard(t_url)

    # fetch_scorecard_data(t_url)
    # f_dest = "raw"
    # write_tournament_data(t_url)


        



if __name__ == "__main__":
    main()