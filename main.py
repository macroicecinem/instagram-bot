import os
import hmac
import hashlib
import json
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# Environment variables
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")
APP_SECRET = os.environ.get("APP_SECRET")
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN", "macroicebot123")

# Trigger keyword
TRIGGER_KEYWORD = "+"

# Messages
COMMENT_REPLY = "📩 To'liq ro'yxat yuborildi! Direct tekshiring 👇"

DM_1 = """Salom! 👋 Ro'yxatni olish uchun avval Instagram sahifamizga obuna bo'ling 👇
@macroice_cinema
Obuna bo'lgach "obuna bo'ldim" deb yozing ✅"""

DM_2 = """So'ragan ro'yxatingiz shu yerda 👇
t.me/MACROICEcinema
Kanalda 92 ta filmning to'liq tartibi bor.
Obuna bo'lishni unutmang! 🎬"""

# Track users:
# "waiting" = DM 1 yuborilgan, javob kutilmoqda
# "done" = DM 2 ham yuborilgan
user_states = {}


def send_dm(user_id, message):
    """Send DM to Instagram user"""
    url = "https://graph.instagram.com/v21.0/me/messages"
    payload = {
        "recipient": {"id": user_id},
        "message": {"text": message},
    }
    params = {"access_token": ACCESS_TOKEN}
    response = requests.post(url, json=payload, params=params)
    print(f"DM to {user_id}: {response.status_code} - {response.text}")
    return response.status_code == 200


def reply_to_comment(comment_id, message):
    """Reply to a comment"""
    url = f"https://graph.instagram.com/v21.0/{comment_id}/replies"
    payload = {"message": message}
    params = {"access_token": ACCESS_TOKEN}
    response = requests.post(url, json=payload, params=params)
    print(f"Comment reply: {response.status_code} - {response.text}")
    return response.status_code == 200


@app.route("/webhook", methods=["GET"])
def verify_webhook():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if mode == "subscribe" and token == VERIFY_TOKEN:
        print("Webhook verified!")
        return challenge, 200
    return "Forbidden", 403


@app.route("/webhook", methods=["POST"])
def handle_webhook():
    # Verify signature
    signature = request.headers.get("X-Hub-Signature-256", "")
    body = request.get_data()
    expected = "sha256=" + hmac.new(
        APP_SECRET.encode(), body, hashlib.sha256
    ).hexdigest()
    if not hmac.compare_digest(signature, expected):
        return "Invalid signature", 403

    data = request.json
    print(f"Webhook: {json.dumps(data, indent=2)}")

    try:
        for entry in data.get("entry", []):
            for change in entry.get("changes", []):
                field = change.get("field")
                value = change.get("value", {})

                # --- COMMENT event ---
                if field == "comments":
                    comment_text = value.get("text", "").strip()
                    commenter_id = value.get("from", {}).get("id")
                    comment_id = value.get("id")

                    print(f"Comment: '{comment_text}' from {commenter_id}")

                    if TRIGGER_KEYWORD in comment_text and commenter_id:
                        if user_states.get(commenter_id) not in ("waiting", "done"):
                            # 1. Comment ga javob
                            if comment_id:
                                reply_to_comment(comment_id, COMMENT_REPLY)
                            # 2. DM 1 yuborish
                            if send_dm(commenter_id, DM_1):
                                user_states[commenter_id] = "waiting"
                                print(f"✅ DM 1 sent to {commenter_id}")

                # --- MESSAGE event (foydalanuvchi javob yozdi) ---
                elif field == "messages":
                    sender_id = value.get("sender", {}).get("id")
                    msg_text = value.get("message", {}).get("text", "")

                    print(f"Message from {sender_id}: '{msg_text}'")

                    # Agar bot o'zi yubormagan bo'lsa
                    my_id = value.get("recipient", {}).get("id")
                    if sender_id == my_id:
                        continue  # bot o'zi yozgan, skip

                    if user_states.get(sender_id) == "waiting":
                        # Nima yozsa ham DM 2 yuborish
                        if send_dm(sender_id, DM_2):
                            user_states[sender_id] = "done"
                            print(f"✅ DM 2 sent to {sender_id}")

    except Exception as e:
        print(f"Error: {e}")

    return jsonify({"status": "ok"}), 200


@app.route("/", methods=["GET"])
def home():
    return "macroiceBot ishlayapti! 🤖", 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)
