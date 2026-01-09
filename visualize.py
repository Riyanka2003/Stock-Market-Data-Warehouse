import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt

# --- CONFIGURATION ---
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root', 
    'password': '@Finance_955',  # <--- Update this!
    'database': 'Stock_Market_DW'
}

def plot_prices(ticker):
    conn = mysql.connector.connect(**DB_CONFIG)
    
    # SQL Query to get dates and closing prices for one stock
    query = """
    SELECT d.Full_Date, f.Close_Price 
    FROM Fact_Stock_Prices f
    JOIN Dim_Stock_Info s ON f.Stock_ID = s.Stock_ID
    JOIN Dim_Date d ON f.Date_ID = d.Date_ID
    WHERE s.Ticker_Symbol = %s
    ORDER BY d.Full_Date ASC
    """
    
    # Load into Pandas DataFrame
    df = pd.read_sql(query, conn, params=(ticker,))
    conn.close()
    
    # Create the Plot
    plt.figure(figsize=(12, 6))
    plt.plot(df['Full_Date'], df['Close_Price'], label=f'{ticker} Close Price', color='blue')
    plt.title(f'Stock Price Trend: {ticker} (Source: My Data Warehouse)', fontsize=16)
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Price (USD)', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend()
    
    # Save the chart as an image
    filename = f"{ticker}_price_chart.png"
    plt.savefig(filename)
    print(f"Chart saved as {filename}")
    plt.show()

if __name__ == "__main__":
    plot_prices('AAPL') # Change to 'MSFT' or 'GOOGL' to see others