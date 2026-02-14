from flask import Flask, request
import requests
import os
import random

app = Flask(__name__)

# =========================================================
# 🔑 ส่วนตั้งค่า (ใส่ KEY ของบอส)
# =========================================================
GROQ_API_KEY = "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"
PAGE_ACCESS_TOKEN = "EAALZAVSrprsEBQs7syZC1g03CaRP1J3u0bShVTSiQneRPFCaU8uxiUZAsivvNP9eeZAWOIRbRwyU3nhJLsVFvWolDH4GM1bZBZCAVCxXTkIvylyNCeFC8yYdPr4RZBIEH6ZCa0ioLTbs82HsnhlqM2ybCTOQDvVLszXGAGVbffTyzXHL4gKB1XlZB8AurotdJnvxlxPbUZAg4DMoYzB0oDbzdZC0OZC5dAZDZD"
VERIFY_TOKEN = "theoracle_bossbook"

# 🃏 คลังภาพไพ่ยิปซี (Rider-Waite) - เอามาแค่บางส่วนเพื่อเป็นตัวอย่าง
TAROT_DECK = {
    "The Fool": "https://upload.wikimedia.org/wikipedia/commons/9/90/RWS_Tarot_00_Fool.jpg",
    "The Magician": "https://upload.wikimedia.org/wikipedia/commons/d/de/RWS_Tarot_01_Magician.jpg",
    "The High Priestess": "https://upload.wikimedia.org/wikipedia/commons/8/88/RWS_Tarot_02_High_Priestess.jpg",
    "The Empress": "https://upload.wikimedia.org/wikipedia/commons/d/d2/RWS_Tarot_03_Empress.jpg",
    "The Emperor": "https://upload.wikimedia.org/wikipedia/commons/c/c3/RWS_Tarot_04_Emperor.jpg",
    "The Lovers": "https://upload.wikimedia.org/wikipedia/commons/3/3a/TheLovers.jpg",
    "The Chariot": "https://upload.wikimedia.org/wikipedia/commons/9/9b/RWS_Tarot_07_Chariot.jpg",
    "Strength": "https://upload.wikimedia.org/wikipedia/commons/f/f5/RWS_Tarot_08_Strength.jpg",
    "The Hermit": "https://upload.wikimedia.org/wikipedia/commons/4/4d/RWS_Tarot_09_Hermit.jpg",
    "Wheel of Fortune": "https://upload.wikimedia.org/wikipedia/commons/3/3c/RWS_Tarot_10_Wheel_of_Fortune.jpg",
    "Death": "https://upload.wikimedia.org/wikipedia/commons/d/d7/RWS_Tarot_13_Death.jpg",
    "The Sun": "https://upload.wikimedia.org/wikipedia/commons/1/17/RWS_Tarot_19_Sun.jpg",
    "The Moon": "https://upload.wikimedia.org/wikipedia/commons/7/7f/RWS_Tarot_18_Moon.jpg",
    "The Star": "https://upload.wikimedia.org/wikipedia/commons/d/db/RWS_Tarot_17_Star.jpg",
    "The World": "https://upload.wikimedia.org/wikipedia/commons/f/ff/RWS_Tarot_21_World.jpg"
}

PROMPT_SETTING = """
You are 'Ora', a mystical Tarot Reader.
Language: Thai.
Role: Interpret the specific Tarot card provided by the user.
Style: Mystical, Insightful, Encouraging.
Format:
1. Name of Card (Thai translation)
2. General Meaning (1 sentence)
3. Advice for the user (1-2 sentences)
"""

@app.route("/", methods=["GET"])
def verify():
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.verify_token") == VERIFY_TOKEN:
        return request.args.get("hub.challenge"), 200
    return "Forbidden", 403

@app.route("/", methods=["POST"])
def webhook():
    data = request.json
    if data.get("object") == "page":
        for entry in data.get("entry"):
            for messaging_event in entry.get("messaging"):
                try:
                    sender_id = messaging_event["sender"]["id"]
                    
                    if messaging_event.get("message"):
                        user_text = messaging_event["message"].get("text")
                        
                        if user_text:
                            # 1. เช็กว่าลูกค้ากดปุ่ม "เปิดไพ่" หรือไม่
                            if "เปิดไพ่" in user_text or "Tarot" in user_text:
                                handle_tarot_reading(sender_id)
                            
                            # 2. ถ้าทักมาทั่วไป ให้ส่งปุ่มเมนู
                            elif user_text in ["เมนู", "สวัสดี", "เริ่ม", "menu"]:
                                send_quick_reply(sender_id, "🔮 โถงแห่งโชคชะตาเปิดแล้ว... เลือกสิ่งที่เจ้าปรารถนา")
                            
                            # 3. คุยเล่นทั่วไป
                            else:
                                ai_response = ask_groq(f"User says: {user_text}")
                                send_message(sender_id, ai_response)

                except Exception as e:
                    print(f"Error: {e}")
    return "OK", 200

# 🔥 ฟังก์ชันใหม่: สุ่มไพ่ + ส่งรูปภาพ + ส่งคำทำนาย
def handle_tarot_reading(recipient_id):
    # 1. สุ่มไพ่จากสำรับ
    card_name, card_url = random.choice(list(TAROT_DECK.items()))
    
    # 2. ส่งรูปไพ่ไปก่อน (ความว้าวอยู่ที่นี่!)
    send_image(recipient_id, card_url)
    
    # 3. ให้ AI ทำนายไพ่ใบนั้น
    prediction = ask_groq(f"ลูกค้าเปิดได้ไพ่: {card_name}. ช่วยทำนายความหมายสั้นๆ และให้คำแนะนำหน่อย")
    
    # 4. ส่งคำทำนายตามไป
    send_message(recipient_id, f"🎴 ไพ่ที่เจ้าได้คือ: {card_name}\n\n{prediction}")

def ask_groq(question):
    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": PROMPT_SETTING},
                {"role": "user", "content": question}
            ],
            "temperature": 0.7
        }
        response = requests.post(url, json=payload, headers=headers)
        res_data = response.json()
        if "choices" in res_data:
            return res_data["choices"][0]["message"]["content"]
        return "หมอกแห่งกาลเวลาบดบัง... โปรดลองใหม่"
    except Exception:
        return "ระบบขัดข้องชั่วคราว"

def send_message(recipient_id, message_text):
    url = f"https://graph.facebook.com/v21.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    payload = {"recipient": {"id": recipient_id}, "message": {"text": message_text}}
    requests.post(url, json=payload)

# 📸 ฟังก์ชันส่งรูปภาพ (Image Sender)
def send_image(recipient_id, image_url):
    url = f"https://graph.facebook.com/v21.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    payload = {
        "recipient": {"id": recipient_id},
        "message": {
            "attachment": {
                "type": "image",
                "payload": {
                    "url": image_url, 
                    "is_reusable": True
                }
            }
        }
    }
    requests.post(url, json=payload)

def send_quick_reply(recipient_id, message_text):
    url = f"https://graph.facebook.com/v21.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    payload = {
        "recipient": {"id": recipient_id},
        "messaging_type": "RESPONSE",
        "message": {
            "text": message_text,
            "quick_replies": [
                {
                    "content_type": "text",
                    "title": "🎴 เปิดไพ่เสี่ยงทาย",
                    "payload": "TAROT"
                },
                {
                    "content_type": "text",
                    "title": "💬 คุยเล่นกับโอรา",
                    "payload": "CHAT"
                }
            ]
        }
    }
    requests.post(url, json=payload)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
