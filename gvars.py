# encoding: utf-8

# This code is free, THANK YOU!
# It is explained at the guide you can find at www.theincompleteguide.com
# You will also find improvement ideas and explanations

from pathlib import Path
from datetime import datetime
import os

MAX_WORKERS = 10 # max threads at a time 

gainRatio = 1.5 # takeProfit = -stopLoss*gainRatio
stopLossMargin = 0.05 # extra margin for the stop loss

operEquity = 10000 # defines the target amount per execution ($)
limitOrderMargin = 0.1 # percentage that defines the offset for the limit orders

# API keys loaded from environment variables (recommended)
# Option 1: Set environment variables before running
#   export ALPACA_API_KEY="your-key-here"
#   export ALPACA_API_SECRET_KEY="your-secret-here"
# Option 2: Edit below (not recommended — may accidentally get committed)
API_KEY = os.environ.get("ALPACA_API_KEY", "")
API_SECRET_KEY = os.environ.get("ALPACA_API_SECRET_KEY", "")
ALPACA_API_URL = os.environ.get("ALPACA_API_URL", "https://paper-api.alpaca.markets")

# Live trading guard — warn if using live endpoint
if "live" in ALPACA_API_URL.lower() and API_KEY == "":
    print('\n\n##### \n\nWARNING: LIVE TRADING ENDPOINT DETECTED BUT NO API KEY SET! \n\n##### \n\n')

# this block checks whether you have your keys written or not
if API_KEY == "" or API_SECRET_KEY == "":
    print('\n\n##### \n\nPlease set ALPACA_API_KEY and ALPACA_API_SECRET_KEY environment variables! \n\nSee gvars.py for instructions. \n\n##### \n\n')
    raise ValueError("Missing Alpaca API credentials")

################################################################ ATTEMPTS ->
# max iteration attempts for the different actions
maxAttempts = {
            'SO':5, # SUBMIT ORDER
            'CP':5, # CHECK POSITION
            'CO':5, # CANCEL ORDER
            'LHD1':10, # LOAD HISTORICAL DATA 1
            'LHD2':20 # LOAD HISTORICAL DATA 2
            }

# limit for the indicators
limStoch = {
            'maxBuy':75, # max allowed value to buy
            'minSell':25  # min allowed value to sell
            }

################################################################ TIMEFRAMES ->
# fetch historical data intervals
fetchItval = {
            'little':'5Min',
            'big':'30Min'
            }

# timeouts that will kill a process
timeouts = {
        'GT':0 # if 0, it discards a bad general trend instantly
        }

# waiting time before repeating each iteration
sleepTimes = {
                'GT': 10*60, # general trend
                'IT': 2*60, # instant trend
                'RS': 60, # RSI
                'ST': 60, # stochastic every minut
                'CO': 10, # check order every 10 seconds
                'SO': 5, # submit order every 5 seconds
                'LH': 5, # load_historical_data
                'PF': 10, # price fetch (current price)
                'CP': 10, # check position, to check if it entered
                'GS': 60, # get slope inside enter position
                'UA': 10*60 # unlock assets
                }

################################################################ PATHS ->
home = str(Path.home())

FILES_FOLDER = home + '/tbot_files_test/'
RAW_ASSETS = './_raw_assets.csv' # you should have this list at the same folder than everything
LOGS_PATH = FILES_FOLDER + 'logs/'
