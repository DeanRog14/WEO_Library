import pandas as pd

def transform(df, id_vars=['Country', 'Subject Descriptor'], value_name='Value'):

    # Melt the dataframe
    df_melted = df.melt(
        id_vars=id_vars,
        var_name='date',
        value_name=value_name
    )
    df_melted['date'] = pd.to_numeric(df_melted['date'], errors='coerce')

    df_melted = df_melted[~df_melted[value_name].isin(['--', ''])]

    df_melted[value_name] = pd.to_numeric(df_melted[value_name], errors='coerce')

    df_melted.dropna(subset=['date', value_name], inplace=True)

    df_melted['date'] = pd.to_datetime(df_melted['date'], format='%Y')

    return df_melted

# Adds a column that has the quarter and year combined
def data_prep(df, value, values):
    # Ensures the values are correct and smaller forms for better runtimes
    df = df.copy()
    subset = df[df[value] == values].copy()

    return subset

# Splits apart the indexes and puts them into a dictionary, good for a column with many different indexes
def prep_dfs(df, value, index_list):
    prepared_dfs = {}

    for index in index_list:
        prepared_dfs[index] = data_prep(df, value, index)

    return prepared_dfs