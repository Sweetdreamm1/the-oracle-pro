from flask import Flask, request
import requests
import os
import google.generativeai as genai

app = Flask(__name__)

# --- ประทับตราสัจธรรม ---
GEMINI_API_KEY = "AIzaSyCw1eaL5SzApaVcE0oTvsDsnu0M77YKyo4"
PAGE_ACCESS_TOKEN = "EAALZAVSrprsEBQs7syZC1g03CaRP1J3u0bShVTSiQneRPFCaU8uxiUZAsivvNP9eeZAWOIRbRwyU3nhJLsVFvWolDH4GM1bZBZCAVCxXTkIvylyNCeFC8yYdPr4RZBIEH6ZCa0ioLTbs82HsnhlqM2ybCTOQDvVLszXGAGVbffTyzXHL4gKB1XlZB8AurotdJnvxlxPbUZAg4DMoYzB0oDbzdZC0OZC5dAZDZD"
VERIFY_TOKEN = "theoracle_bossbook"

# ตั้งค่าพื้นฐาน (Configuration)
genai.configure(api_key=GEMINI_API_KEY)

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
                        # อัญเชิญพลัง Gemini
                        ai_response = ask_gemini(user_text)
                        send_message(sender_id, ai_response)
    return "OK", 200

def ask_gemini(question):
    try:
        # ย้ายมาเรียกใช้ข้างในนี้เพื่อเลี่ยง Error 404 ตอนเริ่มระบบ
       model = genai.GenerativeModel('gemini-1.5-pro')
        response = model.generate_content(f"{PROMPT_SETTING}\n\nคำถามจากดวงจิต: {question}")
        return response.text
    except Exception as e:
        print(f"Error Gemini Details: {e}")
        # แผนสำรอง: ถ้า flash มีปัญหา ให้ลองใช้รุ่นดั้งเดิม
        try:
            model_alt = genai.GenerativeModel('gemini-pro')
            response = model_alt.generate_content(f"{PROMPT_SETTING}\n\nคำถามจากดวงจิต: {question}")
            return response.text
        except:
            return "ขออภัย... สัญญาณจักรวาลขัดข้องชั่วครู่ โปรดลองใหม่อีกครั้ง"

def send_message(recipient_id, message_text):
    url = f"https://graph.facebook.com/v21.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    payload = {"recipient": {"id": recipient_id}, "message": {"text": message_text}}
    try:
        r = requests.post(url, json=payload)
        print(f"Facebook Response: {r.status_code} - {r.text}")
    except Exception as e:
        print(f"Error Sending to Facebook: {e}")

if __name__ == "__main__":
    # มั่นใจว่า Port จะถูกดึงจาก Render อย่างถูกต้อง
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
