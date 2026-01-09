import mysql.connector
import yfinance as yf
import pandas as pd
from datetime import datetime

# --- CONFIGURATION ---
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root', 
    'password': '@Finance_955',  # <--- UPDATE THIS
    'database': 'Stock_Market_DW'
}

# List of stocks to track (The "Magnificent 7" Tech Stocks)
TICKERS = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'TSLA', 'META']

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

def populate_dimensions():
    """Step 1: Ensure Dim_Stock_Info has our companies."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    print("--- Updating Dimension Tables ---")
    for ticker in TICKERS:
        # Fetch company info from Yahoo
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # SQL to insert if not exists
        sql = """
        INSERT INTO Dim_Stock_Info (Ticker_Symbol, Company_Name, Sector, Industry, Exchange)
        SELECT %s, %s, %s, %s, %s
        WHERE NOT EXISTS (SELECT * FROM Dim_Stock_Info WHERE Ticker_Symbol = %s);
        """
        val = (ticker, info.get('longName', 'N/A'), info.get('sector', 'N/A'), 
               info.get('industry', 'N/A'), info.get('exchange', 'N/A'), ticker)
        
        cursor.execute(sql, val)
    
    conn.commit()
    print("Dimensions updated successfully.")
    cursor.close()
    conn.close()

def load_stock_data():
    """Step 2: Fetch prices and load into Fact_Stock_Prices."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    print("\n--- Fetching & Loading Market Data ---")
    
    # Download data for the last 1 year
    start_date = "2023-01-01"
    end_date = datetime.today().strftime('%Y-%m-%d')
    
    for ticker in TICKERS:
        print(f"Processing {ticker}...")
        
        # 1. Get Stock_ID from our Dimension table
        cursor.execute("SELECT Stock_ID FROM Dim_Stock_Info WHERE Ticker_Symbol = %s", (ticker,))
        result = cursor.fetchone()
        if not result:
            print(f"Skipping {ticker} (ID not found)")
            continue
        stock_id = result[0]
        
        # 2. Download Data
        df = yf.download(ticker, start=start_date, end=end_date, progress=False)
        
        # --- FIX STARTS HERE ---
        # Fix for new yfinance format: Flatten MultiIndex columns if they exist
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
            
        # Iterate directly over the Index (Date) instead of resetting it
        for date_obj, row in df.iterrows():
            # date_obj is now the Index (Timestamp), so we can use it directly
            date_id = int(date_obj.strftime('%Y%m%d')) # Create ID like 20230101
            
            # 3. Ensure Date exists in Dim_Date (Simple check)
            check_date = "INSERT IGNORE INTO Dim_Date (Date_ID, Full_Date, Year, Quarter, Month, Month_Name, Day_of_Week, Is_Weekend) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
            date_val = (
                date_id, date_obj.date(), date_obj.year, (date_obj.month-1)//3 + 1,
                date_obj.month, date_obj.strftime('%B'), date_obj.weekday(), 
                1 if date_obj.weekday() >= 5 else 0
            )
            cursor.execute(check_date, date_val)
            
            # 4. Insert Price Data
            # Note: We check if data exists to avoid duplicates
            sql_fact = """
            INSERT INTO Fact_Stock_Prices 
            (Stock_ID, Date_ID, Open_Price, High_Price, Low_Price, Close_Price, Volume) 
            SELECT %s, %s, %s, %s, %s, %s, %s
            WHERE NOT EXISTS (SELECT * FROM Fact_Stock_Prices WHERE Stock_ID = %s AND Date_ID = %s)
            """
            
            # Extract row data safely
            val_fact = (
                stock_id, date_id, 
                float(row['Open']), float(row['High']), float(row['Low']), float(row['Close']), int(row['Volume']),
                stock_id, date_id
            )
            cursor.execute(sql_fact, val_fact)
            
        conn.commit()
    
    print("Data Load Complete!")
    cursor.close()
    conn.close()

if __name__ == "__main__":
    populate_dimensions()
    load_stock_data()