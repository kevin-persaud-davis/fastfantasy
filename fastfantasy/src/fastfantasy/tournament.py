import requests
from bs4 import BeautifulSoup
from time import strptime

class EspnTournament():

    def __init__(self) -> None:

        self.tournament_info = {
            "tournament_id":"",
            "tournament_name":"",
            "date":"",
            "tournament_purse":"",
            "winning_score":"",
            "winner_name":"",
            "winner_id":"",
            "season_id":"",
        }

    def get_tournament_id(self):
        return self.tournament_info["tournament_id"]
    
    def set_tournament_id(self, url):
        t_id = url[url.rfind("=") + 1:]
        self.tournament_info["tournament_id"] = t_id
