from fastfantasy.historical_data import TournamentParticipants
import time
import requests
from bs4 import BeautifulSoup
import pytest

@pytest.fixture
def retrieve_tournament_body():
    

    url = "https://www.espn.com/golf/leaderboard?tournamentId=3742"

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

                        return tourn_body

def test_set_player_ids(retrieve_tournament_body):

    tp = TournamentParticipants()
    tp.set_player_ids(retrieve_tournament_body)

    expected = 34
    actual = tp.player_ids

    assert expected == actual