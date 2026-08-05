import os

from flask import Flask, jsonify, render_template


app = Flask(__name__)


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/api/client-config")
def client_config():
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    return jsonify(
        {
            "apiKey": api_key,
            "model": os.environ.get(
                "GEMINI_LIVE_MODEL", "gemini-3.1-flash-live-preview"
            ),
            "configured": bool(api_key),
        }
    )


@app.get("/health")
def health():
    return jsonify({"ok": True})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="127.0.0.1", port=port, debug=True)
