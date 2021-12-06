import time
import requests
from bs4 import BeautifulSoup

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
        players = t_body.find_all("tr", class_="Table__TR Table__even")
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
        
        return data, data_pts


class Scorecard():

    def __init__(self) -> None:
        pass

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

def main():

    t_url = "https://www.espn.com/golf/leaderboard?tournamentId=3742"
    scorecard_url = "https://www.espn.com/golf/player/scorecards/_/id/3448/tournamentId/3742"
    # run_player_scorecard(t_url)

    tournament = TournamentParticipants()

    tournament.run_tournament_scorecards(t_url)

    


if __name__ == "__main__":
    main()