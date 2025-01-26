import pandas as pd
import matplotlib.pyplot as plt
from calc_price_data import avg, fill_daily_prices
import os
import re

users_path = 'Raw Data/concurrent_steam_users.csv'
sales_path = 'Raw Data/steam_sales_dates.csv'

users_data = pd.read_csv(users_path)
sales_data = pd.read_csv(sales_path)

users_data['DateTime'] = pd.to_datetime(users_data['DateTime'])
sales_data['Start Date'] = pd.to_datetime(sales_data['Start Date'], format='%m/%d/%Y')
sales_data['End Date'] = pd.to_datetime(sales_data['End Date'], format='%m/%d/%Y')

start_date = '2020-01-01'


filtered_users_data = users_data[
    (users_data['DateTime'] >= start_date) & 
    (users_data['DateTime'] <= '2025-01-20') 
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
pattern = re.compile(r'^\d+[A-Za-z]\.csv$')
global_data = pd.DataFrame()
for filename in os.listdir('Raw Data/ind_sales_data/'):
    if pattern.match(filename):
        avg('Raw Data/ind_sales_data/' + filename)
        avg_data = pd.read_csv('Raw Data/ind_sales_data/' + filename + '_davg.csv')
        avg_data = avg_data[avg_data['DateTime'] >= start_date]
        avg_data['DateTime'] = pd.to_datetime(avg_data['DateTime'])
        avg_data = fill_daily_prices(avg_data, 'DateTime', 'AvgDailyPrice')
        global_data = pd.concat([global_data, avg_data['AvgDailyPrice']], axis=1)

global_data['mean'] = global_data.mean(axis=1)
global_data['DateTime'] = avg_data['DateTime']


plt.figure(figsize=(20, 10))
plt.plot(global_data['DateTime'], global_data['mean'], linewidth=2, color = 'blue')
#plt.plot(daily_aggregation['Date'], daily_aggregation['max'], linewidth=2, color = 'green')

for index, row in sales_data.iterrows():
    if row['Start Date'] >= pd.Timestamp(start_date):
        plt.axvspan(row['Start Date'], row['End Date'], color='red', alpha=0.2)

plt.xlabel('Date', fontsize=14)
plt.ylabel('Price', fontsize=14)
plt.grid(alpha=0.2)
plt.tight_layout()
plt.show()
