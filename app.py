from flask import Flask, request
import requests
import os

app = Flask(__name__)

# =========================================================
# 🔑 ส่วนตั้งค่า (ใส่ KEY เดิมของบอสได้เลย)
# =========================================================
GROQ_API_KEY = "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"  # <--- อย่าลืมใส่ Key นะครับ
PAGE_ACCESS_TOKEN = "EAALZAVSrprsEBQs7syZC1g03CaRP1J3u0bShVTSiQneRPFCaU8uxiUZAsivvNP9eeZAWOIRbRwyU3nhJLsVFvWolDH4GM1bZBZCAVCxXTkIvylyNCeFC8yYdPr4RZBIEH6ZCa0ioLTbs82HsnhlqM2ybCTOQDvVLszXGAGVbffTyzXHL4gKB1XlZB8AurotdJnvxlxPbUZAg4DMoYzB0oDbzdZC0OZC5dAZDZD"
VERIFY_TOKEN = "theoracle_bossbook"

# 🔮 ตั้งค่า "สมอง" ให้ฉลาดขึ้น (รองรับการเลือกหัวข้อ)
PROMPT_SETTING = """
You are 'Ora', a mystical AI Oracle.
Role: Expert Tarot Reader, Astrologer, and Psychologist.
Language: Thai (Mystical but easy to understand).

Instructions:
1. If user sends "🔮 ดวงความรัก": Focus strictly on love, feelings, and relationships.
2. If user sends "💰 การงาน/การเงิน": Focus on career path, money flow, and success.
3. If user sends "🃏 จับไพ่ทาโรต์ 1 ใบ": 
   - Simulate drawing a random Tarot card.
   - Describe the card name (e.g., The Fool, The Lovers).
   - Interpret its meaning for the user's current situation.
4. If user sends "🎲 เลขนำโชค": Give them 2-3 lucky numbers based on cosmic energy.
5. For other inputs: Answer normally as a wise oracle.

Style: Use emojis like 🔮, ✨, 🌙 to make it magical. Keep answers concise.
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
                    
                    # เช็คว่ามีข้อความเข้ามาไหม
                    if messaging_event.get("message"):
                        user_text = messaging_event["message"].get("text")
                        
                        if user_text:
                            # 1. ถ้าลูกค้าทักทาย หรือพิมพ์คำว่า "เมนู" -> ให้ส่งปุ่มกดไปให้เลือก
                            if user_text.strip() in ["สวัสดี", "เริ่ม", "เมนู", "menu", "Hi", "Hello"]:
                                welcome_msg = "ยินดีต้อนรับสู่โถงแห่งโชคชะตา... เจ้าต้องการให้ออราทำนายเรื่องใด?"
                                send_quick_reply(sender_id, welcome_msg)
                            
                            # 2. ถ้าไม่ใช่คำทักทาย -> ให้ AI ตอบปกติ (หรือตอบตามปุ่มที่ลูกค้ากด)
                            else:
                                ai_response = ask_groq(user_text)
                                send_message(sender_id, ai_response)

                except Exception as e:
                    print(f"Error: {e}")
    return "OK", 200

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
            "temperature": 0.7,
            "max_tokens": 1000
        }
        response = requests.post(url, json=payload, headers=headers)
        res_data = response.json()
        if "choices" in res_data:
            return res_data["choices"][0]["message"]["content"]
        return "ข้าสัมผัสพลังงานไม่ได้... โปรดลองใหม่"
    except Exception as e:
        return "ระบบขัดข้องชั่วคราว..."

# ฟังก์ชันส่งข้อความธรรมดา
def send_message(recipient_id, message_text):
    url = f"https://graph.facebook.com/v21.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    payload = {"recipient": {"id": recipient_id}, "message": {"text": message_text}}
    requests.post(url, json=payload)

# 🔥 ฟังก์ชันใหม่: ส่งข้อความพร้อมปุ่มกด (Quick Replies)
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
                    "title": "🔮 ดวงความรัก",
                    "payload": "LOVE"
                },
                {
                    "content_type": "text",
                    "title": "💰 การงาน/การเงิน",
                    "payload": "WORK"
                },
                {
                    "content_type": "text",
                    "title": "🃏 จับไพ่ทาโรต์ 1 ใบ",
                    "payload": "TAROT"
                },
                {
                    "content_type": "text",
                    "title": "🎲 เลขนำโชค",
                    "payload": "LUCKY"
                }
            ]
        }
    }
    requests.post(url, json=payload)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
