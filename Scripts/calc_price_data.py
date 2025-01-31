import os
import pandas as pd

def fill_daily_prices(df, date_col, value_col):
 
    df[date_col] = pd.to_datetime(df[date_col])
    full_date_range = pd.date_range(start=df[date_col].min(), end=df[date_col].max())
    df = df.set_index(date_col).reindex(full_date_range, method='ffill')
    df.reset_index(inplace=True)

    df.columns = [date_col, value_col]
    
    return df

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
    else:
        print(f"File {filename} aint it")