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
        condition_entry_long = last_candle['Ema_fast'] > last_candle['Ema_slow'] and last_candle['Adx'] > ADXSoglia
        condition_entry_short = last_candle['Ema_fast'] < last_candle['Ema_slow'] and last_candle['Adx'] > ADXSoglia
        
        stop_loss_long = last_candle['Close'] - (last_candle['Atr'] * atrMultiplier)
        stop_loss_short = last_candle['Close'] + (last_candle['Atr'] * atrMultiplier)
        #vedo se non mi fa uscire subito
        check = exit_diff(df_all)
        
        if (condition_entry_long and check != 1):
            configBack.stop_loss = stop_loss_long
            configBack.point_edit =  stop_loss_short
            configBack.entry_price = last_candle['Close']
            calcoloLottiBack.get_size()
            configBack.add_trade("BUY",last_candle.name, configBack.entry_price, configBack.net_pos, None)
            #OpenClose.apri_operazione("BUY")
        if (condition_entry_short and check != 2):
            configBack.stop_loss = stop_loss_short
            configBack.point_edit =  stop_loss_long
            configBack.entry_price = last_candle['Close']
            calcoloLottiBack.get_size()
            configBack.net_pos = - configBack.net_pos
            #OpenClose.apri_operazione("SHORT")
            configBack.add_trade("SHORT", last_candle.name, configBack.entry_price, configBack.net_pos, None)


def calcolo_Pnl_diff(op, exit_price, fee_percent = 0.00075):
    entry_price = configBack.entry_price
    size = configBack.net_pos
    pnl = round((exit_price - entry_price) * size,2)

    # Valore nozionale totale: usato per calcolare la fee su entrata + uscita
    notional = abs(entry_price * size) + abs(exit_price * size)
    total_fee = notional * fee_percent  # entrata + uscita
    
    pnl_netto = pnl - total_fee
    return pnl_netto
    


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
            configBack.exit_diff_able = False
            configBack.net_pos = 0
            
        elif max >= point and configBack.exit_diff_able == False:
            #print("📈 TP raggiunto LONG")
            configBack.stop_loss = configBack.entry_price
            configBack.exit_diff_able = True

    elif configBack.net_pos < 0:  # SHORT
        if max >= sl:
            guadagno = calcolo_Pnl_diff("SHORT", configBack.stop_loss)
            configBack.add_trade("CLOSE SHORT", last_candle.name, sl, -configBack.net_pos, guadagno)
            configBack.exit_diff_able = False
            configBack.net_pos = 0
        elif min <= point and configBack.exit_diff_able == False:
            #print("📉 TP raggiunto SHORT")
            configBack.stop_loss = configBack.entry_price
            configBack.exit_diff_able = True



    
#deve essere controllato ogni candela chiusa
def exit_diff(df_all):
    if configBack.net_pos == 0:
        return  # Nessuna posizione aperta

    #print("Check Exit")
    num = 0


    # Conta se Ema_fast è decrescente nelle ultime 5 candele
    for i in range(1, cont):
        if df_all['Ema_fast'].iloc[-(i)] < df_all['Ema_fast'].iloc[-(i + 1)]:
            num += 1

    last_candle = df_all.iloc[-1]
    prezzo_chiusura = last_candle['Close']
    timestamp = last_candle.name

    if configBack.net_pos > 0 and num >= max_diff:
        guadagno = calcolo_Pnl_diff("LONG", prezzo_chiusura)
        configBack.add_trade("CLOSE LONG", timestamp, prezzo_chiusura, -configBack.net_pos, guadagno)
        configBack.exit_diff_able = False
        configBack.net_pos = 0  # chiusura
        return 1 # 1 -- l'operazione BUY non deve essere aperta

    elif configBack.net_pos < 0 and num < max_diff:
        guadagno = calcolo_Pnl_diff("SHORT", prezzo_chiusura)
        configBack.add_trade("CLOSE SHORT", timestamp, prezzo_chiusura, -configBack.net_pos, guadagno)
        configBack.exit_diff_able = False
        configBack.net_pos = 0  # chiusura
        return 2 #2 -- l'operazione SHORT non deve essere aperta (viene subito chiusa)
        
    return 0
