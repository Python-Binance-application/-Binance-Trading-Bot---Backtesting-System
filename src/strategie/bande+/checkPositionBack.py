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
atrMultiplier = 2.5
cont = 5
max_diff = 3

#RSIthresDWN = 40
#RSIthresUP = 60

def check_entry(df_all):
        #print("Check Entry")
    if configBack.net_pos != 0:
        return  # Nessuna posizione aperta
    elif configBack.net_pos == 0:
        last_candle = df_all.iloc[-1]
        penultima_candle = df_all.iloc[-2]
        
        condition_entry_long = penultima_candle['SAR'] < penultima_candle['Close'] and last_candle['SAR'] > last_candle['Close'] and last_candle['Adx'] > ADXSoglia
        condition_entry_short = penultima_candle['SAR'] > penultima_candle['Close'] and last_candle['SAR'] < last_candle['Close'] and last_candle['Adx'] > ADXSoglia
        
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
def exit_atr(last_candle):
    if configBack.net_pos == 0:
        return  # Nessuna posizione aperta
    price = last_candle.Close
    min = last_candle.Low
    max = last_candle.High
    sl = configBack.stop_loss
    point = configBack.point_edit
   
    if configBack.net_pos > 0:  # LONG
        if min <= sl:
            guadagno =  calcolo_Pnl_diff("LONG", configBack.stop_loss)
            configBack.add_trade("CLOSE LONG", last_candle.name, sl, -configBack.net_pos, guadagno)
            configBack.net_pos = 0
        
        elif max > point:
            #print("📈 TP raggiunto LONG")
            configBack.stop_loss += (max - configBack.point_edit)
            configBack.point_edit = max


    elif configBack.net_pos < 0:  # SHORT
        if max >= sl:
            guadagno = calcolo_Pnl_diff("SHORT", configBack.stop_loss)
            configBack.add_trade("CLOSE SHORT", last_candle.name, sl, -configBack.net_pos, guadagno)
            configBack.net_pos = 0
        elif min <= point:
            #print("📉 TP raggiunto SHORT")
            configBack.stop_loss -= (configBack.point_edit - min)
            configBack.point_edit = min







def calcolo_Pnl_diff(op, exit_price, fee_percent = 0.00075):
    entry_price = configBack.entry_price
    size = configBack.net_pos
    pnl = round((exit_price - entry_price) * size,2)

    # Valore nozionale totale: usato per calcolare la fee su entrata + uscita
    notional = abs(entry_price * size) + abs(exit_price * size)
    total_fee = notional * fee_percent  # entrata + uscita
    
    pnl_netto = pnl - total_fee
    return round(pnl_netto,2)
