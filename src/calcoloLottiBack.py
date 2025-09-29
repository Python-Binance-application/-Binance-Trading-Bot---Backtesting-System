# IMPORT LIBRERIE
import matplotlib.pyplot as plt
import ta
import os
from binance.client import Client
from pprint import pprint
import configBack


def get_size():
    min_acquistabile = round (10 /configBack.entry_price,2)
    esp = size_esposizione()
    rischio = size_rischio()
    configBack.net_pos = float(min(size_esposizione(), size_rischio()))
    if (configBack.net_pos <= min_acquistabile): # dollari è il minimo acquistabile
        configBack.net_pos = float(min_acquistabile)
    
    
    
    
    
    
def size_esposizione():
    return round(configBack.balance * configBack.esposizione / configBack.entry_price,2)
        
    
def size_rischio():
    pips = abs(configBack.stop_loss - configBack.entry_price)
    return round((configBack.balance * configBack.rischio)/pips,2)
    
