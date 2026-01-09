-- 1. Sanity Check: View the joined data
SELECT 
    d.Full_Date, 
    s.Ticker_Symbol, 
    f.Close_Price, 
    f.Volume 
FROM Fact_Stock_Prices f
JOIN Dim_Stock_Info s ON f.Stock_ID = s.Stock_ID
JOIN Dim_Date d ON f.Date_ID = d.Date_ID
ORDER BY d.Full_Date DESC, s.Ticker_Symbol
LIMIT 15;

-- 2. Volatility Analysis: Which stock swings the most?
SELECT 
    s.Ticker_Symbol,
    ROUND(AVG(f.High_Price - f.Low_Price), 2) AS Avg_Daily_Swing,
    ROUND(AVG(f.Close_Price), 2) AS Avg_Closing_Price
FROM Fact_Stock_Prices f
JOIN Dim_Stock_Info s ON f.Stock_ID = s.Stock_ID
GROUP BY s.Ticker_Symbol
ORDER BY Avg_Daily_Swing DESC;