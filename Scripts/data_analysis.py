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

            avg_data = fill_daily_prices(avg_data, 'DateTime', 'AvgDailyPrice', start_date, end_date)

            if avg_data.isna().sum().sum() > 0:
                print(f"NaNs detected in file: {filename}")
                print(avg_data.isna().sum())
                print(avg_data[avg_data.isna().any(axis=1)])

            global_data = pd.concat([global_data, avg_data['AvgDailyPrice']], axis=1)

    global_data['mean'] = global_data.mean(axis=1,skipna=True)
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

def mark_sale_periods(data, sales_period, pre_sale_days, post_sale_days, date_column):

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

def compare_sale_periods(data, value_column):

    comparison = data.groupby('SalePeriod',observed=True)[value_column].agg(['mean', 'std', 'count'])
    comparison['percentage_change'] = comparison['mean'].pct_change() * 100
    return comparison

def plot_price_trends(global_price_data, sales_period):
    plt.figure(figsize=(12, 6))
    plt.plot(global_price_data['Date'], global_price_data['mean'], linewidth=2, color='blue', label='Avg Price')
    
    for _, row in sales_period.iterrows():
        if row['Start Date'] >= global_price_data['Date'].min():
            plt.axvspan(row['Start Date'], row['End Date'], color='red', alpha=0.2)
    
    plt.xlabel('Date', fontsize=14)
    plt.ylabel('Average Price', fontsize=14)
    plt.title('Global Price Trends Over Time', fontsize=16)
    plt.legend()
    plt.grid(alpha=0.2)
    plt.tight_layout()
    plt.show()

def plot_comparison_bar(data, title, ylabel, ylim):
    plt.figure(figsize=(8, 5))
    plt.bar(data.index, data['mean'], color=['blue', 'orange', 'green', 'red'])
    plt.xlabel('Sale Period', fontsize=12)
    plt.ylabel(ylabel, fontsize=12)
    plt.title(title, fontsize=14)
    plt.ylim(ylim)
    plt.grid(axis='y', linestyle='--', alpha=0.6)
    plt.show()

sales_period = pd.read_csv(sales_path)
sales_period['Start Date'] = pd.to_datetime(sales_period['Start Date']).dt.date
sales_period['End Date'] = pd.to_datetime(sales_period['End Date']).dt.date

user_data_f = process_users_data(users_path, start_date, end_date)
global_price_data = make_global_price_data(ind_sales_path, start_date, end_date)

global_price_data['Date'] = pd.to_datetime(global_price_data['Date']).dt.date
user_data_f['Date'] = pd.to_datetime(user_data_f['Date']).dt.date

pre_sale_interval = post_sale_interval= 7

global_price_data = mark_sale_periods(global_price_data, sales_period, pre_sale_interval, post_sale_interval, 'Date')
user_data_f = mark_sale_periods(user_data_f, sales_period, pre_sale_interval, post_sale_interval, 'Date')

global_price_comparison = compare_sale_periods(global_price_data, 'mean')
user_count_comparison = compare_sale_periods(user_data_f, 'mean')


plot_price_trends(global_price_data, sales_period)
plot_comparison_bar(global_price_comparison, 'Average Price During Sale Periods', 'Avg Price', 0)
plot_comparison_bar(user_count_comparison, 'Average Player Count During Sale Periods', 'Avg Concurrent Players', 7000000)


rolling_corr = global_price_data['mean'].rolling(30).corr(user_data_f['mean'])

rolling_corr.dropna(inplace=True)

valid_dates = global_price_data['Date'][rolling_corr.index]


plt.figure(figsize=(10, 5))
plt.plot(valid_dates, rolling_corr, color='purple', label="30-Day Rolling Correlation")
for _, row in sales_period.iterrows():
    if row['Start Date'] >= global_price_data['Date'].min() and row['Start Date'] <= global_price_data['Date'].max():
        plt.axvspan(row['Start Date'], row['End Date'], color='red', alpha=0.2)
plt.axhline(y=0, color='gray', linestyle='--')
plt.title("Rolling Correlation: Price vs. Player Count")
plt.xlabel("Date")
plt.ylabel("Correlation")
plt.legend()
plt.grid()
plt.show()

def compute_correlation_by_sale_period(global_price_data, user_data_f):
    sale_periods = ['Pre-Sale', 'During Sale', 'Post-Sale', 'No Sale']
    sale_period_correlations = {}

    for period in sale_periods:
        subset_prices = global_price_data[global_price_data['SalePeriod'] == period]
        subset_users = user_data_f[user_data_f['SalePeriod'] == period]
        
        correlation = subset_prices['mean'].corr(subset_users['mean'])
        
        sale_period_correlations[period] = correlation
    
    return sale_period_correlations

def plot_correlation_by_sale_period(sale_period_correlations):
    filtered_correlations = {k: v for k, v in sale_period_correlations.items() if v is not None}
    
    plt.figure(figsize=(8, 5))
    plt.bar(filtered_correlations.keys(), filtered_correlations.values(), color=['blue', 'orange', 'green', 'red'])
    plt.xlabel("Sale Period", fontsize=12)
    plt.ylabel("Correlation", fontsize=12)
    plt.title("Correlation Between Price and Player Count by Sale Period", fontsize=14)
    plt.axhline(y=0, color='gray', linestyle='--')
    plt.grid(axis='y', linestyle='--', alpha=0.6)
    plt.show()

sale_period_correlations = compute_correlation_by_sale_period(global_price_data, user_data_f)
plot_correlation_by_sale_period(sale_period_correlations)



