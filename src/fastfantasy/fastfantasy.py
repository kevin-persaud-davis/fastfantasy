from historical_data import DataRunner, merge_tournaments
from draftkings_mappings import mapper_runner


def full_data(start_season, end_season=None):

    if end_season is not None:

        df = mapper_runner(start_season, end_season)
    else:
        df = mapper_runner(start_season)

    return df

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

    def __init__(self, start, end=None) -> None:
        if end is not None:
            self.end = end
        else:
            self.end = None

        self.start = start

    def raw(self, save=False):
        
        if save:
            if self.end is not None:

                data_fn = f"hpd_{self.start}_{self.end}.csv"
            else:
                data_fn = f"hpd_{self.start}.csv"

            merge_tournaments("*.csv", data_fn)
        
        else:
            data_fn = "hpd.csv"
            raw_df = merge_tournaments("*.csv", data_fn, save=False)
        
            return raw_df

    def full(self):

        if self.end is not None:
            f_df = mapper_runner(self.start, self.end)
        else:
            f_df = mapper_runner(self.start)
        
        return f_df

    def fantasy(self):

        df = self.full()
        id_df = df.iloc[:, :3].copy()
        dk_df = df.iloc[:, 150:].copy()

        df = id_df.join(dk_df, how="outer")
        return df

    def new_collection_process(start, end=None, data="full"):
        pass



def main():
    
    # option 1. Raw ESPN scorecard data
    df = raw_data(2018)

    # option 2. Raw ESPN scorecard data + DraftKings mappings
    fantasy_df = mapper_runner(2018)
    print(fantasy_df.head())

    print(df.shape, fantasy_df.shape)
    # option 3. Draftkings mappings
    
    


if __name__ == "__main__":
    main()