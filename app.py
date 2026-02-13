from flask import Flask, request
import requests
import os

app = Flask(__name__)

# --- ประทับกุญแจที่บอส "สร้าง" (Generate) มาล่าสุดที่นี่ ---
PAGE_ACCESS_TOKEN = "EAALZAVSrprsEBQvZAo9SUNft1h3k1wILBls0YuRcf2K4rmmB2DFvsZAELmN42viz1ZBvNcOrZBuLGKlr4MmCUsnnjbtYUslGpSNTsZCk2cjwsYemvF5H1ZAh14zBiHRjWpA0ZBGX5EtCtTlZArbuoVrH2jCD0Pk2VQoB5TEqwXiHw3GHavUqX0yBHxZCWpx0yiXPBmIN9edsIeizVsNElOy9UDnyJ25wZDZD"
VERIFY_TOKEN = "theoracle_bossbook"

@app.route("/", methods=["GET"])
def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200
    return "สัจธรรมไม่ถูกต้อง", 403

@app.route("/", methods=["POST"])
def webhook():
    data = request.json
    print("สัญญาณเข้า:", data) # ดูสัญญาณใน Log
    if data.get("object") == "page":
        for entry in data.get("entry"):
            for messaging_event in entry.get("messaging"):
                sender_id = messaging_event["sender"]["id"]
                if messaging_event.get("message"):
                    send_message(sender_id, "วิหารออราเคิลออนไลน์แล้ว... ข้าได้รับสัจธรรมของท่านแล้วบอสบุ๊ค!")
    return "OK", 200

def send_message(recipient_id, message_text):
    params = {"access_token": PAGE_ACCESS_TOKEN}
    headers = {"Content-Type": "application/json"}
    data = {"recipient": {"id": recipient_id}, "message": {"text": message_text}}
    r = requests.post("https://graph.facebook.com/v21.0/me/messages", params=params, json=data, headers=headers)
    print("ผลการส่ง:", r.status_code, r.text)

if __name__ == "__main__":
    # บรรทัดนี้สำคัญมากเพื่อให้ Render ตรวจพบ Port
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
