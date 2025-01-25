import os
import pandas as pd
import re

def rem_dup(directory):

    pattern = re.compile(r'^\d+[A-Za-z]\.csv$')

    for filename in os.listdir(directory):

        if pattern.match(filename):
            file_path = os.path.join(directory, filename)

            df = pd.read_csv(file_path)

            df_cleaned = df.drop_duplicates()

            df_cleaned.to_csv(file_path, index=False)


rem_dup('../Raw Data/ind_sales_data/')
