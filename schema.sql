-- 1. Create the Database (Run this line first, then double-click the DB in the sidebar to select it)
CREATE DATABASE Stock_Market_DW;
USE Stock_Market_DW;

-- 2. Create the Dimension Table for Stocks
CREATE TABLE Dim_Stock_Info (
    Stock_ID INT AUTO_INCREMENT PRIMARY KEY,  -- 'AUTO_INCREMENT' is the MySQL version of 'SERIAL'
    Ticker_Symbol VARCHAR(10) NOT NULL,
    Company_Name VARCHAR(100),
    Sector VARCHAR(50),
    Industry VARCHAR(50),
    Exchange VARCHAR(20)
);

-- 3. Create the Dimension Table for Dates
CREATE TABLE Dim_Date (
    Date_ID INT PRIMARY KEY,                  -- Manual ID like 20231025
    Full_Date DATE NOT NULL,
    Year INT,
    Quarter INT,
    Month INT,
    Month_Name VARCHAR(15),
    Day_of_Week INT,
    Is_Weekend BOOLEAN                        -- MySQL accepts BOOLEAN (saves as 0 or 1)
);

-- 4. Create the Fact Table for Prices
CREATE TABLE Fact_Stock_Prices (
    Price_ID INT AUTO_INCREMENT PRIMARY KEY,
    Stock_ID INT,
    Date_ID INT,
    Open_Price DECIMAL(10, 2),
    High_Price DECIMAL(10, 2),
    Low_Price DECIMAL(10, 2),
    Close_Price DECIMAL(10, 2),
    Volume BIGINT,
    
    -- Foreign Keys
    CONSTRAINT fk_stock FOREIGN KEY (Stock_ID) REFERENCES Dim_Stock_Info(Stock_ID),
    CONSTRAINT fk_date FOREIGN KEY (Date_ID) REFERENCES Dim_Date(Date_ID)
);
