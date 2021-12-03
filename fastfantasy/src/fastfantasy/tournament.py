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

    def get_tournament_name(self):
        return self.tournament_info["tournament_name"]

    def set_tournament_name(self, tourn_meta):
        tourn_name = tourn_meta.find("h1").text
        self.tournament_info["tournament_name"] = tourn_name
