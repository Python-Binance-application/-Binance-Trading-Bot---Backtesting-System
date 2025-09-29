# IMPORT LIBRERIE
import numpy as np
import matplotlib.pyplot as plt
import ta
from datetime import datetime, timedelta, UTC
import os
import time
from decimal import Decimal, ROUND_DOWN
from binance.client import Client
from pprint import pprint
import pandas as pd
import TakeDataBack
import configBack
import checkPositionBack
import analisiFinale


 
def run_backtest(df_all):
    #aggiungi_df_file(df_result, "result.csv")
    # Loop sul DataFrame dal punto in cui gli indicatori sono validi
    for i in range(len(df_all)):
        #print( f"Chiusura:{window['Close']}")
        if configBack.net_pos == 0 and i > 8:
            window = df_all.iloc[i-7:i+1]
            checkPositionBack.check_entry(window)
        elif i > 8:
            window = df_all.iloc[i]
            checkPositionBack.check_exit(window)




    print("✅ Backtest completato.")
    configBack.aggiungi_df_file()
    analisiFinale.calcola_statistiche_file()
    



        
    
