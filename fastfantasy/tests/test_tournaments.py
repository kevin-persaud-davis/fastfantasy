from fastfantasy.tournaments import EspnSeasonSchedule

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