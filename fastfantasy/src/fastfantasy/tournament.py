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
            "win_total":"",
            "tournament_size":"",
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

    def get_tournament_purse(self):
        return self.tournament_info["tournament_purse"]

    def set_tournament_purse(self, tourn_header):
        
        purse_class = tourn_header.find("div", class_="n7 clr-gray-04").text

        # string find method
        purse_start = purse_class.find("$") + 1

        if purse_class.find("D") != -1:
            purse_end = purse_class.find("D")
            purse = purse_class[purse_start:purse_end]
        else:
            purse = purse_class[purse_start:]
        
        purse = purse.replace(",", "")

        self.tournament_info["tournament_purse"] = purse

    def get_winning_score(self):
        return self.tournament_info["win_total"]

    def set_winning_score(self, t_body):
       
        """Get winning score total for tournament

        Args:
            t_body (element.tag) : tourn table body. Child of ResponsiveTable

        Returns
            winning score total
        """
        
        # tournament winner's total's data
        tourn_totals = t_body.find("td", class_="Table__TD")
        if tourn_totals:
            totals = tourn_totals.find_next_siblings()
            if len(totals) == 9:
                # selects 4 round (72 hole) total
                total = totals[-3].text
                self.tournament_info["win_total"] = total
            else:
                total = totals[-3].text
                if len(total) == 0:
                    self.tournament_info["win_total"] = None
                else:
                    self.tournament_info["win_total"] = total

def main():

    espn_t = EspnTournament()

    espn_t.date_parser("Oct 5-8 2018")  

    
    url = "https://www.espn.com/golf/leaderboard?tournamentId=3802"
    # url = "https://www.espn.com/golf/leaderboard?tournamentId=3780"

    with requests.Session() as session:

            page = session.get(url)

            if page.status_code == 200:

                soup = BeautifulSoup(page.content, "html.parser")

                header = soup.find("div", class_="Leaderboard__Header")
                
                espn_t.set_tournament_purse(header)

                print(espn_t.get_tournament_purse())

if __name__ == "__main__":
    main()





