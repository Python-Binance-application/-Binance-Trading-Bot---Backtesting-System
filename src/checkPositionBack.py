# IMPORT LIBRERIE
import numpy as np
import matplotlib.pyplot as plt
import ta
from datetime import datetime, timedelta, UTC
import os
import time
from decimal import Decimal, ROUND_DOWN
from binance.client import Client
from binance.enums import SIDE_BUY, SIDE_SELL, ORDER_TYPE_MARKET
from pprint import pprint
import pandas as pd
import calcoloLottiBack

import configBack

#Variabili Globali per entry and exit
ADXSoglia = 30
atrMultiplier = 2


#RSIthresDWN = 40
#RSIthresUP = 60

def check_entry(df_all):
        #print("Check Entry")
    if configBack.net_pos != 0:
        return  # Nessuna posizione aperta
    elif configBack.net_pos == 0:
        last_candle = df_all.iloc[-1]
        penultima_candle = df_all.iloc[-2]
        
        ADX_condition = last_candle['Adx'] < ADXSoglia
        
        touch_condition_long = penultima_candle['Low'] <= penultima_candle['BB_lower'] or last_candle['Low'] <= last_candle['BB_lower']
        touch_condition_short = penultima_candle['High'] >= penultima_candle['BB_upper'] or last_candle['High'] >= last_candle['BB_upper']
        
        candle_condition_long = last_candle['Close'] >= penultima_candle['High']
        candle_condition_short = last_candle['Close'] <= penultima_candle['Low']
        
        condition_entry_long = candle_condition_long and touch_condition_long and ADX_condition
        condition_entry_short = candle_condition_short and touch_condition_short and ADX_condition
        
        stop_loss_long = round(last_candle['Close'] - (last_candle['Atr'] * atrMultiplier),2)
        stop_loss_short = round(last_candle['Close'] + (last_candle['Atr'] * atrMultiplier),2)
        #vedo se non mi fa uscire subito

        
        if (condition_entry_long):
            configBack.stop_loss = stop_loss_long
            configBack.point_edit =  stop_loss_short
            configBack.entry_price = last_candle['Close']
            calcoloLottiBack.get_size()
            configBack.add_trade("BUY",last_candle.name, configBack.entry_price, configBack.net_pos, None)
            #OpenClose.apri_operazione("BUY")
        if (condition_entry_short):
            configBack.stop_loss = stop_loss_short
            configBack.point_edit =  stop_loss_long
            configBack.entry_price = last_candle['Close']
            calcoloLottiBack.get_size()
            configBack.net_pos = - configBack.net_pos
            #OpenClose.apri_operazione("SHORT")
            configBack.add_trade("SHORT", last_candle.name, configBack.entry_price, configBack.net_pos, None)


    


# === STRATEGIA: EXIT ATR ===
def check_exit(last_candle):
    if configBack.net_pos == 0:
        return  # Nessuna posizione aperta
    price = last_candle.Close
    min = last_candle.Low
    max = last_candle.High
    sl = configBack.stop_loss
    medium =last_candle.BB_middle
    entry_price = configBack.entry_price
   
    touch_condition_exit_short = last_candle['Low'] <= last_candle['BB_lower']
    touch_condition_exit_long =last_candle['High'] >= last_candle['BB_upper']

    candle_long = last_candle['Close'] > last_candle['Open']
    candle_short = last_candle['Close'] < last_candle['Open']
    
    
    if configBack.net_pos > 0:  # LONG
        if min <= sl:
            guadagno =  calcolo_Pnl_diff("BUY", configBack.stop_loss)
            configBack.add_trade("CLOSE BUY", last_candle.name, sl, -configBack.net_pos, guadagno)
            configBack.net_pos = 0
            
        elif max > medium and sl != entry_price:
                fee_adjustment = entry_price * 0.0015
                new_stop_loss  = round(entry_price + fee_adjustment, 2)
                if last_candle['Close'] > new_stop_loss + 0.1:
                    configBack.stop_loss = new_stop_loss
                else:
                    guadagno = calcolo_Pnl_diff("LONG", last_candle['Close'])
                    configBack.add_trade("CLOSE LONG", last_candle.name, sl, -configBack.net_pos, guadagno)
                    configBack.net_pos = 0
        
        if candle_short and touch_condition_exit_long:
            guadagno =  calcolo_Pnl_diff("LONG", last_candle['Close'])
            configBack.add_trade("CLOSE LONG", last_candle.name, last_candle['Close'], -configBack.net_pos, guadagno)
            configBack.net_pos = 0
            
           


    elif configBack.net_pos < 0:  # SHORT
        if max >= sl:
            guadagno = calcolo_Pnl_diff("SHORT", configBack.stop_loss)
            configBack.add_trade("CLOSE SHORT", last_candle.name, sl, -configBack.net_pos, guadagno)
            configBack.net_pos = 0
        
        elif min < medium and sl != entry_price:
            fee_adjustment = entry_price * 0.0015
            new_stop_loss  = round(entry_price - fee_adjustment, 2)
            if last_candle['Close'] < new_stop_loss - 0.1:
                configBack.stop_loss = new_stop_loss
            else:
                guadagno = calcolo_Pnl_diff("SHORT", last_candle['Close'])
                configBack.add_trade("CLOSE SHORT", last_candle.name, sl, -configBack.net_pos, guadagno)
                configBack.net_pos = 0
        
        if candle_long and touch_condition_exit_short:
            guadagno =  calcolo_Pnl_diff("SHORT", last_candle['Close'])
            configBack.add_trade("CLOSE SHORT", last_candle.name, last_candle['Close'], -configBack.net_pos, guadagno)
            configBack.net_pos = 0







def calcolo_Pnl_diff(op, exit_price, fee_percent = 0.00075):
    entry_price = configBack.entry_price
    size = configBack.net_pos
    pnl = round((exit_price - entry_price) * size,2)

    # Valore nozionale totale: usato per calcolare la fee su entrata + uscita
    notional = abs(entry_price * size) + abs(exit_price * size)
    total_fee = notional * fee_percent  # entrata + uscita
    #print(f"hai pagato {total_fee} su {notional} quantità comprata")
    pnl_netto = pnl - total_fee
    return round(pnl_netto,2)
