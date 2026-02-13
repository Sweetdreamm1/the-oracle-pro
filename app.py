from flask import Flask, request
import requests
import os

app = Flask(__name__)

# --- ข้อมูลสัจธรรมที่บอสประทับไว้ ---
VERIFY_TOKEN = "theoracle_bossbook"
PAGE_ACCESS_TOKEN = "EAALZAVSrprsEBQhYW3ZAwC5W2C0QnLqkqbOSzhvMyMJZCZB2wdNvTdDp5cFjXfgSJkm3zbBLfBWGNDRqre6WYa84VdMIYS2BtbGPBroDHc1HlRQPgP9UIZCchGEqzVE9QDZCNYwkuZA4Msmt9NMu7i8VcT6ZCrjpFCH74GabZCtusDCwOYWSWthBhwV0kY4RQW1sPtZBSxsXomesmeef6GwUAZCuiPK9AZDZD"

@app.route("/", methods=["GET"])
def verify():
    # ส่วนนี้ใช้ยืนยันตัวตนกับ Facebook Webhook
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200
    return "สัจธรรมไม่ถูกต้อง", 403

@app.route("/", methods=["POST"])
def webhook():
    # ส่วนนี้ใช้รับข้อมูลจาก Messenger
    data = request.json
    print(data)

    if data.get("object") == "page":
        for entry in data.get("entry"):
            for messaging_event in entry.get("messaging"):
                sender_id = messaging_event["sender"]["id"]
                
                if messaging_event.get("message"):
                    message_text = messaging_event["message"].get("text")
                    
                    # ประโยคทักทายเริ่มต้นของโอรา
                    reply_text = "ยินดีต้อนรับสู่วิหารออราเคิล... ข้าพเจ้าคือกระจกเงาแห่งความจริง ท่านมาที่นี่เพื่อเผชิญหน้ากับสัจธรรมหรือความหลง?"
                    
                    send_message(sender_id, reply_text)
                    
    return "OK", 200

def send_message(recipient_id, message_text):
    # ฟังก์ชันส่งข้อความกลับผ่าน Facebook Graph API
    params = {"access_token": PAGE_ACCESS_TOKEN}
    headers = {"Content-Type": "application/json"}
    data = {
        "recipient": {"id": recipient_id},
        "message": {"text": message_text}
    }
    requests.post(
        "https://graph.facebook.com/v21.0/me/messages",
        params=params,
        json=data,
        headers=headers
    )

if __name__ == "__main__":
    # ตั้งค่าพอร์ตสำหรับ Render (พอร์ต 10000)
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
