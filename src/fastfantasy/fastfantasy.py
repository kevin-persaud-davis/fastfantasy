from historical_data import DataRunner, merge_tournaments
from draftkings_mappings import FantasyMapper, mapper_runner


def raw_data(start_season, end_season=None, save_data=False):

    if save_data:
        if end_season is not None:

            data_fn = f"hpd_{start_season}_{end_season}.csv"
        else:
            data_fn = f"hpd_{start_season}.csv"

        merge_tournaments("*.csv", data_fn)
    
    else:
        data_fn = "hpd.csv"
        raw_df = merge_tournaments("*.csv", data_fn, save=False)
        
        return raw_df

class DataAccess():

    def __init__(self, start, end=None, data="raw") -> None:
        if end is not None:
            self.end = end
        else:
            self.end = None

        self.start = start
        self.data = data

def main():
    
    df = raw_data(2018)
    print(df.head())


if __name__ == "__main__":
    main()