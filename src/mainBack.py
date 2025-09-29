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
import backtest
import analisiFinale
import checkPositionBack


configBack.inizialize()
df_all = TakeDataBack.take_dataframe()



ADXSoglia = [15]




for val_adx in ADXSoglia:
    checkPositionBack.ADXSoglia = val_adx
    backtest.run_backtest(df_all)
    configBack.inizialize()
    
        
#analisiFinale.analisi()



        
    
