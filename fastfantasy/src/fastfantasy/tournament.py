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

    def parse_espn_dates(self, date, identifier, b_identifier=True):
        """Parse for subset date of the original date

        Args:
            date (str) - date of a tournament (ex. 'Oct 5-8 2018')
            identifier (str) - ident. to be searched for
            b_identifer (bool) - flag to tell where subset search begins

        Returns:
            subset of the date
        """
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

    def get_date(self):
        return self.tournament_info["tournament_date"]
    
    def set_date(self, tourn_meta):
        tourn_date = tourn_meta.find("span").text
        t_date = self.date_parser(tourn_date)
        self.tournament_info["tournament_date"] = t_date


espn_t = EspnTournament()

espn_t.date_parser("Oct 5-8 2018")




