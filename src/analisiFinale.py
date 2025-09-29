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
import checkPositionBack

def calcola_statistiche():
    # 1. Somma totale del Profit & Loss (solo operazioni chiuse)
    total_pnl = configBack.df_result['P&L'].dropna().sum()

    # 2. Numero totale operazioni
    n_operazioni = len(configBack.df_result) // 2  # ogni trade ha 1 apertura + 1 chiusura

    # 3. Numero BUY / SHORT
    n_buy = (configBack.df_result['Tipo'] == 'BUY').sum()
    n_short = (configBack.df_result['Tipo'] == 'SHORT').sum()

    # 4. Numero operazioni chiuse in profitto / perdita
    pnl_chiusure = configBack.df_result[configBack.df_result['P&L'].notna()]
    n_profitti = (pnl_chiusure['P&L'] > 0).sum()
    n_perdite = (pnl_chiusure['P&L'] < 0).sum()

    # 5. Percentuale vincite
    win_rate = round(n_profitti / len(pnl_chiusure) * 100, 2) if len(pnl_chiusure) > 0 else 0.0

    # 6. Massimo Drawdown
    cumulative_pnl = pnl_chiusure['P&L'].cumsum()
    max_drawdown = (cumulative_pnl.cummax() - cumulative_pnl).max()

    # 7. Profitto medio per operazione chiusa
    avg_pnl = pnl_chiusure['P&L'].mean()
    
    #Dati di partenza
    print("📊 Dati di partenza\n------------------------")
    print(f"Badget iniziale    : {configBack.balance}")
    print(f"  ESPOSIZIONE            : {configBack.esposizione*100} %")
    print(f"  RISCHIO                : {configBack.rischio*100} %")
    # Risultati
    print("📊 STATISTICHE BACKTEST\n------------------------")
    print(f"Operazioni totali      : {n_operazioni}")
    print(f"  BUY                  : {n_buy}")
    print(f"  SHORT                : {n_short}")
    print(f"Operazioni chiuse      : {len(pnl_chiusure)}")
    print(f"  In profitto          : {n_profitti}")
    print(f"  In perdita           : {n_perdite}")
    print(f"Win rate               : {win_rate} %")
    print(f"PNL Totale             : {round(total_pnl, 2)}")
    print(f"Profitto medio         : {round(avg_pnl, 2)}")
    print(f"Max Drawdown           : {round(max_drawdown, 2)}")




def calcola_statistiche_file():
    df_result = configBack.df_result
    # === Calcoli principali ===
    total_pnl = df_result['P&L'].dropna().sum()
    n_operazioni = len(df_result) // 2
    n_buy = (df_result['Tipo'] == 'BUY').sum()
    n_short = (df_result['Tipo'] == 'SHORT').sum()
    pnl_chiusure = df_result[df_result['P&L'].notna()]
    n_profitti = (pnl_chiusure['P&L'] > 0).sum()
    n_perdite = (pnl_chiusure['P&L'] < 0).sum()
    win_rate = round(n_profitti / len(pnl_chiusure) * 100, 2) if len(pnl_chiusure) > 0 else 0.0
    cumulative_pnl = pnl_chiusure['P&L'].cumsum()
    max_drawdown = (cumulative_pnl.cummax() - cumulative_pnl).max()
    avg_pnl = pnl_chiusure['P&L'].mean()

    # === Parametri iniziali e strategia ===
    iniziale = configBack.balance
    esposizione = configBack.esposizione * 100
    rischio = configBack.rischio * 100

    # === Parametri strategici globali ===
    strategy_params = {
        'ADXSoglia': checkPositionBack.ADXSoglia,
        'ATR Multiplier': checkPositionBack.atrMultiplier
        #'Candele per uscita diff (cont)': checkPositionBack.cont,
        #'Soglia max differenza (max_diff)': checkPositionBack.max_diff
    }

    # === Dizionario finale ===
    stats = {
        'start date' : configBack.start_str ,
        'end date' : configBack.end_str ,
        'Badget iniziale': iniziale,
        'Esposizione (%)': esposizione,
        'Rischio (%)': rischio,
        'Operazioni totali': n_operazioni,
        'BUY': n_buy,
        'SHORT': n_short,
        'Operazioni chiuse': len(pnl_chiusure),
        'In profitto': n_profitti,
        'In perdita': n_perdite,
        'Win rate (%)': win_rate,
        'PNL Totale': round(total_pnl, 2),
        'Profitto medio': round(avg_pnl, 2),
        'Max Drawdown': round(max_drawdown, 2),
        **strategy_params
    }

    df_stats = pd.DataFrame([stats])
    file_name = "statistiche_backtest.csv"

    # Se il file esiste, fai append senza header
    if os.path.exists(file_name):
        df_stats.to_csv(file_name, mode='a', index=False, header=False)
    else:
        df_stats.to_csv(file_name, index=False)

    print(f"✅ Statistiche salvate in '{file_name}' (append mode)")
