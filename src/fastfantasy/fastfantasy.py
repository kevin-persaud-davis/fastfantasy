from historical_data import parallel_historical_runner, parallel_tournament_data
from historical_data import clean_up_runner, merge_tournaments
from draftkings_mappings import mapper_runner
from tournament import EspnSeason, CleanTournaments


class DataAccess():

    def __init__(self, start, end=None) -> None:
        if end is not None:
            self.end = end
        else:
            self.end = None

        self.start = start

    def raw(self, save=False):
        """Get raw historical data.


        Parameters
        ----------
        save : bool, optional 
            If False, return raw data. Otherwise save 
            data to disk.

        Examples
        --------
        >>> historical_data = DataAccess(2018)
        >>> raw_df = historical_data.raw()
        """
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
        """Get full historical data.

        Data includes raw + fantasy point mappings.

        Examples
        --------
        >>> historical_data = DataAccess(2018)
        >>> full_df = historical_data.full()
        >>> full_df.head()
        """

        if self.end is not None:
            f_df = mapper_runner(self.start, self.end)
        else:
            f_df = mapper_runner(self.start)
        
        return f_df

    def fantasy(self):
        """Get fantasy historical data.

        Data only includes fantasy point mappings.

        Examples
        --------
        >>> historical_data = DataAccess(2018)
        >>> fantasy_df = historical_data.fantasy()
        >>> fantasy_df.head()
        """
        df = self.full()
        id_df = df.iloc[:, :3].copy()
        dk_df = df.iloc[:, 150:].copy()

        df = id_df.join(dk_df, how="outer")
        return df

    def new_collection_process(self, start, end=None, data="full"):
        """Run full data collection process for historical data.

        data options include {"full", "raw", "fantasy"}.

        Parameters
        ----------
        start : int
            Start season.

        end : int, optional
            End season.

        data : str,
            Historical data type.

        Examples
        --------
        >>> historical_data = DataAccess(2018)
        >>> df = historical_data.new_collection_process(2016, 2018, "full")
        >>> df.head()
        """
        if end is not None:
            self.end = end
        else:
            self.end = None
        self.start = start

        e_season = EspnSeason(self.start, self.end)
    
        e_season.retrieve_all_seasons()

        tourn_df = e_season.feed_season_data()

        if e_season.end is not None:
            clean_end = e_season.end
            clean_fn = f"valid_tournaments_{e_season.start}_{clean_end}.csv"
        else:
            clean_fn = f"valid_tournaments_{e_season.start}.csv"

        clean_tourn = CleanTournaments(tourn_df)
        clean_tourn.save_cleaned_tournaments(clean_fn)

        parallel_historical_runner(self.start, self.end)
        # add clean up runner 
        clean_up_runner()

        if data == "raw":
            return self.raw(save=False)
        elif data == "full":
            return self.full()
        elif data == "fantasy":
            return self.fantasy()
        else:
            print(f"Please enter one of three data access options.\n")

def main():
    
    # option 1. Raw ESPN scorecard data
    historical_data = DataAccess(2018)
    raw_df = historical_data.raw()

    # option 2. Raw ESPN scorecard data + DraftKings mappings
    full_df = historical_data.full()

    # option 3. Draftkings mappings
    fantasy_df = historical_data.fantasy()
    


if __name__ == "__main__":
    main()