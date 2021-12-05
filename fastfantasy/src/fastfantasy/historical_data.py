
import requests
from bs4 import BeautifulSoup

class TournamentParticipants():

    def __init__(self) -> None:
        self.player_ids = []

    def find_player_id(self, player):
        """Find player id

        Args:
            player (str) : tournament participant

        Returns:
            player id
        """
        id_ = "id/"
        beg = player.find(id_) + len(id_)
        end = player.rfind("/")

        return player[beg:end]

    def get_player_ids(self, t_body):
        """Get player ids from tournament body
        
        """
        player_ids = []
        players = t_body.find_all("tr", class_="Table__TR Table__even")
        if players is not None:
            for player in players:
                p_id_link = player.find("a")
                # ensure that espn has player links on page
                # if not, there is no player information
                if p_id_link is not None:
                    p_id = self.find_player_id(p_id_link["href"])
                    player_ids.append(p_id)


def main():
    pass

if __name__ == "__main__":
    main()