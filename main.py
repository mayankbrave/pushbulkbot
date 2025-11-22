import os
import time
import requests
from bs4 import BeautifulSoup
from flask import Flask, request

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

app = Flask(__name__)

def send(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

# List of FII/DII identifiers
WATCH_NAMES = [
    "Morgan", "Goldman", "UBS", "JP Morgan", "Citigroup", "Nomura",
    "Societe", "HSBC", "BNP", "Credit Suisse", "BofA", "Vanguard",
    "BlackRock", "Templeton",
    "HDFC", "ICICI", "Kotak", "SBI", "LIC", "Axis", "Nippon",
]

last_deals = set()

def fetch_nse_bulk_deals():
    url = "https://www.nseindia.com/api/bulk-deals"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get(url, headers=headers, timeout=10)
        data = r.json()
        return data["data"]
    except:
        return []

def is_fii(name):
    if not name:
        return False
    return any(key.lower() in name.lower() for key in WATCH_NAMES)

def process_deals():
    global last_deals

    deals = fetch_nse_bulk_deals()
    if not deals:
        return

    for d in deals:
        buyer = d.get("buyerName")
        if not is_fii(buyer):
            continue

        stock = d.get("symbol")
        qty = d.get("quantity")
        price = d.get("tradePrice")
        date = d.get("tradeDate")

        id_key = f"{buyer}-{stock}-{qty}-{price}-{date}"

        if id_key in last_deals:
            continue

        last_deals.add(id_key)

        msg = (
            "📈 *FII BUY ALERT*\n"
            f"FII: {buyer}\n"
            f"Stock: {stock}\n"
            f"Exchange: NSE\n"
            f"Type: Bulk Deal\n"
            f"Qty: {qty} shares\n"
            f"Price: ₹{price}\n"
            f"Date: {date}"
        )

        send(msg)

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json()

    if "message" in data:
        text = data["message"]["text"]
        chat = data["message"]["chat"]["id"]

        if text == "/start":
            send("👋 I will alert you whenever FII/DII buy stocks in NSE/BSE.")

        elif text == "/ping":
            send("Alive 😎")

    return "OK"

def loop():
    send("Bot started 🚀")
    while True:
        process_deals()
        print("Checked deals...")
        time.sleep(100)  # every 1.6 minutes

if __name__ == "__main__":
    loop()
