import requests
from bs4 import BeautifulSoup
from time import strptime

def tournament_information(url, s_id):
    
    tourn_info = {}

    with requests.Session() as session:

        page = session.get(url)

        if page.status_code == 200:
            soup = BeautifulSoup(page.content, "lxml")

            header = soup.find("div", class_="Leaderboard__Header")

            mt4 = header.find_all("div", class_="mt4")
            tourn_meta = mt4[-1]


class EspnTournament():

    def __init__(self) -> None:
        # self.tournament_id = ""
        # self.tournament_name = ""
        # self.date = ""
        # self.purse = ""
        # self.winning_score = ""
        # self.winner_name = ""
        # self.winner_id = ""
        # self.season_id = ""
        self.tournament_info = {
            "tournament_id":"",
            "tournament_name":"",
            "date":"",
            "purse":"",
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
        return self.tournament_info["tournament_info"]

    def set_tournament_name(self, tourn_meta):
        tourn_name = tourn_meta.find("h1").text
        self.tournament_info["tournament_name"] = tourn_name

    def get_date(self):
        return self.tournament_info["tournament_date"]
    
    def set_date(self, tourn_meta):
        tourn_date = tourn_meta.find("span").text
        t_date = self.date_parser(tourn_date)
        self.tournament_info["tournament_date"] = t_date

    def date_parser(self, date):

        year = date[date.rfind(" ")+1:]

        month_and_day = self.parse_espn_dates(date, "-")
        
        day = self.parse_espn_dates(month_and_day, " ", b_identifier=False)
        day = day.lstrip()
        
        month = self.parse_espn_dates(month_and_day, " ", b_identifier=True)
        month_abr = month[:3]
        month_number = strptime(month_abr, "%b").tm_mon
        
        date_str = str(month_number) + "/" + day + "/" + year
        return date_str

    def parse_espn_dates(date, identifier, b_identifier=True):
    
        if b_identifier:
            if date.find(identifier) != -1:
                b_idx = date.find(identifier)
                # Should return month
                n_date = date[:b_idx].rstrip()
                return n_date
            else:
                # special case of only one date in link
                b_idx = date.find(",")
                n_date = date[:b_idx]
                return n_date
        else:
            if date.find(identifier) != -1:
                a_idx = date.find(identifier)
                # Should return day
                return date[a_idx: ]
            else:
                print("Did not find identifier in string for: ", date)

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
        self.season_urls = []

    def get_season_urls(self):
        return self.season_urls

    def set_season_urls(self):
        if self.end is not None:
            self.season_urls = [self.b_url + str(season) 
                            for season in range(self.start, self.end+1)]
        else:
            self.season_urls = [f"{self.b_url}{self.start}"]

    def get_season_schedule(self):
        pass

    def find_schedule(self, season_url):
        
        with requests.Session() as session:

            page = session.get(season_url)
            if page.status_code == 200:
                
                soup = BeautifulSoup(page.content, "lxml")

                season_table = soup.select("div.Res")
                season_table = soup.select("div.ResponsiveTable")
                if season_table is not None:
                    season_body = season_table[0].find("tbody", class_="Table__TBODY")

                tournament_data = []
                
                tournaments = season_body.find_all("div", class_="eventAndLocation__innerCell")
                
                if tournaments is not None:
                    for tournament in tournaments:
                        tournament_url = tournament.find("a")
                        if tournament_url:    
                            t_url = tournament_url["href"]
                            print(f"Fetching {t_url} data")

                            season_id = season_url[season_url.rfind("/")+1 :]
                            t_data = tournament_information(t_url, season_id)
                            tournament_data.append(t_data)
                    
                    return tournament_data
            else:
                page.raise_for_status()

    def set_season_schedule(self):
        # iterate through season urls

        # number of season urls {0, 1, N}
        tournament_data = []
        if self.season_urls is not None:
            for url in self.season_urls:
                pass



def main():
    espn_ss = EspnSeasonSchedule(2017)
    espn_ss.set_season_urls()

    actual = espn_ss.get_season_urls()
    print(actual)

if __name__ == "__main__":
    
    main()