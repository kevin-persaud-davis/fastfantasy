from fastfantasy.tournaments import EspnSeasonSchedule
from fastfantasy.tournament import EspnTournament

import requests
from bs4 import BeautifulSoup
import pytest

def test_season_urls():
    """Test season urls from given season inputs (start and end)"""
    expected = ['https://www.espn.com/golf/schedule/_/season/2017', 
            'https://www.espn.com/golf/schedule/_/season/2018',
            'https://www.espn.com/golf/schedule/_/season/2019']
    
    espn_ss = EspnSeasonSchedule(2017, 2019)
    espn_ss.set_season_urls()

    actual = espn_ss.get_season_urls()

    assert actual == expected

def test_season_urls_start():
    """Test season urls for only start season"""
    expected = ['https://www.espn.com/golf/schedule/_/season/2017']

    espn_ss = EspnSeasonSchedule(2017)
    espn_ss.set_season_urls()

    actual = espn_ss.get_season_urls()

    assert actual == expected

def test_espn_tournament_id():
    """Test espn tournament id"""
    tournament_url = "https://www.espn.com/golf/leaderboard?tournamentId=3802"
    expected = "3802"

    espn_t = EspnTournament()
    
    t_id = espn_t.set_tournament_id(tournament_url)
    actual = espn_t.get_tournament_id()

    assert actual == expected

@pytest.fixture
def retrieve_tournament():
    url = "https://www.espn.com/golf/leaderboard?tournamentId=3802"

    with requests.Session() as session:

            page = session.get(url)

            if page.status_code == 200:

                soup = BeautifulSoup(page.content, "html.parser")

                header = soup.find("div", class_="Leaderboard__Header")

                mt4 = header.find_all("div", class_="mt4")
                tourn_meta = mt4[-1]

                return tourn_meta


def test_espn_tournament_name(retrieve_tournament):
    
    expected = "THE CJ CUP @ NINE BRIDGES"

    espn_t = EspnTournament()

    espn_t.set_tournament_name(retrieve_tournament)

    actual = espn_t.get_tournament_name()

    assert expected == actual


def test_espn_date_parser():

    expected = "Oct 5"

    d = "Oct 5-8 2018"

    espn_t = EspnTournament()

    actual = espn_t.parse_espn_dates(d, "-")

    assert expected == actual

def test_date_parser():

    expected = "10/5/2018"

    d = "Oct 5-8 2018"

    espn_t = EspnTournament()

    actual = espn_t.date_parser(d)

    assert expected == actual

def test_date(retrieve_tournament):
    expected = "10/19/2017"

    espn_t = EspnTournament()
    
    espn_t.set_date(retrieve_tournament)

    acutal = espn_t.get_date()

    assert expected == acutal



