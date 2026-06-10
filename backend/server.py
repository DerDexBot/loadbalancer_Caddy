import os
import time
import socket
import logging
from flask import Flask, jsonify

# Flask-/Werkzeug-Access-Logs deaktivieren (sonst doppelte Ausgabe)
logging.getLogger("werkzeug").setLevel(logging.ERROR)

app = Flask(__name__)

SERVER_ID = os.environ.get("SERVER_ID", socket.gethostname())
start_time = time.time()
request_count = 0


@app.route("/")
def index():
    global request_count
    request_count += 1
    return jsonify({
        "server":           SERVER_ID,
        "requests_handled": request_count,
        "uptime_seconds":   round(time.time() - start_time, 2),
        "timestamp":        time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    })


@app.route("/health")
def health():
    return jsonify({"status": "ok", "server": SERVER_ID}), 200


if __name__ == "__main__":
    print(f"[{SERVER_ID}] Startet auf Port 8080 ...")
    app.run(host="0.0.0.0", port=8080)
