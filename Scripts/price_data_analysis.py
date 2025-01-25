import pandas as pd
import os

import matplotlib.pyplot as plt

# Directory containing the CSV files
data_dir = '../Raw Data/ind_sales_data/'

# List to hold dataframes
df_list = []

# Iterate over all files in the directory
for file in os.listdir(data_dir):
    if file.endswith('.csv'):
        file_path = os.path.join(data_dir, file)
        df = pd.read_csv(file_path)
        df_list.append(df)

# Create an empty dataframe to hold the final prices
all_data_df = pd.DataFrame()
cnt = 0
# Iterate over the list of dataframes and add the final price column to the all_data_df
for i, df in enumerate(df_list):
    # Ensure the DateTime column is in datetime format
    df['DateTime'] = pd.to_datetime(df['DateTime'])
    # Sort the dataframe by the DateTime column
    df.sort_values(by='DateTime', inplace=True)
    # Forward fill to keep the most recent value for empty cells
    df.ffill(inplace=True)
    # Add the final price column to the all_data_df with a unique name
    all_data_df[f'final_price_{cnt}'] = df.iloc[:, 1]
    cnt += 1
    
all_data_df['mean_final_price'] = all_data_df.mean(axis=1)

# Load the sales data
# Plot the mean final price
plt.figure(figsize=(10, 6))
plt.plot(all_data_df.index, all_data_df['mean_final_price'], label='Mean Final Price')
plt.xlabel('Index')
plt.ylabel('Mean Final Price')
plt.title('Mean Final Price Over Time')
plt.legend()
plt.show()
print(all_data_df.tail(100))
