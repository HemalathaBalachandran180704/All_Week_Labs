from flask import Flask, jsonify, render_template
import csv

app = Flask(__name__)

# Load CSV data
with open("users.csv", newline="") as f:
    reader = csv.DictReader(f)
    users = list(reader)

index = {"pos": 0}

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/next")
def next_user():
    if index["pos"] >= len(users):
        index["pos"] = 0
    user = users[index["pos"]]
    index["pos"] += 1
    return jsonify(user)

if __name__ == "__main__":
    app.run(debug=False)
