import os
import json
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN", "macroicebot123")
MY_ACCOUNT_ID = "17841444255173953"

VIDEO_KEYWORDS = {
    "18233163412315422": {
        "minion": "Multifilmni O'zbek tilida ko'rish uchun sahifamiz biosidagi havola ustiga bosib \"DodaPlay\" ilovasini yuklang.",
        "mnion": "Multifilmni O'zbek tilida ko'rish uchun sahifamiz biosidagi havola ustiga bosib \"DodaPlay\" ilovasini yuklang.",
        "minon": "Multifilmni O'zbek tilida ko'rish uchun sahifamiz biosidagi havola ustiga bosib \"DodaPlay\" ilovasini yuklang.",
        "миньон": "Multifilmni O'zbek tilida ko'rish uchun sahifamiz biosidagi havola ustiga bosib \"DodaPlay\" ilovasini yuklang.",
        "минион": "Multifilmni O'zbek tilida ko'rish uchun sahifamiz biosidagi havola ustiga bosib \"DodaPlay\" ilovasini yuklang.",
    },
    "17874389535525083": {
        "qiz": "Obsessiya filmini O'zbek tilida ko'rish uchun sahifamiz biosidagi havola ustiga bosib \"DodaPlay\" ilovasini yuklang.",
        "киз": "Obsessiya filmini O'zbek tilida ko'rish uchun sahifamiz biosidagi havola ustiga bosib \"DodaPlay\" ilovasini yuklang.",
        "qz": "Obsessiya filmini O'zbek tilida ko'rish uchun sahifamiz biosidagi havola ustiga bosib \"DodaPlay\" ilovasini yuklang.",
        "kiz": "Obsessiya filmini O'zbek tilida ko'rish uchun sahifamiz biosidagi havola ustiga bosib \"DodaPlay\" ilovasini yuklang.",
    },
    "18146536351513830": {
        "it": "Avval sahifamga obuna bo'ling. Filmlarni O'zbek tilida ko'rish uchun sahifamiz biosidagi havola ustiga bosib \"DodaPlay\" ilovasini yuklang.",
    },
    "18103363679035943": {
        "qora": "Avval sahifamga obuna bo'ling. Filmlarni O'zbek tilida ko'rish uchun sahifamiz biosidagi havola ustiga bosib \"DodaPlay\" ilovasini yuklang.",
    },
    "18133502506596652": {
        "serial": "Serialni O'zbek tilida ko'rish uchun sahifamiz biosidagi havola ustiga bosib \"DodaPlay\" ilovasini yuklang.",
    },
    "18078665936432123": {
        "+": "🎬 Avval sahifamga obuna bo'ling va biodagi macroice.uz havolasiga bosib Telegram kanalimizdan filmlarni ko'ring!",
    },
    "17994825497975971": {
        "temir": "🎬 Avval sahifamga obuna bo'ling va biodagi macroice.uz havolasiga bosib Telegram kanalimizdan Temir Odam filmini ko'ring!",
    },
    "18473768101096135": {
        "kapitan": "🎬 Avval sahifamga obuna bo'ling va biodagi macroice.uz havolasiga bosib Telegram kanalimizdan Qasoskorlar filmini ko'ring!",
        "capitan": "🎬 Avval sahifamga obuna bo'ling va biodagi macroice.uz havolasiga bosib Telegram kanalimizdan Qasoskorlar filmini ko'ring!",
        "captian": "🎬 Avval sahifamga obuna bo'ling va biodagi macroice.uz havolasiga bosib Telegram kanalimizdan Qasoskorlar filmini ko'ring!",
        "капитан": "🎬 Avval sahifamga obuna bo'ling va biodagi macroice.uz havolasiga bosib Telegram kanalimizdan Qasoskorlar filmini ko'ring!",
    },
    "18253266406306179": {
        "tahlil": "🎬 Avval sahifamga obuna bo'ling va biodagi macroice.uz havolasiga bosib YouTube kanalimizdan to'liq reaksiya va tahlil videoni ko'ring!",
        "тахлил": "🎬 Avval sahifamga obuna bo'ling va biodagi macroice.uz havolasiga bosib YouTube kanalimizdan to'liq reaksiya va tahlil videoni ko'ring!",
        "qachon chiqadi": "📅 31-iyuldan rus va ingliz tilida, o'zbek tilida esa 6-avgustdan kinoteatrlarda ko'rishingiz mumkin! Sahifamga obuna bo'ling! 🎬",
        "qachon": "📅 31-iyuldan rus va ingliz tilida, o'zbek tilida esa 6-avgustdan kinoteatrlarda ko'rishingiz mumkin! Sahifamga obuna bo'ling! 🎬",
    },
    "18475932589097936": {
        "+": "📩 To'liq ro'yxat uchun biodagi telegram kanalimizga o'ting.",
        "marvel": "📩 To'liq Marvel ro'yxati uchun biodagi telegram kanalimizga o'ting.",
    },
    "18096396052932962": {
        "+": "Kinoni olish uchun avval sahifamizga obuna bo'ling va biodagi Telegram kanalimizga o'ting! 🎬",
    },
    "18093412184217647": {
        "youtube": "YouTube videoni ko'rish uchun profil biosidagi havolaga bosing! 👆🔗",
    },
    "17973591039060965": {
        "+": "🎬 Qasoskorlar 5 syujeti haqida YouTube videoni ko'rish uchun profil shapkasidagi havolaga bosing!",
    },
    "18101827772108974": {
        "+": "Kino va seriallarni ko'rish uchun biodagi havola orqali telegram kanalimizga o'ting!",
    },
    "17887646772396519": {
        "temir": "Filmni ko'rish uchun profilim shapkasidagi havolaga bosib telegram kanalimizga o'ting👈",
    },
}

processed_ids = set()


def reply_to_comment(comment_id, message):
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
        return challenge, 200
    return "Forbidden", 403


@app.route("/webhook", methods=["POST"])
def handle_webhook():
    data = request.json
    print(f"Webhook: {json.dumps(data, indent=2)}")

    try:
        for entry in data.get("entry", []):
            for change in entry.get("changes", []):
                field = change.get("field")
                value = change.get("value", {})

                if field == "comments":
                    comment_id = value.get("id")
                    comment_text = value.get("text", "").strip().lower()
                    commenter_id = value.get("from", {}).get("id")
                    media_id = value.get("media", {}).get("id")
                    parent_id = value.get("parent_id")

                    if commenter_id == MY_ACCOUNT_ID:
                        continue

                    if parent_id:
                        print(f"⏭️ Skipped reply comment from {commenter_id}")
                        continue

                    if comment_id in processed_ids:
                        continue
                    processed_ids.add(comment_id)

                    print(f"Comment: '{comment_text}' from {commenter_id}, media: {media_id}")

                    keywords = VIDEO_KEYWORDS.get(media_id, {})
                    if not keywords:
                        print(f"⏭️ No keywords configured for media {media_id}")
                        continue

                    for keyword, reply in keywords.items():
                        if keyword in comment_text:
                            reply_to_comment(comment_id, reply)
                            print(f"✅ Reply sent for keyword '{keyword}' to {commenter_id}")
                            break

    except Exception as e:
        print(f"Error: {e}")

    return jsonify({"status": "ok"}), 200


@app.route("/", methods=["GET"])
def home():
    return "macroiceBot ishlayapti! 🤖", 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)
