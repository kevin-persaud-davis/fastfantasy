from pathlib import Path, PurePath
from historical_data import get_espn_tournaments
import path_config

import pandas as pd
import numpy as np

def find_subsequence(seq, subseq):
    target = np.dot(subseq, subseq)
    candidates = np.where(np.correlate(seq,
                                       subseq, mode='valid') == target)[0]
    # some of the candidates entries may be false positives, double check
    check = candidates[:, np.newaxis] + np.arange(len(subseq))
    mask = np.all((np.take(seq, check) == subseq), axis=-1)
    # yield from candidates[mask] # (generator way)
    return candidates[mask]

def birdie_streak(df):
    """Find three consecutive birdies on player scorecard

    Args:
        df (pd.Dataframe) : historical player data

    """
    np_df = df.to_numpy()
    rc = 0
    b_seq = [3,3,3]
    birdie_steak = []
    for player in np_df:
        x = find_subsequence(player, b_seq)
        if x.size > 0:
            birdie_steak.append(3)
        else:
            birdie_steak.append(0)
    return birdie_steak


class FantasyMapper():

    def __init__(self, df, tid_list):
        self.df = df[df.tournament_id.isin(tid_list)]

    def get_data(self):
        return self.df

    def get_cut(self):
        X = np.where((self.df.round_3_18 > 0) & (self.df.round_4_18 > 0),
                1,
                0)
        return X

    def set_cut(self):
        cut_mask = self.get_cut()
        self.df["made_cut"] = cut_mask

    def handle_place_ties(self):
        """Handle position ties for winners of tournaments"""

        winners = self.df[self.df["place"]==1].copy()
        df_ties = winners[winners.tournament_id.duplicated(keep=False)].reset_index()
        playoff_winners = df_ties.groupby("tournament_id").first()
        new_totals = playoff_winners[["index", "total"]].reset_index(drop=True)

        self.df["total"].iloc[new_totals["index"].values] = self.df["total"].iloc[new_totals["index"].values].apply(lambda x: x-1)
        self.df["place"] = self.df.groupby("tournament_id")["total"].rank("min")

    def set_position_rank(self):
        """Final position placing for tournament participants"""

        col_start = self.df.columns.get_loc("round_1_1")
        col_end = self.df.columns.get_loc("round_4_18") + 1

        score_cols = self.df.columns[col_start:col_end]

        self.df["total"] = np.where(self.df.made_cut, self.df[score_cols].sum(axis=1), np.nan)
        self.df["place"] = self.df.groupby("tournament_id")["total"].rank("min")
        
        self.handle_place_ties()

    def get_place_pts(self):
        """Points given  to tournament participants for finishing position 
        
        Returns:
            place_df (pd.Dataframe) : point mapping for placed finished in tournament
        """
        place_dict = {}
        for place in range(1,51):
            if place == 1:
                place_dict[place] = 30
            elif place == 2:
                place_dict[place] = 20
            elif place == 3:
                place_dict[place] = 18
            elif place == 4:
                place_dict[place] = 16
            elif place == 5:
                place_dict[place] = 14
            elif place == 6:
                place_dict[place] = 12
            elif place == 7:
                place_dict[place] = 10
            elif place == 8:
                place_dict[place] = 9
            elif place == 9:
                place_dict[place] = 8
            elif place == 10:
                place_dict[place] = 7
            elif place > 10 and place <= 15:
                place_dict[place] = 6
            elif place > 15 and place <= 20:
                place_dict[place] = 5
            elif place > 20 and place <= 25:
                place_dict[place] = 4
            elif place > 25 and place <= 30:
                place_dict[place] = 3
            elif place > 30 and place <= 40:
                place_dict[place] = 2
            elif place > 40 and place <= 50:
                place_dict[place] = 1
            else:
                continue

        place_df = pd.DataFrame(list(place_dict.items()), columns=["place", "place_pts"])
        return place_df

    def map_placings(self, place_df):
        """Map position placings, for players, with placing points

        Args:
            place_df (pd.Dataframe) : draftkings fantasy position point totals
        """
        placing_conditions = [
            self.df["place"] == place_df["place"][0],
            self.df["place"] == place_df["place"][1],
            self.df["place"] == place_df["place"][2],
            self.df["place"] == place_df["place"][3],
            self.df["place"] == place_df["place"][4],
            self.df["place"] == place_df["place"][5],
            self.df["place"] == place_df["place"][6],
            self.df["place"] == place_df["place"][7],
            self.df["place"] == place_df["place"][8],
            self.df["place"] == place_df["place"][9],
            self.df["place"] == place_df["place"][10],
            self.df["place"] == place_df["place"][11],
            self.df["place"] == place_df["place"][12],
            self.df["place"] == place_df["place"][13],
            self.df["place"] == place_df["place"][14],
            self.df["place"] == place_df["place"][15],
            self.df["place"] == place_df["place"][16],
            self.df["place"] == place_df["place"][17],
            self.df["place"] == place_df["place"][18],
            self.df["place"] == place_df["place"][19],
            self.df["place"] == place_df["place"][20],
            self.df["place"] == place_df["place"][21],
            self.df["place"] == place_df["place"][22],
            self.df["place"] == place_df["place"][23],
            self.df["place"] == place_df["place"][24],
            self.df["place"] == place_df["place"][25],
            self.df["place"] == place_df["place"][26],
            self.df["place"] == place_df["place"][27],
            self.df["place"] == place_df["place"][28],
            self.df["place"] == place_df["place"][29],
            self.df["place"] == place_df["place"][30],
            self.df["place"] == place_df["place"][31],
            self.df["place"] == place_df["place"][32],
            self.df["place"] == place_df["place"][33],
            self.df["place"] == place_df["place"][34],
            self.df["place"] == place_df["place"][35],
            self.df["place"] == place_df["place"][36],
            self.df["place"] == place_df["place"][37],
            self.df["place"] == place_df["place"][38],
            self.df["place"] == place_df["place"][39],
            self.df["place"] == place_df["place"][40],
            self.df["place"] == place_df["place"][41],
            self.df["place"] == place_df["place"][42],
            self.df["place"] == place_df["place"][43],
            self.df["place"] == place_df["place"][44],
            self.df["place"] == place_df["place"][45],
            self.df["place"] == place_df["place"][46],
            self.df["place"] == place_df["place"][47],
            self.df["place"] == place_df["place"][48],
            self.df["place"] == place_df["place"][49],
            ]
        self.df["fantasy_placing_pts"] = np.select(placing_conditions, place_df["place_pts"])

    def set_placing(self):
        """Set placing points for players"""

        p_df = self.get_place_pts()
        self.map_placings(p_df)

    def get_rd_cols(self, base_col):
        """Make columns for holes in pga tournament

        Args:
            base_col (str) : base name for column

        Returns:
            columns for holes played in tournament, total of 72
        """
        cols = []
        for rd in range(1,5):
            rd_base = base_col + str(rd)
            for hole in range(1,19):
                rd_h_cols = rd_base + "_" + str(hole)
                cols.append(rd_h_cols)
        return cols
    
    def set_hole_points(self):
        """Fantasy hole point mappings for player hole scores"""
        hole_fantasy_pts = {"eagle": 8, "birdie": 3,"par": 0.5, "bogie": -0.5, "double": -1}
        fantasy_pts_df = pd.DataFrame(list(hole_fantasy_pts.items()), columns=["hole_score", "points"])

        rd_pts_start = "round_1_1_pts"
        rd_pts_end = "round_4_18_pts"
        fantasy_points_conditions = [
            self.df.loc[:, rd_pts_start:rd_pts_end] == fantasy_pts_df.iloc[0,0],
            self.df.loc[:, rd_pts_start:rd_pts_end] == fantasy_pts_df.iloc[1,0],
            self.df.loc[:, rd_pts_start:rd_pts_end] == fantasy_pts_df.iloc[2,0],
            self.df.loc[:, rd_pts_start:rd_pts_end] == fantasy_pts_df.iloc[3,0],
            self.df.loc[:, rd_pts_start:rd_pts_end] == fantasy_pts_df.iloc[4,0]
        ]
        f_cols = self.get_rd_cols("f_pts_")
        self.df[f_cols] = np.select(fantasy_points_conditions, fantasy_pts_df["points"])
        self.df["fantasy_hole_score_pts"] = self.df[f_cols].sum(axis=1)
    
    def set_rounds_finished(self):
        """Indicate each round a player finished (i.e. all 18 holes)"""
        self.df["complete_r1"] = np.where(self.df.round_1_18 > 0, 1, 0)
        self.df["complete_r2"] = np.where(self.df.round_2_18 > 0, 1, 0)
        self.df["complete_r3"] = np.where(self.df.round_3_18 > 0, 1, 0)
        self.df["complete_r4"] = np.where(self.df.round_4_18 > 0, 1, 0)

    def set_bogey_free(self):
        """Create bogeyfree round fantasy point column
    
        Note: Add 3 points per bogey free round in tournament
        """
        bogey_rd1 = self.df.filter(like="f_pts_1_") < 0
        bogey_rd2 = self.df.filter(like="f_pts_2_") < 0
        bogey_rd3 = self.df.filter(like="f_pts_3_") < 0
        bogey_rd4 = self.df.filter(like="f_pts_4_") < 0

        self.df["bf1"] = np.where(self.df.complete_r1, bogey_rd1.sum(axis=1), np.nan)
        self.df["bf2"] = np.where(self.df.complete_r2, bogey_rd2.sum(axis=1), np.nan)
        self.df["bf3"] = np.where(self.df.complete_r3, bogey_rd3.sum(axis=1), np.nan)
        self.df["bf4"] = np.where(self.df.complete_r4, bogey_rd4.sum(axis=1), np.nan)

        self.df["fantasy_bogeyfree_pts"] = (self.df.loc[:, "bf1":"bf4"]==0).astype(int).sum(axis=1) * 3
        
    def find_birdie_streak(self):
        """Find three consecutive birdies on player scorecard"""
        np_df = self.df.to_numpy()
        rc = 0
        b_seq = [3,3,3]
        birdie_streak = []
        for player in np_df:
            x = find_subsequence(player, b_seq)
            if x.size > 0:
                birdie_streak.append(3)
            else:
                birdie_streak.append(0)
        return birdie_streak

    def set_birdie_streak(self):
        """Create biridie streak fantasy point columns"""
        f1_df = self.df.filter(like="f_pts_1_")
        f2_df = self.df.filter(like="f_pts_2_")
        f3_df = self.df.filter(like="f_pts_3_")
        f4_df = self.df.filter(like="f_pts_4_")

        self.df["birdie_streak_r1"] = birdie_streak(f1_df)
        self.df["birdie_streak_r2"] = birdie_streak(f2_df)
        self.df["birdie_streak_r3"] = birdie_streak(f3_df)
        self.df["birdie_streak_r4"] = birdie_streak(f4_df)

        self.df["fantasy_birdie_streak_pts"] = self.df.loc[:,"birdie_streak_r1":"birdie_streak_r4"].sum(axis=1)

    def set_hole_in_one(self):
        """Create hole in one fantasy point column

        Notes: Gives 5 points per hole in one to player
        """
        self.df["fantasy_hole_in_one_pts"] = self.df.loc[:, "round_1_1":"round_4_18"].isin([1]).sum(axis=1) * 5

    def set_under70(self):
        """Create under 70 fantasy point column

        Note:
            5 point fantasy bonus for player with all four completed (full 18 holes) rounds under 70
        """
        rd1_df = self.df.filter(like="rd_1")
        rd2_df = self.df.filter(like="rd_2")
        rd3_df = self.df.filter(like="rd_3")
        rd4_df = self.df.filter(like="rd_4")

        self.df["rd_total_1"] = np.where(self.df.complete_r1, rd1_df.sum(axis=1), np.nan)
        self.df["rd_total_2"] = np.where(self.df.complete_r2, rd2_df.sum(axis=1), np.nan)
        self.df["rd_total_3"] = np.where(self.df.complete_r3, rd3_df.sum(axis=1), np.nan)
        self.df["rd_total_4"] = np.where(self.df.complete_r4, rd4_df.sum(axis=1), np.nan)

        total_1 = self.df["rd_total_1"] < 70
        total_2 = self.df["rd_total_2"] < 70
        total_3 = self.df["rd_total_3"] < 70
        total_4 = self.df["rd_total_4"] < 70

        self.df["under70_1"] = np.where(total_1, 1, 0)
        self.df["under70_2"] = np.where(total_2, 1, 0)
        self.df["under70_3"] = np.where(total_3, 1, 0)
        self.df["under70_4"] = np.where(total_4, 1, 0)

        self.df["fantasy_under70_pts"] = np.where(self.df.loc[:,"under70_1":"under70_2"].sum(axis=1) == 4, 5, 0)

    def set_total_points(self):
        """Calculate total fantasy points over course of tournament"""

        self.df["fantasy_total_points"] = self.df.filter(like="fantasy_").sum(axis=1)

    def run_all_transformations(self):
        """run all fantasy transformations on df"""
        self.set_cut()
        self.set_position_rank()
        self.set_placing()
        self.set_hole_points()
        self.set_rounds_finished()
        self.set_bogey_free()
        self.set_birdie_streak()
        self.set_hole_in_one()
        self.set_under70()
        self.set_total_points()

def mapper_runner(start, end=None):

    if end is not None:
        tourn_df = get_espn_tournaments(start, end)
    else:
        tourn_df = get_espn_tournaments(start)

    hpd_path = Path(path_config.DATA_PROCESSED, "hpd_2018.csv")
    hpd_df = pd.read_csv(hpd_path, parse_dates=["date"])
    tournament_ids = tourn_df.tournament_id.unique()
    f_mapper = FantasyMapper(hpd_df, tournament_ids)

    f_mapper.run_all_transformations()
    print(f_mapper.df.shape)

def main():
    
    mapper_runner(2018)

if __name__ == "__main__":
    main()
