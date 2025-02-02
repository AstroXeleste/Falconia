import numpy as np
import pandas as pd

def combine_datasets(list_of_dataframes) -> pd.DataFrame:
    df = pd.DataFrame({'Reading'})
    for dataframe in list_of_dataframes:
        pd.merge(df, dataframe)
    return df