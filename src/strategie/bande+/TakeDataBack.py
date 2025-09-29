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
import configBack

start_str = configBack.start_str
end_str = configBack.end_str


def get_df_update(df_all):
        # Calcolo solo su righe nuove
       
        df_all['Atr'] = ta.volatility.AverageTrueRange(
            high=df_all['High'], low=df_all['Low'], close=df_all['Close'], window=14
        ).average_true_range().loc[df_all.index].round(2)
        
        df_all['Adx'] = ta.trend.ADXIndicator(
            high=df_all['High'], low=df_all['Low'], close=df_all['Close'], window=30
        ).adx().loc[df_all.index].round(2)
        
        df_all['SAR'] = ta.trend.PSARIndicator(
        high=df_all['High'], low=df_all['Low'], close=df_all['Close'],
        step=0.02, max_step=0.2
    ).psar().loc[df_all.index].round(2)
    
        return df_all
        
        
def take_dataframe():
    global start_str, end_str

    try:
        df_old = pd.read_csv(configBack.filename, parse_dates=['Timestamp'], index_col='Timestamp')
    except FileNotFoundError:
        df_old = pd.DataFrame()
    
    if not df_old.empty:
        return df_old
    else:
        symbol = configBack.symbol
        tf = configBack.tf
        start_dt = datetime.strptime(start_str, "%d %b %Y %H:%M:%S")
        end_dt = datetime.strptime(end_str, "%d %b %Y %H:%M:%S")
        
        try:
            klines = configBack.client.get_historical_klines(
                symbol,
                tf,
                start_str=start_dt.strftime("%d %b %Y %H:%M:%S"),
                end_str=end_dt.strftime("%d %b %Y %H:%M:%S")
            )
        except Exception as e:
            print("Presa Dati Errore:", e)
            return

        if not klines:
            print("Nessun nuovo dato da aggiornare.")
            return

        df_old = pd.DataFrame(klines, columns=['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume',
                                               'close_time', 'quote_av', 'trades', 'tb_base_av', 'tb_quote_av', 'ignore'])

        df_old['Timestamp'] = pd.to_datetime(df_old['Timestamp'], unit='ms')
        df_old.set_index('Timestamp', inplace=True)
        df_old.drop(['close_time', 'quote_av', 'trades', 'tb_base_av', 'tb_quote_av', 'ignore'], axis=1, inplace=True)
        df_old = df_old.astype('float64')
        df_old = get_df_update(df_old)
        # 🔴 Rimuovi righe con NaN o con almeno un valore == 0
        df_old.replace(0, np.nan, inplace=True)  # Trasforma gli 0 in NaN
        df_old.dropna(inplace=True)              # Rimuove tutte le righe con almeno un NaN
        df_old.to_csv(configBack.filename, index=True)
        print("Dati caricati.")
        return df_old
