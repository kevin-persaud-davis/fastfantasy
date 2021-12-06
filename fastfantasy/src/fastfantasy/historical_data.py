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


# def run_player_scorecard(url):

#     espn_home_url = "https://www.espn.com/golf/"

#     t_id = url[url.rfind("=")+1:]
#     base_url = url

#     if (t_id != "1155") and (t_id != "995"):
#         with requests.Session() as session:

#             time.sleep(3)
            
#             # home_page = session.get(espn_home_url)

#             page = session.get(base_url)

#             if page.status_code == 200: 
#                 print("good url: ", url)
            
#                 soup = BeautifulSoup(page.content, "html.parser")
#                 # Table's on webpage. index with -1 in case of playoff table
#                 tourn_tables = soup.select("div.ResponsiveTable")

#                 if tourn_tables is not None:
                    
#                     if len(tourn_tables) == 1 or len(tourn_tables) == 2:
        
#                         tourn_table = tourn_tables[-1]
#                         tourn_body = tourn_table.find("tbody", class_="Table__TBODY")
                        
#                         tp = TournamentParticipants()
#                         tp.set_player_ids(tourn_body)
#                         print(tp.player_ids)

#                         tp.set_scorecard_urls(t_id)
#                         print(tp.player_scorecards)
                        
#                     elif len(tourn_tables) == 0:

#                         print(f"error with {url}")

#                         page = session.get(espn_home_url)
#                         return url

#                     else:
#                         print(f"Number of tables {len(tourn_tables)} in url {url}")

#             else:
#                 h_page = session.get(espn_home_url)


class Scorecard():

    def __init__(self) -> None:
        pass


def main():

    t_url = "https://www.espn.com/golf/leaderboard?tournamentId=3742"
    scorecard_url = "https://www.espn.com/golf/player/scorecards/_/id/3448/tournamentId/3742"
    # run_player_scorecard(t_url)

    tournament = TournamentParticipants()

    tournament.run_tournament_scorecards(t_url)

    


if __name__ == "__main__":
    main()