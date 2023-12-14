import pandas as pd
import matplotlib.pyplot as plt

def read_data(filepath):
    return pd.read_csv(filepath)

def plot_revenue_over_time(data):
    # Group by Year and sum the revenues
    revenue_by_year = data.groupby('Year')['Revenue_Millions'].sum().reset_index()
    # Plot
    plt.figure(figsize=(10,6))
    plt.plot(revenue_by_year['Year'], revenue_by_year['Revenue_Millions'], marker='o')
    plt.title('Total Movie Revenue Over Time')
    plt.xlabel('Year')
    plt.ylabel('Revenue in Millions')
    plt.grid(True)
    plt.show()

if __name__ == "__main__":
    filepath = '/Users/zu/workspaces/ai-cookbook/data/csv/IMDB-Movie-Data.csv'
    data = read_data(filepath)
    plot_revenue_over_time(data)