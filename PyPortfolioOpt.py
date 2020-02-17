import pandas as pd
import quandl
from pypfopt.efficient_frontier import EfficientFrontier
from pypfopt import risk_models, expected_returns
import alpaca_trade_api as tradeapi
import os
import threading
import time
from Rebalance import percent_rebalance, rebalance
from Portfolio import PortfolioManager

#------------API Settings----------------------------------------------------------
APCA_API_KEY_ID = 'PK4XBAFHJJ87641VWI74'
APCA_API_SECRET_KEY = 'VWdSvZtqfyPQ16ciwnzieiaWotasuiAYsw/gHcz7'
APCA_API_BASE_URL = 'https://paper-api.alpaca.markets'

selected = ['CNP', 'F', 'WMT', 'GE', 'TSLA','AAPL']
quandl.ApiConfig.api_key = 'fCjG3zcmhtTrPLbEVpYn'

# Call Alpaca's trade API
api = tradeapi.REST(APCA_API_KEY_ID, APCA_API_SECRET_KEY, APCA_API_BASE_URL)

"uncomment to see all positions"
#api.list_positions()

# Import price data from quandl:
# This gives you the ticker, date, and adj_close columns for the tickers selected 
#from quandl.
data = quandl.get_table('WIKI/PRICES', ticker = selected,
                        qopts = { 'columns': ['date', 'ticker', 'adj_close'] },
                        date = { 'gte': '2016-1-1', 'lte': '2018-12-31' }, 
                        paginate=True)

# reorganize data
clean = data.set_index('date')
table = clean.pivot(columns='ticker')

# Calculate expected returns and sample covariance
mean = expected_returns.mean_historical_return(table)
risk = risk_models.sample_cov(table)

# Optimise for max Sharpe ratio, this outputs weights for your portfolio
frontier = EfficientFrontier(mean, risk)
raw_weights = frontier.max_sharpe()

# Format Data 
cleaned_weights = frontier.clean_weights()

#"Uncomment the following line if you want to get the ticker weights in a CSV file."    
# frontier.save_weights_to_file("weights.csv")  # saves to file as "weights.csv"
# returns expected annual return, annual volatility, and sharpe ratio
frontier.portfolio_performance(verbose=True) # assumes: (verbose=False, risk_free_rate=0.02)

# Format Data
lst = []
for key, value in cleaned_weights.items():
    lst.append([key[1], value])

# create PortfolioManager named manager
manager = PortfolioManager()

# inputs previous data into manager
manager.add_items(lst)

# rebalances portfolio with updated information and sends out orders after
# This process will only run for 60 seconds and automatically stop
percent_rebalance(manager, 'timeout')

print(cleaned_weights)