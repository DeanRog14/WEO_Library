import requests
import pandas as pd
import os
import numpy as np
from .errors import WEO_ParsingError

class WEODataFrame(pd.DataFrame):
    @property
    def _constructor(self):
        return WEODataFrame

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.id_column = "ISO"

    def convert(x):
        if isinstance(x, str) and "," in x:
            x = x.replace(",", "")
        try:
            return float(x)
        except ValueError:
            return np.nan

    def accept_year(func):
        def inner(self, *arg, year=None, start_year=None, end_year=None):
            df = func(self)
            if arg:
                year = arg[0]
            elif start_year and end_year:
                year = [start_year + y for y in range(end_year - start_year + 1)]
            if year:
                if isinstance(year, list):
                    year = [str(y) for y in year]
                else:
                    year = str(year)
    
                ts = df.transpose()[year]
                return ts.apply(pd.to_numeric, errors="coerce").astype(float)
            else:
                return df
        return inner

    @property
    def years(self):
        return [col for col in self.columns if str(col).isdigit()]

    @property
    def daterange(self):
        return pd.period_range(start=self.years[0], end=self.years[-1], freq="Y")

    def variables(self):
        mapping_df = self[['WEO Subject Code', 'Units', 'Subject Descriptor']].drop_duplicates()
        mapping_dict = mapping_df.set_index('WEO Subject Code')[['Units', 'Subject Descriptor']].to_dict(orient='index')

        for code, info in mapping_dict.items():
            desc = info['Subject Descriptor']
            unit = info['Units']
            print(f"('{code}', '{desc}', '{unit}')")

    def units(self, subject=None):
        ix = self["Subject Descriptor"] == subject
        return (self[ix] if subject else self)["Units"].unique().tolist()

    def codes(self):
        print(self['WEO Subject Code'].unique())

    def from_code(self, code):
        row = self[self['WEO Subject Code'] == code].drop_duplicates(subset=['WEO Subject Code'])

        desc = row.iloc[0]['Subject Descriptor']
        unit = row.iloc[0]['Units']
        return desc, unit

    def countries(self, name=None):
        if name:
            country_name = name.lower()
            selection = self["Country"].str.lower().str.contains(country_name)
            result = self.loc[selection, ["WEO Country Code", "ISO", "Country"]].drop_duplicates()
            return result
        else:
            return self[["WEO Country Code", "ISO", "Country"]].drop_duplicates()

    def iso_code3(self, name):
        return self.countries(name).ISO.iloc[0]

    def get(self, subject, unit):
        ix = (self["Subject Descriptor"] == subject) & (self["Units"] == unit)
        df = self[ix]
    
        df_selected = df[self.years + [self.id_column]].drop_duplicates(subset=[self.id_column])
        df_selected = df_selected.set_index(self.id_column)
        df_transposed = df_selected.transpose()
        df_transposed.columns.name = ""
        df_transposed.index = self.daterange
    
        return df_transposed

    # def _extract(self, ix, column):
    #     _df = (
    #         self.df[ix][self.years + [column]]
    #         .set_index(column)
    #         .transpose()
    #         .map(convert)
    #     )
    #     _df.columns.name = ""
    #     _df.index = self.daterange
    #     return _df

    # def fix_year(self, year):
    #     return (
    #         self.df[["ISO", "WEO Subject Code", str(year)]]
    #         .pivot(index="WEO Subject Code", columns="ISO", values=str(year))
    #         .map(convert)
    #     )
        
    def country(self, iso_code, year=None, compact=True):
        if len(iso_code) == 3:
            ix = self['ISO'] == iso_code
        else:
            raise WEO_ParsingError(iso_code)
        _df = self._extract(ix, "WEO Subject Code")
        if compact:
            _df = _df[self.core_codes]
        if year is None:
            return _df
        else:
            _df = _df.transpose()[str(year)]
            _df["Description"] = _df.index.map(lambda c: " - ".join(self.from_code(c)))
            return _df

    @accept_year
    def gdp_nc(self):
        return self.get("Gross domestic product, current prices", "National currency")

    @accept_year
    def gdp_id(self):
        return self.get("Gross domestic product, current prices", "Purchasing power parity; international dollars")

    @accept_year
    def gdp_usd(self):
        return self.get("Gross domestic product, current prices", "U.S. dollars")

    def nlargest(self, n=10, year=2018):
        return self.gdp_usd(year).sort_values(ascending=False).head(n).index.tolist()

    def exchange_rate(self, year=None):
        return self.gdp_nc(year) / self.gdp_usd(year)

    @accept_year
    def population(self):
        return self.get("Population", "Persons")

    @accept_year
    def gdp_pc_nc(self):
        return self.get(
            "Gross domestic product per capita, current prices", "National currency"
        )

    @accept_year
    def gdp_pc_usd(self):
        return self.get(
            "Gross domestic product per capita, current prices", "U.S. dollars"
        )

    @accept_year
    def gdp_ppp(self):
        return self.get(
            "Gross domestic product, current prices",
            "Purchasing power parity; international dollars",
        )

    @accept_year
    def gdp_growth(self):
        return self.get("Gross domestic product, constant prices", "Percent change")

    @accept_year
    def current_account(self):
        return self.get("Current account balance", "U.S. dollars")

    @accept_year
    def inflation(self):
        return self.get("Inflation, end of period consumer prices", "Percent change")

    @accept_year
    def gov_net_lending_pgdp(self):
        return self.get("General government net lending/borrowing", "Percent of GDP")

    @accept_year
    def gov_gross_debt_pgdp(self):
        return self.get("General government gross debt", "Percent of GDP")

    def libor_usd(self):
        return self.get(
            "Six-month London interbank" " offered rate (LIBOR)", "Percent"
        )["USA"]
