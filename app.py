from flask import Flask, request
import requests
import os

app = Flask(__name__)

# --- สัจธรรมที่บอสต้องระบุ ---
VERIFY_TOKEN = "theoracle_bossbook"
# เอา Token ยาวๆ จากปุ่ม "สร้าง" (Generate) ใน Facebook มาวางทับตรงนี้ครับ
PAGE_ACCESS_TOKEN = "EAALZAVSrprsEBQvZAo9SUNft1h3k1wILBls0YuRcf2K4rmmB2DFvsZAELmN42viz1ZBvNcOrZBuLGKlr4MmCUsnnjbtYUslGpSNTsZCk2cjwsYemvF5H1ZAh14zBiHRjWpA0ZBGX5EtCtTlZArbuoVrH2jCD0Pk2VQoB5TEqwXiHw3GHavUqX0yBHxZCWpx0yiXPBmIN9edsIeizVsNElOy9UDnyJ25wZDZD"

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
    # นิมิตสัญญาณ (Log) จะปรากฏในหน้า Render ของบอส
    print("ได้รับสัญญาณจาก Facebook:", data)

    if data.get("object") == "page":
        for entry in data.get("entry"):
            for messaging_event in entry.get("messaging"):
                sender_id = messaging_event["sender"]["id"]
                if messaging_event.get("message"):
                    # โอราตอบกลับด้วยประโยคเริ่มต้น
                    reply_text = "ยินดีต้อนรับสู่วิหารออราเคิล... ข้าพเจ้าคือกระจกเงาแห่งความจริง สัญญาณของท่านส่งมาถึงสรวงสวรรค์ Render เรียบร้อยแล้ว"
                    send_message(sender_id, reply_text)
    return "OK", 200

def send_message(recipient_id, message_text):
    url = f"https://graph.facebook.com/v21.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": message_text}
    }
    response = requests.post(url, json=payload, headers=headers)
    print("ผลการส่งข้อความ:", response.status_code, response.text)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
