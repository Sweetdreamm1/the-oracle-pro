from flask import Flask, request
import requests
import os
import google.generativeai as genai

app = Flask(__name__)

# --- ประทับตราสัจธรรม (ใส่ข้อมูลของบอสตรงนี้) ---
GEMINI_API_KEY = "AIzaSyAltPoRUQ8X73oNbHPt8tFWnea5iYweHms"
PAGE_ACCESS_TOKEN = "EAALZAVSrprsEBQtVFdQlUq2j3TVI8gMI6OMKjArlz9zCW1HvwfSrtcj80pPcNdNOQaXFGkLULvg6Pn0JCFCwSqsjVRvYyKb7ifoOwZArMtuUlTaNKV7pG2R1ZCHLkjHf7DnEDZAR5FslGcdJMuKWu4myPy417GOKuap5VAqpSe7gG7XmgvZB4mbxwjAMXQRfCTgQ86VwXAhBWZAcERNBrQDsqGcAZDZD"
VERIFY_TOKEN = "theoracle_bossbook"

# ตั้งค่าสมอง Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# คำสั่งศักดิ์สิทธิ์ (System Prompt) - บอสแก้บุคลิกตรงนี้ได้เลย
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
                        # อัญเชิญ Gemini มาคิดหาคำตอบ
                        ai_response = ask_gemini(user_text)
                        send_message(sender_id, ai_response)
    return "OK", 200

def ask_gemini(question):
    try:
        response = model.generate_content(f"{PROMPT_SETTING}\n\nคำถามจากดวงจิต: {question}")
        return response.text
    except Exception as e:
        print(f"Error Gemini: {e}")
        return "ขออภัย... สัญญาณจักรวาลขัดข้องชั่วครู่ โปรดลองใหม่อีกครั้ง"

def send_message(recipient_id, message_text):
    url = f"https://graph.facebook.com/v21.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    payload = {"recipient": {"id": recipient_id}, "message": {"text": message_text}}
    requests.post(url, json=payload)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
