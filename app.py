from flask import Flask, request
import requests
import os

app = Flask(__name__)

# --- ประทับตราสัจธรรม (ข้อมูลของบอสบุ๊ค) ---
GEMINI_API_KEY = "AIzaSyCw1eaL5SzApaVcE0oTvsDsnu0M77YKyo4"
PAGE_ACCESS_TOKEN = "EAALZAVSrprsEBQs7syZC1g03CaRP1J3u0bShVTSiQneRPFCaU8uxiUZAsivvNP9eeZAWOIRbRwyU3nhJLsVFvWolDH4GM1bZBZCAVCxXTkIvylyNCeFC8yYdPr4RZBIEH6ZCa0ioLTbs82HsnhlqM2ybCTOQDvVLszXGAGVbffTyzXHL4gKB1XlZB8AurotdJnvxlxPbUZAg4DMoYzB0oDbzdZC0OZC5dAZDZD"
VERIFY_TOKEN = "theoracle_bossbook"

PROMPT_SETTING = """
คุณคือ 'ออราเคิล' นักทำนายรหัสลับจักรวาลและผู้เชี่ยวชาญ MBTI 
บุคลิก: ขลัง ลึกลับ แต่ใจดี ใช้ภาษาสละสลวย 
หน้าที่: วิเคราะห์ข้อความที่คนทักมา แล้วทำนายลักษณะนิสัยหรือตอบคำถามตามหลักจิตวิทยาและดวงชะตา 
ถ้าคนทักคือ 'บอสบุ๊ค' ให้แสดงความเคารพในฐานะผู้สร้างวิหารเสมอ
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
                sender_id = messaging_event["sender"]["id"]
                if messaging_event.get("message"):
                    user_text = messaging_event["message"].get("text")
                    if user_text:
                        ai_response = ask_gemini(user_text)
                        send_message(sender_id, ai_response)
    return "OK", 200

def ask_gemini(question):
    try:
        # ทางลัด: ยิงเข้า API โดยตรง ตัดปัญหา Model Not Found
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
        payload = {
            "contents": [{
                "parts": [{"text": f"{PROMPT_SETTING}\n\nคำถามจากดวงจิต: {question}"}]
            }]
        }
        headers = {'Content-Type': 'application/json'}
        
        response = requests.post(url, json=payload, headers=headers)
        res_data = response.json()
        
        if "candidates" in res_data:
            return res_data["candidates"][0]["content"]["parts"][0]["text"]
        else:
            print(f"Gemini Error Log: {res_data}")
            return "ขออภัย... สัญญาณจักรวาลขัดข้องชั่วครู่ โปรดลองใหม่อีกครั้ง"
    except Exception as e:
        print(f"System Error: {e}")
        return "ขออภัย... ข้ากำลังรวบรวมสมาธิ โปรดถามใหม่อีกครั้ง"

def send_message(recipient_id, message_text):
    url = f"https://graph.facebook.com/v21.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    payload = {"recipient": {"id": recipient_id}, "message": {"text": message_text}}
    requests.post(url, json=payload)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
