import requests
from bs4 import BeautifulSoup
from time import strptime

class EspnTournament():

    def __init__(self) -> None:

        self.tournament_info = {
            "tournament_id":"",
            "tournament_name":"",
            "tournament_date":"",
            "tournament_purse":"",
            "win_total":"",
            "tournament_size":"",
            "winner_name":"",
            "winner_id":"",
            "season_id":"",
        }

    def __getitem__(self, i):
        return self.tournament_info[i]

    def set_all_w(self, w_name, w_id, w_total):
        self.tournament_info["winner_name"] = w_name
        self.tournament_info["winner_id"] = w_id
        self.tournament_info["win_total"] = w_total

    def set_all_missing(self):
        self.tournament_info["win_total"] = None
        self.tournament_info["tournament_size"] = None
        self.tournament_info["winner_name"] = None
        self.tournament_info["winner_id"] = None

    def get_tournament_id(self):
        return self.tournament_info["tournament_id"]
    
    def set_tournament_id(self, url):
        """Set tournament id from a url.

        Parameters
        ----------
        url : str
            ESPN tournament url.

        Examples
        --------
        >>> espn_t = EspnTournament()
        >>> t_url = "https://www.espn.com/golf/leaderboard?tournamentId=3802"
        >>> espn_t.set_tournament_id(t_url)
        """
        t_id = url[url.rfind("=") + 1:]
        self.tournament_info["tournament_id"] = t_id

    def get_tournament_name(self):
        return self.tournament_info["tournament_name"]

    def set_tournament_name(self, tourn_meta):
        """Set tournament name from a tournament meta.

        Parameters
        ----------
        tournament_meta : element.Tag 
            child of Leaderboard__Header class to find tournament name.

        Examples
        --------
        >>> espn_t = EspnTournament()
        >>> espn_t.set_tournament_id(tourn_meta)
        """
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
        Set tournament name from a tournament meta.

        Parameters
        ----------
        date : str 
            ESPN tournament date to parse.

        identifier : str
            Identifier to be searched for.

        b_identifier : bool
            Flag to tell where subset search begins.

        Returns
        -------
        str
            Parsed ESPN date.

        Examples
        --------
        >>> espn_t = EspnTournament()
        >>> espn_t.parse_espn_dates("Oct 5-8 2018", "-")
        "Oct 5"
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
        """Reformat ESPN tournament date.

        Parameters
        ----------
        date : str 
            Date to parse.

        Returns
        -------
        str
            Reformatted ESPN date.

        Examples
        --------
        >>> espn_t = EspnTournament()
        >>> espn_t.date_parser("Oct 5-8 2018")
        "10/5/2018"
        """

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
        """Set tournament date from a tournament meta.

        Parameters
        ----------
        tourn_meta : element.Tag 
            child of Leaderboard__Header class.

        Examples
        --------
        >>> espn_t = EspnTournament()
        >>> espn_t.set_date(tourn_meta)
        """
        tourn_date = tourn_meta.find("span").text
        t_date = self.date_parser(tourn_date)
        self.tournament_info["tournament_date"] = t_date

    def get_tournament_purse(self):
        return self.tournament_info["tournament_purse"]

    def set_tournament_purse(self, tourn_header):
        """Set tournament purse from a tournament header.

        Parameters
        ----------
        tourn_header : element.Tag 
            Leaderboard__Header class.

        Examples
        --------
        >>> espn_t = EspnTournament()
        >>> espn_t.set_tournament_purse(tourn_header)
        """
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
        """Set winning score total for tournament body.

        Parameters
        ----------
        t_body : element.Tag 
            Child of ResponsiveTable.

        Examples
        --------
        >>> espn_t = EspnTournament()
        >>> espn_t.set_winning_score(t_body)
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

    def get_tournament_size(self):
        return self.tournament_info["tournament_size"]

    def set_tournament_size(self, t_body):
        """Set tournament size for tournament body.

        Parameters
        ----------
        t_body : element.Tag 
            Child of ResponsiveTable.

        Examples
        --------
        >>> espn_t = EspnTournament()
        >>> espn_t.set_tournament_size(t_body)
        """
        players = t_body.find_all("tr", class_="Table__TR Table__even")
        if players is not None:
            num_players = len(players)
            self.tournament_info["tournament_size"] = num_players

    def get_winner_name(self):
        return self.tournament_info["winner_name"]

    def set_winner_name(self, t_body):
        """Set winner name for tournament body.

        Parameters
        ----------
        t_body : element.Tag 
            Child of ResponsiveTable.

        Examples
        --------
        >>> espn_t = EspnTournament()
        >>> espn_t.set_winner_name(t_body)
        """
        winner = t_body.find("a")
        if winner:
            name = winner.text
            self.tournament_info["winner_name"] = name
        else:
            self.tournament_info["winner_name"] = None

    def get_winner_id(self):
        return self.tournament_info["winner_id"]

    def set_winner_id(self, t_body):
        """Set winner id for tournament body.

        Parameters
        ----------
        t_body : element.Tag 
            Child of ResponsiveTable.

        Examples
        --------
        >>> espn_t = EspnTournament()
        >>> espn_t.set_winner_id(t_body)
        """
        winner = t_body.find("a")
        if winner:
            winner_id = winner["href"]
            # substring start and end indexes
            start_winner = winner_id.find("id/") + 3
            end_winner = winner_id.rfind("/")

            id = winner_id[start_winner:end_winner]
            self.tournament_info["winner_id"] = id
        else:
            self.tournament_info["winner_id"] = None

    def get_season_id(self):
        return self.tournament_info["season_id"]

    def set_season_id(self, s_id):
        """Set season id from s_id.

        Parameters
        ----------
        s_id : int
            Season id to set.

        Examples
        --------
        >>> espn_t = EspnTournament()
        >>> espn_t.set_season_id(2018)
        """
        self.tournament_info["season_id"] = s_id


class EspnSeason():

    def __init__(self, start, end=None) -> None:
        b_url = "https://www.espn.com/golf/schedule/_/season/"
        if end is not None:
            season_urls = [b_url + str(season) for season in range(start, end+1)]
        else:
            season_urls = [f"{b_url}{start}"]

        self.season_urls = season_urls
        self.season_data = []
    
    def retrieve_tournament_info(self, t_url, s_id):
        
        espn_t = EspnTournament()
        
        with requests.Session() as session:

            page = session.get(t_url)

            if page.status_code == 200:
                
                soup = BeautifulSoup(page.content, "html.parser")
                header = soup.find("div", class_="Leaderboard__Header")

                mt4 = header.find_all("div", class_="mt4")
                tourn_meta = mt4[-1]

                espn_t.set_tournament_id(t_url)

                espn_t.set_tournament_name(tourn_meta)
                
                espn_t.set_date(tourn_meta)

                espn_t.set_tournament_purse(header)
                
                # Table's on webpage. index with -1 in case of playoff table
                tourn_tables = soup.select("div.ResponsiveTable")
                if tourn_tables:
                    # win_total, tournamnet_size, winner_name, winner_id
                    tourn_table = tourn_tables[-1]

                    tourn_body = tourn_table.find("tbody", class_="Table__TBODY")

                    espn_t.set_winning_score(tourn_body)

                    espn_t.set_tournament_size(tourn_body)
                    
                    espn_t.set_winner_name(tourn_body)
                    
                    espn_t.set_winner_id(tourn_body)

                    espn_t.set_season_id(s_id)
                    
                    if espn_t.get_tournament_id() == "2277":

                        espn_t.set_all_w("Scott Piercy", "1037", "265")
                        
                else:
                    print(f"No div.ResponsiveTable, (Tournament {espn_t.get_tournament_id()} Cancelled)")

                    espn_t.set_all_missing()
                    espn_t.set_season_id(s_id)

            self.season_data.append(espn_t)

    def retrieve_season(self, season_url):
        """Get all tournaments in the season with their specific identifiers
    
        Args:
            season_url (str) : espn season schedule webpage

        Returns:
            collection of espn tournament data
        """
        with requests.Session() as session:

            page = session.get(season_url)
            if page.status_code == 200:
                    
                soup = BeautifulSoup(page.content, "html.parser")

                season_table = soup.select("div.ResponsiveTable")
                if season_table is not None:
                    season_body = season_table[0].find("tbody", class_="Table__TBODY")
                
                tournaments = season_body.find_all("div", class_="eventAndLocation__innerCell")
                
                if tournaments is not None:
                    for tournament in tournaments:
                        tournament_url = tournament.find("a")
                        if tournament_url:    
                            t_url = tournament_url["href"]
                            print(f"Fetching {t_url} data")

                            season_id = season_url[season_url.rfind("/")+1 :]

                            self.retrieve_tournament_info(t_url, season_id)
            else:
                print(f"Error retrieving page. page status code: {page.status_code}")
    
    def retrieve_all_seasons(self):
        
        for season in self.season_urls:
            self.retrieve_season(season)


def main():
    
    tournament_url = "https://www.espn.com/golf/leaderboard?tournamentId=3802"
    e_season = EspnSeason(2017, 2018)
    # e_season.retrieve_tournament_info(tournament_url, 2018)

    # print(e_season.season_data[0].tournament_info)
    # tournament_data = retrieve_all_tournamet_info(tournament_url, 2018)

    season_url = "https://www.espn.com/golf/schedule/_/season/2018"
    # season_data = retrieve_full_season(season_url)

    # e_season.retrieve_season(season_url)

    # print(len(e_season.season_data))

    # for tournament in e_season.season_data:
    #     print(tournament.tournament_info)

    # for season in season_data: print(season.tournament_info)
    # print(len(season_data))
    
    e_season.retrieve_all_seasons()
    print(len(e_season.season_data))
    
    
if __name__ == "__main__":
    main()





