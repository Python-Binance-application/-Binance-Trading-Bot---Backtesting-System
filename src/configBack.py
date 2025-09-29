from binance.client import Client
import pandas as pd

symbol = "SOLUSDT"
tf=Client.KLINE_INTERVAL_5MINUTE
filename="solusdt.csv"
start_str = "01 Jul 2025 00:00:00"
end_str = "30 Jul 2025 00:00:00"

balance = 4000
esposizione = 0.8 #80%
rischio = 0.01 #1%

api_key = "m5pQMdYETwuL7x4aM2tepQIlaNy6EMWzjisMdB8uGhGgBqoEyrs69lxFycVIeKDU"
api_secret = "h5VxPjOEJMlvvrDJNyygulOmlUErklPNQyUDvysIDuKhoDoK9Xzom7nXUy9YrZo3"
client = 0

#verranno modificate durante l'esecuzione
stop_loss = -1
point_edit = -1
exit_diff_able = False
entry_price = 0
net_pos = 0


# buy o sell
azione = "BUY"
# minima quantità solo da acquistare
minimo_acquistabile = 0.05

df_result = 0
file_result = "operazioni_backtest.csv"
cont = 0


file_analisi = "analisi.csv"




def inizialize():
    get_connection_binance()
    reset_variabili_globali()
    create_result()


def reset_variabili_globali ():
    global stop_loss, point_edit, exit_diff_able, entry_price, net_pos, df_result
    stop_loss = -1
    point_edit = -1
    exit_diff_able = False
    entry_price = 0
    net_pos = 0


    
    
def get_connection_binance():
    global client
    client = Client(api_key, api_secret, requests_params={ 'timeout': 20 })



def create_result():
    global df_result
    # Crea DataFrame con tipi espliciti per evitare FutureWarning
    df_result = pd.DataFrame({
        'Tipo': pd.Series(dtype='str'),
        'Data/Ora': pd.Series(dtype='str'),  # o 'datetime64[ns]' se vuoi usare datetime
        'Prezzo': pd.Series(dtype='float'),
        'Quantità': pd.Series(dtype='float'),
        'P&L': pd.Series(dtype='float')
    })

    df_result.index.name = 'CodTrade'

    
def add_trade(tipo, data_ora, prezzo, quantita, pnl):
    global df_result

    # Calcola il prossimo CodTrade
    next_id = 1 if df_result.empty else df_result.index.max() + 1

       # Costruisci la riga da aggiungere
    new_trade = {
        'Tipo': str(tipo),
        'Data/Ora': str(data_ora),  
        'Prezzo': float(prezzo),
        'Quantità': float(quantita),
        'P&L': float(pnl) if pnl is not None else 0
    }
    # Aggiungi la riga al DataFrame
    df_result.loc[next_id] = new_trade
    
    
def aggiungi_df_file():
    df_result.to_csv(file_result, index = True)
    
