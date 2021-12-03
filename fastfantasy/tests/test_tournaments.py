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
def retrieve_tournament_meta():
    url = "https://www.espn.com/golf/leaderboard?tournamentId=3802"

    with requests.Session() as session:

            page = session.get(url)

            if page.status_code == 200:

                soup = BeautifulSoup(page.content, "html.parser")

                header = soup.find("div", class_="Leaderboard__Header")

                mt4 = header.find_all("div", class_="mt4")
                tourn_meta = mt4[-1]

                return tourn_meta

@pytest.fixture
def retrieve_tournament_header():
    url = "https://www.espn.com/golf/leaderboard?tournamentId=3802"

    with requests.Session() as session:

            page = session.get(url)

            if page.status_code == 200:

                soup = BeautifulSoup(page.content, "html.parser")

                header = soup.find("div", class_="Leaderboard__Header")
                return header

@pytest.fixture
def retrieve_tournament_body():

    url = "https://www.espn.com/golf/leaderboard?tournamentId=3802"

    with requests.Session() as session:

            page = session.get(url)

            if page.status_code == 200:

                soup = BeautifulSoup(page.content, "html.parser")

                header = soup.find("div", class_="Leaderboard__Header")

            # Table's on webpage. index with -1 in case of playoff table
            tourn_tables = soup.select("div.ResponsiveTable")
            if tourn_tables:
                # win_total, tournamnet_size, winner_name, winner_id
                tourn_table = tourn_tables[-1]

                tourn_body = tourn_table.find("tbody", class_="Table__TBODY")
                return tourn_body


def test_espn_tournament_name(retrieve_tournament_meta):
    
    expected = "THE CJ CUP @ NINE BRIDGES"

    espn_t = EspnTournament()

    espn_t.set_tournament_name(retrieve_tournament_meta)

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

def test_date(retrieve_tournament_meta):
    expected = "10/19/2017"

    espn_t = EspnTournament()
    
    espn_t.set_date(retrieve_tournament_meta)

    acutal = espn_t.get_date()

    assert expected == acutal


def test_tournament_purse(retrieve_tournament_header):
    expected = "9250000"

    espn_t = EspnTournament()

    espn_t.set_tournament_purse(retrieve_tournament_header)

    actual = espn_t.get_tournament_purse()

    assert expected == actual

def test_winning_score(retrieve_tournament_body):

    expected = "279"

    espn_t = EspnTournament()
    espn_t.set_winning_score(retrieve_tournament_body)

    actual = espn_t.get_winning_score()

    assert expected == actual


def test_tournament_size(retrieve_tournament_body):

    expected = 78

    espn_t = EspnTournament()
    espn_t.set_tournament_size(retrieve_tournament_body)

    actual = espn_t.get_tournament_size()

    assert expected == actual


def test_winner_name(retrieve_tournament_body):
    expected = "Justin Thomas"

    espn_t = EspnTournament()
    espn_t.set_winner_name(retrieve_tournament_body)

    actual = espn_t.get_winner_name()

    assert expected == actual

def test_winner_id(retrieve_tournament_body):

    expected = "4848"

    espn_t = EspnTournament()
    espn_t.set_winner_id(retrieve_tournament_body)

    actual = espn_t.get_winner_id()

    assert expected == actual


