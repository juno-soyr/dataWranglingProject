import os
import pandas as pd
import re

def calculate_daily_average(df):

    df['DateTime'] = pd.to_datetime(df['DateTime'])

    df_avg = df.groupby(df['DateTime'].dt.date)['Final price'].mean().reset_index()
    df_avg.columns = ['DateTime', 'AvgDailyPrice']

    return df_avg

def avg(file_path):
   
    df = pd.read_csv(file_path)

    if 'DateTime' in df_cleaned.columns and 'Final price' in df_cleaned.columns:

        df_avg = calculate_daily_average(df_cleaned)
        
        new_filename = f"{os.path.splitext(filename)[0]}_davg.csv"
        new_file_path = os.path.join(directory, new_filename)
        
        df_avg.to_csv(new_file_path, index=False)

        print(f"calc avg daily price for {new_filename}")
    else:
        print(f"File {filename} aint it")

avg('../Raw Data/ind_sales_data/gta5.csv')