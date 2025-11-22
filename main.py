import requests
import time
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": text})

send_message("Bot Started on Railway 🚀")

while True:
    # TODO: add your FII/DII API check here later
    print("Bot running...")
    time.sleep(10)
