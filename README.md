# 📊 Binance Trading Bot - Backtesting System

Sistema completo di backtesting per strategie di trading su Binance con analisi statistica avanzata e ottimizzazione parametri.

## 📋 Descrizione

Questo sistema permette di testare strategie di trading su dati storici di Binance, utilizzando indicatori tecnici avanzati e generando report dettagliati delle performance. Ideale per validare strategie prima di utilizzarle in real-time.

### ⚙️ Indicatori Utilizzati

- **ATR (Average True Range)**: Per calcolare stop loss dinamici
- **ADX (Average Directional Index)**: Per misurare la forza del trend
- **Bande di Bollinger**: Per identificare condizioni di ipercomprato/ipervenduto
- **SAR Parabolico**: Indicatore trend-following

### 🎯 Strategia di Trading

**Condizioni di Entry:**

**LONG**:
- Prezzo tocca o supera la banda di Bollinger inferiore
- La candela corrente chiude sopra il massimo della candela precedente
- ADX < soglia configurabile (trend debole, possibile inversione)

**SHORT**:
- Prezzo tocca o supera la banda di Bollinger superiore
- La candela corrente chiude sotto il minimo della candela precedente
- ADX < soglia configurabile (trend debole, possibile inversione)

**Condizioni di Exit:**
1. Stop loss raggiunto (basato su ATR × moltiplicatore)
2. Prezzo attraversa la banda di Bollinger media con breakeven attivato
3. Candela di inversione dopo tocco della banda opposta

## 🚀 Installazione

### Prerequisiti

- Python 3.8 o superiore
- Account Binance (solo per scaricare dati storici)

### Setup

1. **Clona il repository**
```bash
git clone https://github.com/tuo-username/binance-backtest-bot.git
cd binance-backtest-bot
```

2. **Installa le dipendenze**
```bash
pip install -r requirements.txt
```

3. **Configura le API Keys**

Modifica il file `configBack.py` e inserisci le tue credenziali Binance:

```python
api_key = "LA_TUA_API_KEY_BINANCE"
api_secret = "LA_TUA_API_SECRET_BINANCE"
```

4. **Configura i parametri di backtest**

Nel file `configBack.py`:
```python
symbol = "SOLUSDT"                    # Coppia di trading
tf = Client.KLINE_INTERVAL_5MINUTE    # Timeframe
start_str = "01 Jul 2025 00:00:00"    # Data inizio backtest
end_str = "30 Jul 2025 00:00:00"      # Data fine backtest

balance = 4000        # Capitale iniziale
esposizione = 0.8     # 80% del capitale per trade
rischio = 0.01        # 1% di rischio per trade
```

Nel file `checkPositionBack.py`:
```python
ADXSoglia = 30           # Soglia ADX per entry
atrMultiplier = 2        # Moltiplicatore ATR per stop loss
```

## 📊 Utilizzo

### Esecuzione Backtest Singolo

```bash
python mainBack.py
```

### Test con Parametri Multipli

Modifica il file `mainBack.py` per testare diverse configurazioni:

```python
ADXSoglia = [15, 20, 25, 30]  # Testa diverse soglie ADX

for val_adx in ADXSoglia:
    checkPositionBack.ADXSoglia = val_adx
    backtest.run_backtest(df_all)
    configBack.inizialize()
```

### Output Generati

Il sistema genera automaticamente:

1. **operazioni_backtest.csv**: Log dettagliato di tutte le operazioni
   - Tipo operazione (BUY/SHORT/CLOSE)
   - Timestamp
   - Prezzo di esecuzione
   - Quantità
   - Profit & Loss per ogni chiusura

2. **statistiche_backtest.csv**: Metriche aggregate
   - Date di inizio/fine backtest
   - Budget iniziale e parametri di rischio
   - Numero operazioni totali
   - Win rate e profitto medio
   - Max drawdown
   - Parametri strategici utilizzati

3. **solusdt.csv**: Dati storici con indicatori calcolati

## 📈 Metriche Analizzate

Il sistema calcola automaticamente:

- **PNL Totale**: Profitto/perdita totale del periodo
- **Numero Operazioni**: Totale trades eseguiti (LONG/SHORT)
- **Win Rate**: Percentuale di operazioni in profitto
- **Profitto Medio**: Media del P&L per operazione
- **Max Drawdown**: Massima perdita consecutiva
- **Operazioni in Profitto/Perdita**: Conteggio dettagliato

### Esempio Output Console

```
📊 Dati di partenza
------------------------
Budget iniziale    : 4000
  ESPOSIZIONE      : 80.0 %
  RISCHIO          : 1.0 %

📊 STATISTICHE BACKTEST
------------------------
Operazioni totali      : 140
  BUY                  : 70
  SHORT                : 70
Operazioni chiuse      : 140
  In profitto          : 85
  In perdita           : 55
Win rate               : 60.71 %
PNL Totale             : 1245.67
Profitto medio         : 8.90
Max Drawdown           : 234.50
```

## 📁 Struttura del Progetto

```
├── mainBack.py                 # Entry point per eseguire backtest
├── configBack.py              # Configurazioni e parametri globali
├── TakeDataBack.py            # Download e preparazione dati storici
├── checkPositionBack.py       # Logica di entry/exit strategy
├── calcoloLottiBack.py        # Calcolo position size
├── backtest.py                # Engine principale del backtest
├── analisiFinale.py           # Calcolo statistiche e generazione report
├── operazioni_backtest.csv    # Output: log operazioni
├── statistiche_backtest.csv   # Output: metriche aggregate
└── solusdt.csv               # Dati storici con indicatori
```

## 🔧 Personalizzazione Strategia

### Modificare Parametri Entry/Exit

Modifica `checkPositionBack.py`:

```python
# Parametri entry
ADXSoglia = 30          # Forza trend minima
atrMultiplier = 2       # Distanza stop loss

# Condizioni personalizzate
def check_entry(df_all):
    # Aggiungi qui le tue condizioni
    pass
```

### Aggiungere Nuovi Indicatori

In `TakeDataBack.py`:

```python
def get_df_update(df_all):
    # Esempio: aggiungi MACD
    df_all['MACD'] = ta.trend.MACD(
        close=df_all['Close']
    ).macd()
    return df_all
```

### Modificare Position Sizing

In `calcoloLottiBack.py`:

```python
def get_size():
    # Implementa qui la tua logica di sizing
    # Basata su Kelly Criterion, Fixed Fractional, etc.
    pass
```

## 📊 Ottimizzazione Parametri

### Walk-Forward Analysis

```python
# Esempio: test su periodi multipli
periodi = [
    ("01 Jan 2025", "31 Mar 2025"),
    ("01 Apr 2025", "30 Jun 2025"),
    ("01 Jul 2025", "30 Sep 2025")
]

for start, end in periodi:
    configBack.start_str = start
    configBack.end_str = end
    df_all = TakeDataBack.take_dataframe()
    backtest.run_backtest(df_all)
```

### Grid Search Parametri

```python
# Test combinazioni multiple
adx_values = [15, 20, 25, 30]
atr_values = [1.5, 2.0, 2.5, 3.0]

for adx in adx_values:
    for atr in atr_values:
        checkPositionBack.ADXSoglia = adx
        checkPositionBack.atrMultiplier = atr
        backtest.run_backtest(df_all)
        configBack.inizialize()
```

## ⚠️ Note Importanti

### Considerazioni sul Backtesting

- **Overfitting**: Evita di ottimizzare eccessivamente su dati storici
- **Slippage**: Il backtest non considera sempre lo slippage reale
- **Fees**: Include commissioni dello 0.075% per operazione
- **Dati**: Assicurati che i dati storici siano completi e accurati
- **Forward Testing**: Testa sempre su dati out-of-sample

### Limitazioni

- Non simula condizioni di mercato estreme (flash crash, illiquidità)
- Non considera la profondità del book
- Assume esecuzione istantanea agli ordini
- Non simula rejected orders o partial fills

## 🔍 Debugging e Troubleshooting

### Nessuna operazione eseguita
- Verifica che ADXSoglia non sia troppo alta
- Controlla che i dati contengano abbastanza candele
- Verifica che gli indicatori siano calcolati correttamente

### Risultati irrealistici
- Controlla il calcolo delle fees
- Verifica lo slippage simulation
- Assicurati che lo stop loss sia realistico

### Errori di memoria
- Riduci il periodo di backtest
- Aumenta il timeframe (usa 15m invece di 5m)
- Processa i dati in chunks

## 📈 Confronto con Live Trading

Prima di passare al live trading:

1. ✅ Backtest su almeno 6 mesi di dati
2. ✅ Forward test su 1-2 mesi out-of-sample
3. ✅ Paper trading per 1 mese
4. ✅ Live con capitale ridotto (10-20%)
5. ✅ Monitora per divergenze rispetto al backtest

## 🤝 Contribuire

Le pull request sono benvenute! Per modifiche importanti:

1. Fork il progetto
2. Crea un branch per la feature (`git checkout -b feature/AmazingFeature`)
3. Commit le modifiche (`git commit -m 'Add AmazingFeature'`)
4. Push al branch (`git push origin feature/AmazingFeature`)
5. Apri una Pull Request

## 📝 TODO / Miglioramenti Futuri

- [ ] Monte Carlo simulation per robustezza
- [ ] Walk-forward optimization automatica
- [ ] Visualizzazione equity curve
- [ ] Export report HTML/PDF
- [ ] Confronto multi-strategia
- [ ] Analisi correlazione con market conditions
- [ ] Integrazione con database SQL
- [ ] Dashboard interattiva con Streamlit

## 📄 Licenza

[MIT](LICENSE)

## ⚖️ Disclaimer

**IMPORTANTE**: Il backtesting è solo uno strumento di analisi. Le performance passate non garantiscono risultati futuri. Questo software è fornito per scopi educativi e di ricerca.

- ⚠️ Il trading di criptovalute comporta rischi significativi
- ⚠️ Non investire più di quanto puoi permetterti di perdere
- ⚠️ Testa sempre su paper trading prima del live
- ⚠️ I risultati del backtest possono differire dal live trading
- ⚠️ Gli autori non sono responsabili per perdite finanziarie

---

**Creato per traders che vogliono testare le proprie strategie prima di rischiare capitale reale** 📊✨
