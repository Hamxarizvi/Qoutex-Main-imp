import requests
import time
import pandas as pd
import pandas_ta as ta
import telegram

# ========== CONFIG ==========
PAIR = "GBPUSDT"  # Simulated pair
INTERVAL = "1m"
LIMIT = 100
API_URL = f"https://api.binance.com/api/v3/klines?symbol={PAIR}&interval={INTERVAL}&limit={LIMIT}"

TELEGRAM_TOKEN = "7956580247:AAEk8_lDxIUwwfOh3_0Qt6fYqzZLOPwqTJI"
TELEGRAM_USER = "@QoutexPrivateBot"

bot = telegram.Bot(token=TELEGRAM_TOKEN)

# ========== STRATEGY ==========
def fetch_candles():
    try:
        res = requests.get(API_URL)
        raw = res.json()
        df = pd.DataFrame(raw, columns=[
            "time", "open", "high", "low", "close", "volume",
            "close_time", "quote_asset_volume", "trades",
            "taker_buy_base", "taker_buy_quote", "ignore"])
        df["close"] = df["close"].astype(float)
        df["open"] = df["open"].astype(float)
        return df
    except Exception as e:
        print("Error fetching data:", e)
        return None

def analyze(df):
    df["rsi"] = ta.rsi(df["close"], length=14)
    macd = ta.macd(df["close"])
    df["macd"] = macd["MACD_12_26_9"]
    df["macdsignal"] = macd["MACDs_12_26_9"]
    df["ema_fast"] = ta.ema(df["close"], length=5)
    df["ema_slow"] = ta.ema(df["close"], length=13)

    last = df.iloc[-1]
    if last["rsi"] > 70 and last["macd"] < last["macdsignal"] and last["ema_fast"] < last["ema_slow"]:
        return "SELL"
    elif last["rsi"] < 30 and last["macd"] > last["macdsignal"] and last["ema_fast"] > last["ema_slow"]:
        return "BUY"
    return None

def send_signal(signal):
    msg = f"\n🔥 *Binary Signal Alert* 🔥\nPair: {PAIR}\nAction: {signal} {'📈' if signal=='BUY' else '📉'}\nTimeframe: 1 Minute\nStrategy: RSI + MACD + EMA\nTime: {time.strftime('%H:%M:%S')}"
    try:
        bot.send_message(chat_id=TELEGRAM_USER, text=msg, parse_mode=telegram.ParseMode.MARKDOWN)
        print("Signal sent:", signal)
    except Exception as e:
        print("Telegram Error:", e)

# ========== LOOP ==========
print("🔄 Starting Signal Bot...")
while True:
    data = fetch_candles()
    if data is not None:
        signal = analyze(data)
        if signal:
            send_signal(signal)
    time.sleep(60)