import ccxt
import os
from ta.trend import EMAIndicator
from ta.momentum import RSIIndicator
import time
import random

api_key = os.getenv("API_KEY")
api_secret = os.getenv("API_SECRET")
pair = os.getenv("PAIR", "DOGE5L/USDT")
stake_amount = float(os.getenv("STAKE_AMOUNT", "100"))
dry_run = os.getenv("DRY_RUN", "true").lower() == "true"
profit_target = float(os.getenv("PROFIT_TARGET", "0.04"))

exchange = ccxt.gateio({
    'apiKey': api_key,
    'secret': api_secret,
    'enableRateLimit': True,
})

def get_ohlcv():
    candles = exchange.fetch_ohlcv(pair, timeframe='5m', limit=50)
    closes = [c[4] for c in candles]
    return closes

def simulate_trade():
    closes = get_ohlcv()
    ema9 = EMAIndicator(close=pd.Series(closes), window=9).ema_indicator()
    ema21 = EMAIndicator(close=pd.Series(closes), window=21).ema_indicator()
    rsi = RSIIndicator(close=pd.Series(closes), window=14).rsi()

    if ema9.iloc[-1] > ema21.iloc[-1] and ema9.iloc[-2] <= ema21.iloc[-2] and rsi.iloc[-1] > 50:
        print("📈 سیگنال خرید شناسایی شد!")
        if not dry_run:
            print(f"✅ سفارش خرید {stake_amount} {pair}")
        bought_price = closes[-1]
        # بررسی حد سود ۴٪
        while True:
            time.sleep(10)
            current_price = exchange.fetch_ticker(pair)['last']
            profit = (current_price - bought_price) / bought_price
            if profit >= profit_target:
                print("🎯 سود ۴٪ حاصل شد، فروش انجام شد!")
                if not dry_run:
                    print("✅ فروش انجام شد.")
                break
            elif ema9.iloc[-1] < ema21.iloc[-1]:
                print("📉 EMA9 زیر EMA21، فروش اضطراری")
                break

while True:
    try:
        simulate_trade()
        time.sleep(60)
    except Exception as e:
        print("❌ خطا:", e)
        time.sleep(30)
