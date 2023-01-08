# Programming-Practice

This repository collects some programming applications of financial practices I worked on. 

All sensitive information has been obfuscated.


### 1. Strategy Backtest

#### a. GrowthStocksStrategy.py
      Description: Pick stocks with strong growth indicators. 
      
      Basic filter:
      1. Net Income TTM growth rate: top 1/3
      2. deducted profit/net profit > 50%
      3. roe > 0.01
      4. currentratio > -1
      5. trade volumne top 90% in the past half year
      6. not ST
      
      Scoring:
      1. change positions during reporting period, as the return in the past month could represent the market reaction.
      2. analyst expectation change
      3. analyst agreed expected growth rate
      
      Outcome:
      2018-5-4 to 2022-5-4 excess annual return over 15.5%.
      
      
### 2. Data Process and Automation Needs
This file collects codes that are developed to meet specifc needs in data procession and analysis.

#### a. AutomaticDownload.py
      Description: Automatically download attachments from the mailbox in a time series.
      
#### b. PlacementExtraction.py
      Description: Process raw data sheets from Wind Database and extract specific placement information.
      
#### c. ProcessExcel.py
      Description: Process excel file, and split each into two according to specific requirements.

#### d. QuotationCheck.py
      Description: A risk control model in a quotation procedure according to risk management requirements.

### 3. Option Pricing
This file collects code examples in option pricing work.

#### a. VolatilityGet.py
      Description: Calculate 1m/3m/6m/12m/24m/Garch volatiities.
      
#### b. TrinomialTree_Snowball.py
      Description: Snowball option pricing using trinomial tree model.
                   The model can be used to calculate option price of different snowball structures, e.g. standard, step down, snowball with floor, etc.
                   
#### c. FloatRebate_MonteCarlo_Snowball.py
      Description: Snowball option pricing using MonteCarlo simulations.
                   The model can be used to calculate option price of different snowball structures, e.g. standard, float rebate, step down, etc.

### 4. Snowball

#### a. HistoricalTest_Snowball.py
      Description: Generate historical income distribution of standard snowball structure.
      
#### b. MonteCarlo_Snowball.py
      Description: Simulate income distribution of standard snowball structure by Monte Carlo Methods.
      
#### c. Winrate_Snowball.py
      Description: Calculate historical win rate of standard snowball structure.
