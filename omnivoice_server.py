"""
Server nhỏ bọc OmniVoice thành endpoint POST /tts cho pipeline AI-auto-generate-video.

Cách chạy:
    pip install flask
    python omnivoice_server.py

Server sẽ chạy tại http://127.0.0.1:8123
Pipeline sẽ gửi POST /tts với JSON { "text": "..." } và nhận về audio mp3.
"""

from flask import Flask, request, Response
import io
import tempfile
import os

app = Flask(__name__)

print("Đang tải model OmniVoice, vui lòng chờ (lần đầu sẽ tải model từ HuggingFace)...")
from omnivoice import OmniVoice  
model = OmniVoice.from_pretrained("k2-fsa/OmniVoice")
print("Model đã sẵn sàng. Server đang chạy tại http://127.0.0.1:8123")


@app.route("/tts", methods=["POST"])
def tts():
    data = request.get_json(force=True)
    text = data.get("text", "")
    if not text:
        return {"error": "Thiếu 'text' trong request"}, 400

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        tmp_path = tmp.name

    try:
        model.generate(text=text, output=tmp_path)

        with open(tmp_path, "rb") as f:
            audio_bytes = f.read()

        return Response(audio_bytes, mimetype="audio/mpeg")
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8123)