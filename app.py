import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from google import genai
from chatbot_config import CHATBOT_NAME, SYSTEM_PROMPT

load_dotenv()

app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False

api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key) if api_key else None

MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")


@app.get("/")
def home():
    return render_template("index.html", chatbot_name=CHATBOT_NAME)


@app.post("/chat")
def chat():
    data = request.get_json(silent=True) or {}
    message = str(data.get("message", "")).strip()

    if not message:
        return jsonify({"error": "Please enter a question."}), 400

    if client is None:
        return jsonify({"error": "GEMINI_API_KEY is not configured."}), 500

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=[
                {
                    "role": "user",
                    "parts": [{"text": message}]
                }
            ],
            config={
                "system_instruction": SYSTEM_PROMPT,
                "temperature": 0.4,
            },
        )

        answer = (response.text or "").strip()
        if not answer:
            answer = "I could not generate an answer for that question."

        return jsonify({"answer": answer})
    except Exception as exc:
        return jsonify({"error": f"Unable to process the request: {exc}"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=False)
