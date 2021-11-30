import requests
from bs4 import BeautifulSoup

class EspnTournament():

    def __init__(self) -> None:
        self.tournament_id = ""
        self.tournament_name = ""
        self.date = ""
        self.purse = ""
        self.winning_score = ""
        self.winner_name = ""
        self.winner_id = ""
        self.season_id = ""

    def get_tournament_id(self):
        pass
    
    def set_tournament_id(self):
        pass

    def get_tournament_name(self):
        pass

    def set_tournament_name(self):
        pass

    def get_date(self):
        pass
    
    def set_date(self):
        pass

    def get_purse(self):
        pass

    def set_purse(self):
        pass

    def get_winning_score(self):
        pass

    def set_winning_score(self):
        pass

    def get_winner_name(self):
        pass

    def set_winner_name(self):
        pass

    def get_winner_id(self):
        pass

    def set_winner_id(self):
        pass

    def get_season_id(self):
        pass

    def set_season_id(self):
        pass


class EspnSeasonSchedule():

    b_url = "https://www.espn.com/golf/schedule/_/season/"

    def __init__(self, start_season, end_season=None) -> None:
        if end_season is not None:
            self.end = end_season
        else:
            self.end = None

        self.start = start_season

    def get_season_urls(self):
        pass

    def set_season_urls(self):
        if self.end is not None:
            season_urls = [self.b_url + str(season) 
                            for season in range(self.start, self.end+1)]
        else:
            season_urls = [f"{self.b_url}{self.start}"]
            
    def get_season_schedule(self):
        pass
    
    def set_season_schedule(self):
        pass



def main():
    pass

if __name__ == "__main__":
    
    main()