from flask import Flask, request, jsonify, render_template_string, redirect
import csv, os
 
app = Flask(__name__)
CSV_FILE = "data.csv"
FIELDS = ["serial", "name", "email"]
LAST_SELECTED = None
 
def ensure_csv():
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=FIELDS)
            w.writeheader()
 
def read_all():
    ensure_csv()
    with open(CSV_FILE, newline="") as f:
        return list(csv.DictReader(f))
 
def find_by_serial(s):
    for row in read_all():
        if row["serial"] == str(s):
            return row
    return None
 
def upsert(row):
    rows = read_all()
    updated = False
    for i, r in enumerate(rows):
        if r["serial"] == row["serial"]:
            rows[i] = row
            updated = True
            break
    if not updated:
        rows.append(row)
    with open(CSV_FILE, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)
 
HTML = """
<!DOCTYPE html>
<html>
<head>
<title>CSV Form</title>
<meta http-equiv="refresh" content="15; URL='/?index={{next_index}}'">
</head>
<body>
<h2>Enter Data</h2>
<form method="post" action="/submit">
    Serial: <input name="serial" required><br><br>
    Name: <input name="name" required><br><br>
    Email: <input name="email" required><br><br>
<button type="submit">Submit</button>
</form>
 
  <h2>Selected Record </h2>
  {% if selected %}
<p><b>Serial:</b> {{selected.serial}} <br>
<b>Name:</b> {{selected.name}} <br>
<b>Email:</b> {{selected.email}}</p>
  {% else %}
<p>No record selected yet</p>
  {% endif %}
</body>
</html>
"""
 
@app.route("/")
def index():
    rows = read_all()
    total = len(rows)
    if total == 0:
        selected = None
        next_index = 0
    else:
        current_index = request.args.get("index", default=0, type=int)
        current_index = current_index % total
        selected = rows[current_index]
        next_index = (current_index + 1) % total
 
    return render_template_string(HTML, selected=selected, next_index=next_index)
 
@app.route("/all")
def all_data():
    rows = read_all()
    return jsonify(rows)
 
@app.route("/submit", methods=["POST"])
def submit():
    upsert({
        "serial": request.form["serial"],
        "name": request.form["name"],
        "email": request.form["email"]
    })
    return redirect("/")
 
@app.route("/select/<serial>")
def select(serial):
    global LAST_SELECTED
    LAST_SELECTED = serial
    row = find_by_serial(serial)
    if not row:
        return jsonify({"error": "not found"}), 404
    return jsonify(row)  # also return full record to curl
 
@app.route("/get/<serial>")
def get_serial(serial):
    row = find_by_serial(serial)
    if not row:
        return jsonify({"error":"not found"}), 404
    return jsonify(row)
 
if __name__ == "__main__":
    ensure_csv()
    app.run(debug=True)