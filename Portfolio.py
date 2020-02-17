import pandas as pd
import quandl
from pypfopt.efficient_frontier import EfficientFrontier
from pypfopt import risk_models, expected_returns
import alpaca_trade_api as tradeapi
import os
import threading
import time
from Rebalance import percent_rebalance, rebalance

#------------CONSTANTS----------------------------------------------------------
APCA_API_KEY_ID = 'PK4XBAFHJJ87641VWI74'
APCA_API_SECRET_KEY = 'VWdSvZtqfyPQ16ciwnzieiaWotasuiAYsw/gHcz7'
APCA_API_BASE_URL = 'https://paper-api.alpaca.markets'

selected = ['CNP', 'F', 'WMT', 'GE', 'TSLA','AAPL']
quandl.ApiConfig.api_key = 'fCjG3zcmhtTrPLbEVpYn'

#------------class PortfolioManager---------------------------------------------
class PortfolioManager():    
    def __init__(self):
        self.api = tradeapi.REST(APCA_API_KEY_ID, APCA_API_SECRET_KEY, \
                                 APCA_API_BASE_URL)
        self.r_positions = {}

    def format_percent(self, num):
        if(str(num)[-1] == "%"):
            return float(num[:-1]) / 100
        else:
            return float(num)

    def clear_orders(self):
        try:
            self.api.cancel_all_orders()
            print("All open orders cancelled.")
        except Exception as e:
            print(f"Error: {str(e)}")

    def add_items(self, data):
        ''' Expects a list of lists containing two items: symbol and position qty/pct
        '''
        for row in data:
            self.r_positions[row[0]] = [row[1], 0]

    

    def send_basic_order(self, sym, qty, side):
        qty = int(qty)
        if(qty == 0):
            return
        q2 = 0
        try:
            position = self.api.get_position(sym)
            curr_pos = int(position.qty)
            if((curr_pos + qty > 0) != (curr_pos > 0)):
                q2 = curr_pos
                qty = curr_pos + qty
        except BaseException:
            pass
        try:
            if q2 != 0:
                self.api.submit_order(sym, abs(q2), side, "market", "gtc")
                try:
                    self.api.submit_order(sym, abs(qty), side, "market", "gtc")
                except Exception as e:
                    print(
                        f"Error: {str(e)}. Order of | {abs(qty) + abs(q2)} {sym} {side} | partially sent ({abs(q2)} shares sent).")
                    return False
            else:
                self.api.submit_order(sym, abs(qty), side, "market", "gtc")
            print(f"Order of | {abs(qty) + abs(q2)} {sym} {side} | submitted.")
            return True
        except Exception as e:
            print(
                f"Error: {str(e)}. Order of | {abs(qty) + abs(q2)} {sym} {side} | not sent.")
            return False

    def confirm_full_execution(self, sym, qty, side, expected_qty):
        sent = self.send_basic_order(sym, qty, side)
        if(not sent):
            return

        executed = False
        while(not executed):
            try:
                position = self.api.get_position(sym)
                if int(position.qty) == int(expected_qty):
                    executed = True
                else:
                    print(f"Waiting on execution for {sym}...")
                    time.sleep(20)
            except BaseException:
                print(f"Waiting on execution for {sym}...")
                time.sleep(20)
        print(
            f"Order of | {abs(qty)} {sym} {side} | completed.  Position is now {expected_qty} {sym}.")

    def timeout_execution(self, sym, qty, side, expected_qty, timeout):
        sent = self.send_basic_order(sym, qty, side)
        if(not sent):
            return
        output = []
        executed = False
        timer = threading.Thread(
            target=self.set_timeout, args=(
                timeout, output))
        timer.start()
        while(not executed):
            if(len(output) == 0):
                try:
                    position = self.api.get_position(sym)
                    if int(position.qty) == int(expected_qty):
                        executed = True
                    else:
                        print(f"Waiting on execution for {sym}...")
                        time.sleep(20)
                except BaseException:
                    print(f"Waiting on execution for {sym}...")
                    time.sleep(20)
            else:
                timer.join()
                try:
                    position = self.api.get_position(sym)
                    curr_qty = position.qty
                except BaseException:
                    curr_qty = 0
                print(
                    f"Process timeout at {timeout} seconds: order of | {abs(qty)} {sym} {side} | not completed. Position is currently {curr_qty} {sym}.")
                return
        print(
            f"Order of | {abs(qty)} {sym} {side} | completed.  Position is now {expected_qty} {sym}.")

    def set_timeout(self, timeout, output):
        time.sleep(timeout)
        output.append(True)

#------------End of class PortfolioManager--------------------------------------