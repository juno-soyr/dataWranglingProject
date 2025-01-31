import pandas as pd
import matplotlib.pyplot as plt
from calc_price_data import avg, fill_daily_prices
import os
import re

users_path = '../Raw Data/concurrent_steam_users.csv'
sales_path = '../Raw Data/steam_sales_dates.csv'
ind_sales_path = '../Raw Data/ind_sales_data/'
start_date = '2020-01-01'
end_date = '2024-12-31'

def make_global_price_data(ind_sales_dir, start_date, end_date):

    pattern = re.compile(r'^\d+[A-Za-z]\.csv$')
    global_data = pd.DataFrame()

    for filename in os.listdir(ind_sales_dir):

        if pattern.match(filename):

            file_path = os.path.join(ind_sales_dir, filename)
            avg(file_path)
            avg_data = pd.read_csv(file_path + '_davg.csv')

            avg_data['DateTime'] = pd.to_datetime(avg_data['DateTime'])
            avg_data = avg_data[avg_data['DateTime'] >= start_date]
            avg_data = avg_data[avg_data['DateTime'] <= end_date]

            avg_data = fill_daily_prices(avg_data, 'DateTime', 'AvgDailyPrice')

            global_data = pd.concat([global_data, avg_data['AvgDailyPrice']], axis=1)

    global_data['mean'] = global_data.mean(axis=1)
    global_data['Date'] = avg_data['DateTime']
    return global_data

def process_users_data(users_path, start_date, end_date):

    users_data = pd.read_csv(users_path)
    users_data['DateTime'] = pd.to_datetime(users_data['DateTime'])

    filtered_users_data = users_data[
        (users_data['DateTime'] >= start_date) & 
        (users_data['DateTime'] <= end_date) 
    ]

    filtered_users_data = filtered_users_data.copy()
    filtered_users_data['Date'] = filtered_users_data['DateTime'].dt.date

    daily_aggregation = (
        filtered_users_data
        .groupby('Date')['In-Game']
        .agg(['mean', 'max', 'min']) 
        .reset_index()
    )
    daily_aggregation['Date'] = pd.to_datetime(daily_aggregation['Date'])
    return daily_aggregation

def mark_sale_periods(data, sales_period, date_column='DateTime', pre_sale_days=7, post_sale_days=7):

    sale_status = ['Pre-Sale', 'During Sale', 'Post-Sale', 'No Sale']
    
    data['SalePeriod'] = 'No Sale'
    
    for _, row in sales_period.iterrows():
        start_date = row['Start Date']
        end_date = row['End Date']

        data.loc[
            (data[date_column] >= start_date - pd.Timedelta(days=pre_sale_days)) &
            (data[date_column] < start_date),
            'SalePeriod'
        ] = 'Pre-Sale'

        data.loc[
            (data[date_column] >= start_date) &
            (data[date_column] <= end_date),
            'SalePeriod'
        ] = 'During Sale'

        data.loc[
            (data[date_column] > end_date) &
            (data[date_column] <= end_date + pd.Timedelta(days=post_sale_days)),
            'SalePeriod'
        ] = 'Post-Sale'
    
    data['SalePeriod'] = pd.Categorical(data['SalePeriod'], categories=sale_status, ordered=True)
    
    return data

sales_period = pd.read_csv(sales_path)
sales_period['Start Date'] = pd.to_datetime(sales_period['Start Date']).dt.date
sales_period['End Date'] = pd.to_datetime(sales_period['End Date']).dt.date


user_data_f = process_users_data(users_path, start_date, end_date)
global_price_data = make_global_price_data(ind_sales_path, start_date, end_date)

global_price_data['Date'] = pd.to_datetime(global_price_data['Date']).dt.date
user_data_f['Date'] = pd.to_datetime(user_data_f['Date']).dt.date

global_price_data = mark_sale_periods(global_price_data, sales_period, date_column='Date')
user_data_f = mark_sale_periods(user_data_f, sales_period, date_column='Date')

plt.figure(figsize=(10, 5))
plt.plot(global_price_data['Date'], global_price_data['mean'], linewidth=2, color = 'blue')
#plt.plot(user_data_f['Date'], user_data_f['max'], linewidth=2, color = 'green')

for index, row in sales_period.iterrows():
    if row['Start Date'] >= pd.Timestamp(start_date).date():
        plt.axvspan(row['Start Date'], row['End Date'], color='red', alpha=0.2)

plt.xlabel('Date', fontsize=14)
plt.ylabel('Price', fontsize=14)
plt.grid(alpha=0.2)
plt.tight_layout()
plt.show()
