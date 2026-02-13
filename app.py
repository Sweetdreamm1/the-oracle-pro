from flask import Flask, request
import requests
import os

app = Flask(__name__)

# =========================================================
# 🔒 ส่วนตั้งค่ากุญแจ (สำคัญมาก!)
# =========================================================

# 1. ใส่ API KEY ของ Groq ที่บอสไปกดสร้างมา (ขึ้นต้นด้วย gsk_...)
# *ตอน Commit ถ้า GitHub เตือนเรื่องความปลอดภัย ให้กด "Allow secret" ได้เลยครับ*
GROQ_API_KEY = "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"

# 2. ข้อมูลเดิมของ Facebook (บอสไม่ต้องแก้ ผมใส่ให้ครบแล้ว)
PAGE_ACCESS_TOKEN = "EAALZAVSrprsEBQs7syZC1g03CaRP1J3u0bShVTSiQneRPFCaU8uxiUZAsivvNP9eeZAWOIRbRwyU3nhJLsVFvWolDH4GM1bZBZCAVCxXTkIvylyNCeFC8yYdPr4RZBIEH6ZCa0ioLTbs82HsnhlqM2ybCTOQDvVLszXGAGVbffTyzXHL4gKB1XlZB8AurotdJnvxlxPbUZAg4DMoYzB0oDbzdZC0OZC5dAZDZD"
VERIFY_TOKEN = "theoracle_bossbook"

# 3. ตั้งค่าตัวตนของ "โอรา" (ออราเคิล)
PROMPT_SETTING = """
You are 'Ora' (The Oracle), a mysterious and wise AI assistant for 'Boss Book'.
Character: Mystical, insightful, kind but slightly enigmatic.
Role: Expert in MBTI, psychology, and destiny readings.
Language: Reply in Thai language mostly. Use beautiful, respectful words.
Instruction: Keep answers concise (under 3-4 sentences) unless asked for details.
If asked who created you, answer: "ท่านบอสบุ๊ค ผู้กุมความลับแห่งจักรวาล (Boss Book)"
"""

# =========================================================
# ⚙️ ระบบการทำงาน (ห้ามแก้ไขส่วนนี้ถ้าไม่จำเป็น)
# =========================================================

@app.route("/", methods=["GET"])
def verify():
    # ยืนยันตัวตนกับ Facebook
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.verify_token") == VERIFY_TOKEN:
        return request.args.get("hub.challenge"), 200
    return "Forbidden", 403

@app.route("/", methods=["POST"])
def webhook():
    # รับข้อความจากแชท
    data = request.json
    if data.get("object") == "page":
        for entry in data.get("entry"):
            for messaging_event in entry.get("messaging"):
                try:
                    sender_id = messaging_event["sender"]["id"]
                    if messaging_event.get("message"):
                        user_text = messaging_event["message"].get("text")
                        if user_text:
                            # ส่งให้ Groq ช่วยคิดคำตอบ
                            ai_response = ask_groq(user_text)
                            # ส่งคำตอบกลับไปหาคนทัก
                            send_message(sender_id, ai_response)
                except Exception as e:
                    print(f"Webhook Error: {e}")
    return "OK", 200

def ask_groq(question):
    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            # ใช้โมเดล Llama 3.3 ตัวล่าสุด (แก้ปัญหา Model Decommissioned)
            "model": "llama-3.3-70b-versatile", 
            "messages": [
                {"role": "system", "content": PROMPT_SETTING},
                {"role": "user", "content": question}
            ],
            "temperature": 0.7, # ระดับความคิดสร้างสรรค์ (0.7 กำลังดี)
            "max_tokens": 1024
        }
        
        response = requests.post(url, json=payload, headers=headers)
        res_data = response.json()
        
        # ดึงคำตอบออกมาจาก JSON
        if "choices" in res_data:
            return res_data["choices"][0]["message"]["content"]
        else:
            print(f"Groq API Error Detail: {res_data}")
            return "ข้าสัมผัสได้ถึงคลื่นรบกวนในจักรวาล... (ระบบขัดข้องชั่วคราว โปรดลองใหม่)"
            
    except Exception as e:
        print(f"Connection Error: {e}")
        return "ข้ากำลังรวบรวมสมาธิ... โปรดถามใหม่อีกครั้ง"

def send_message(recipient_id, message_text):
    # ฟังก์ชันส่งข้อความกลับเข้า Messenger
    url = f"https://graph.facebook.com/v21.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    payload = {
        "recipient": {"id": recipient_id}, 
        "message": {"text": message_text}
    }
    try:
        r = requests.post(url, json=payload)
        if r.status_code != 200:
            print(f"Facebook Send Error: {r.text}")
    except Exception as e:
        print(f"Network Error sending to FB: {e}")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
