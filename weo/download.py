import requests
import pandas as pd
import os

def download(year, release, file_type):
    # Only selects datasets from after the 2007 period
    if (year > 2007 and year < 2026):
        # The 2011 year is not Apr, Oct so we need specific parameters
        if (year == 2011) and release in ('April', 'September'):
            # Need the short term of the month
            if (release == 'April'):
                month_short = 'Apr'
            elif (release == 'September'):
                month_short = 'Sep'
            else:
                print("Sorry that month is not in the 2011, WEO dataset")

            # Gets the dataset based on the month from the 2011 year
            ashx_url = f'https://www.imf.org/-/media/Files/Publications/WEO/WEO-Database/{year}/WEO{month_short}{year}all.ashx'

        short_apr = 'Apr'
        short_oct = 'Oct'
        lower_apr = 'april'
        
        if (year > 2023):
            if (year == 2025 and release == "April"):
                ashx_url = f'https://www.imf.org/-/media/Files/Publications/WEO/WEO-Database/{year}/{lower_apr}/WEO{short_apr}{year}all.ashx'
            if (year == 2024):
                if (release == 'April'):
                    ashx_url = f'https://www.imf.org/-/media/Files/Publications/WEO/WEO-Database/{year}/{release}/WEO{short_apr}{year}all.ashx'
                elif (release == 'October'):
                    ashx_url = f'https://www.imf.org/-/media/Files/Publications/WEO/WEO-Database/{year}/{release}/WEO{short_oct}{year}all.ashx'
                else:
                    print("That month is not in the WEO dataset")

        elif (year != 2011):
            if (release == 'April'):
                ashx_url = f'https://www.imf.org/-/media/Files/Publications/WEO/WEO-Database/{year}/WEO{short_apr}{year}all.ashx'
            elif (release == 'October'):
                ashx_url = f'https://www.imf.org/-/media/Files/Publications/WEO/WEO-Database/{year}/WEO{short_oct}{year}all.ashx'
            else:
                print("That month is not in the WEO dataset")


        # Queries to the WEO database based on the given url
        response = requests.get(ashx_url)
        # Ensures that the url given allows for proper loading
        if response.status_code == 200:
            if (file_type == 'csv'):
                file_content = response.content
                # Creates the csv file with the dataset
                dataset_name = f'WEO_{year}_{release}.csv'
                with open(dataset_name, 'wb') as f:
                    f.write(file_content)
            else:
                file_content = response.content
                # Creates the csv file with the dataset
                dataset_name = f'WEO_{year}_{release}.xls'
                with open(dataset_name, 'wb') as f:
                    f.write(file_content)

            print("File downloaded successfully!")
            print(dataset_name)
        else:
            print(f"Error downloading file. Status code: {response.status_code}")
    else:
        print("Sorry your year is out of range for this library")