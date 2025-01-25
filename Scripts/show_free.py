import os
import re
import pandas as pd

def went_free(file_path):

    print(f"checking {file_path}")

    data = pd.read_csv(file_path)

    data['DateTime'] = pd.to_datetime(data['DateTime'])

    data = data.sort_values(by='DateTime', ascending=True)

    free_price_data = data[data['Final price'] == 0]

    if len(free_price_data) >= 2 and all(data['Final price'].iloc[-2:] == 0):
        last_two_dates = free_price_data['DateTime'].iloc[-2:]
        date_diff = (last_two_dates.iloc[1] - last_two_dates.iloc[0]).days
        if date_diff >= 7:
            return True
        
    return False

def print_free(directory):

    pattern = re.compile(r'(\d+)([a-zA-Z])\.csv')

    for filename in os.listdir(directory):

        match = pattern.match(filename)
        if match:

            number = match.group(1)
            letter = match.group(2)

            file_path = os.path.join(directory, filename)
            if went_free(file_path):
                print(f"Game {number}{letter} went free")


directory_path = "../Raw Data/ind_sales_data"

# gta5_path ="../Raw Data/ind_sales_data/gta5.csv"
# csgo_path = "../Raw Data/ind_sales_data/csgo.csv"
# pubg_path = "../Raw Data/ind_sales_data/pubg.csv"

# print(went_free(gta5_path))
# print(went_free(csgo_path))
# print(went_free(pubg_path))

print_free(directory_path)
