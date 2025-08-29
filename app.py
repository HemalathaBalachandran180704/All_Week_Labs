from flask import Flask, request, jsonify, render_template_string, redirect
import csv, os

app = Flask(__name__)
DATA_FILE = "data.csv"
HEADERS = ["serial", "name", "email"]
LAST_PICKED = None

def make_csv():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=HEADERS)
            writer.writeheader()

def load_all():
    make_csv()
    with open(DATA_FILE, newline="") as f:
        return list(csv.DictReader(f))

def find_serial(num):
    for row in load_all():
        if row["serial"] == str(num):
            return row
    return None

def save_or_update(new_row):
    rows = load_all()
    found = False
    for i, r in enumerate(rows):
        if r["serial"] == new_row["serial"]:
            rows[i] = new_row
            found = True
            break
    if not found:
        rows.append(new_row)
    with open(DATA_FILE, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=HEADERS)
        writer.writeheader()
        writer.writerows(rows)

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>CSV Form</title>
    <script>
        setTimeout(function(){
            window.location.href = "/?index={{next_index}}";
        }, 5000);
    </script>
    <style>
        table { border-collapse: collapse; margin-top: 15px; }
        th, td { border: 1px solid black; padding: 6px; text-align: center; }
        th { background: #f2f2f2; }
    </style>
</head>
<body>
    <h2>Add / Update Entry</h2>
    <form method="post" action="/submit">
        Serial No: <input name="serial" required><br><br>
        Full Name: <input name="name" required><br><br>
        Email ID: <input name="email" required><br><br>
        <button type="submit">Save</button>
    </form>

    <h2>Selected Record (Auto refreshes every 5 sec)</h2>
    {% if selected %}
    <table>
        <tr><th>Serial</th><th>Name</th><th>Email</th></tr>
        <tr>
            <td>{{selected.serial}}</td>
            <td>{{selected.name}}</td>
            <td>{{selected.email}}</td>
        </tr>
    </table>
    {% else %}
    <p>No record selected</p>
    {% endif %}
</body>
</html>
"""

TABLE_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>All Records</title>
    <style>
        table { border-collapse: collapse; margin-top: 20px; }
        th, td { border: 1px solid black; padding: 6px; text-align: center; }
        th { background: #ddd; }
    </style>
</head>
<body>
    <h2>All Records in CSV</h2>
    <table>
        <tr>
            {% for h in headers %}
                <th>{{h}}</th>
            {% endfor %}
        </tr>
        {% for row in rows %}
        <tr>
            {% for h in headers %}
                <td>{{row[h]}}</td>
            {% endfor %}
        </tr>
        {% endfor %}
    </table>
</body>
</html>
"""

@app.route("/")
def home():
    rows = load_all()
    total = len(rows)
    if total == 0:
        selected = None
        next_index = 0
    else:
        current_index = request.args.get("index", default=0, type=int)
        current_index = current_index % total
        selected = rows[current_index]
        next_index = (current_index + 1) % total

    return render_template_string(HTML_PAGE, selected=selected, next_index=next_index)

@app.route("/all")
def all_json():
    return jsonify(load_all())

@app.route("/all_table")
def all_table():
    rows = load_all()
    return render_template_string(TABLE_PAGE, rows=rows, headers=HEADERS)

@app.route("/submit", methods=["POST"])
def submit():
    save_or_update({
        "serial": request.form["serial"],
        "name": request.form["name"],
        "email": request.form["email"]
    })
    return redirect("/")

@app.route("/get/<serial>")
def get_record(serial):
    row = find_serial(serial)
    if not row:
        return jsonify({"error":"not found"}), 404
    return jsonify(row)

if __name__ == "__main__":
    make_csv()
    app.run(debug=True)
