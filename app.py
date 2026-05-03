from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return "CIS 4930 Cumulative Project: Flask app is running!"

@app.route("/health")
def health():
    return jsonify({"status": "ok"})

@app.route("/info")
def info():
    return jsonify({
        "project": "CIS 4930 Cumulative Project",
        "tools": ["GitHub", "Jenkins", "Docker", "Docker Compose", "Flask", "Nginx", "Pytest"],
        "purpose": "Demonstrate a simple automated DevOps workflow"
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)