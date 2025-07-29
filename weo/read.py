import pandas as pd
import os
from .dataframe import WEODataFrame

def reads_csv(file_name):
    # Splits the name of the file to allow for different encodings
    base_name = os.path.splitext(file_name)[0]
    name_list = base_name.split("_")
    prefix, year, month = name_list

    # Selecting a different encoding based on what year the dataset is from
    if(int(year) > 2020):
        df = pd.read_csv(file_name, delimiter="\t", encoding="utf-16-le")
    else:
        df = pd.read_csv(file_name, delimiter="\t", encoding="iso-8859-1")

    # Drops the row if the country is na or NaN
    df = df.dropna(subset=["Country"])
    
    return WEODataFrame(df.copy(deep=True))