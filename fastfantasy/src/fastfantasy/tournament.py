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