import os
import pandas as pd

def calculate_daily_average(df):

    df['DateTime'] = pd.to_datetime(df['DateTime'])

    df = df.sort_values(by='DateTime')
    
    df = df[(df['Final price'] != 0) | 
            ((df['Final price'] == 0) & 
             (~((df['DateTime'].diff().abs() < pd.Timedelta(hours=12)) | 
                (df['DateTime'].diff(-1).abs() < pd.Timedelta(hours=12)))))]
    
    df_avg = df.groupby(df['DateTime'].dt.date)['Final price'].mean().reset_index()
    df_avg.columns = ['DateTime', 'AvgDailyPrice']

    return df_avg

def avg(file_path):
   
    df = pd.read_csv(file_path)
    filename = os.path.basename(file_path)

    if 'DateTime' in df.columns and 'Final price' in df.columns:

        df_avg = calculate_daily_average(df)
        
        new_filename = f"{filename}_davg.csv"
        directory = os.path.dirname(file_path)
        new_file_path = os.path.join(directory, new_filename)
        
        df_avg.to_csv(new_file_path, index=False)

        print(f"calc avg daily price for {new_filename}")
    else:
        print(f"File {filename} aint it")