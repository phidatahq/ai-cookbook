import pandas as pd
import matplotlib.pyplot as plt

# Function to load data
def load_data(file_path):
    return pd.read_csv(file_path)

# Function to prepare data
def prepare_data(df):
    return df.groupby('Year')['Revenue_Millions'].sum().reset_index()

# Function to plot data
def plot_revenue_over_time(df):
    df.plot(x='Year', y='Revenue_Millions', kind='line')
    plt.title('Total Movie Revenue Over Time')
    plt.xlabel('Year')
    plt.ylabel('Total Revenue (Millions of Dollars)')
    plt.show()

if __name__ == "__main__":
    path = '/Users/zu/workspaces/ai-cookbook/data/csv/IMDB-Movie-Data.csv'
    data = load_data(path)
    prepared_data = prepare_data(data)
    plot_revenue_over_time(prepared_data)