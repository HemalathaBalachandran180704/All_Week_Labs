# from flask import Flask, render_template, request
# import sqlite3
# from models.text_to_sql import TextToSQL

# app = Flask(__name__)
# model = TextToSQL()

# # DB connection
# conn = sqlite3.connect("test.db", check_same_thread=False)
# cursor = conn.cursor()

# def execute_sql(query):
#     try:
#         cursor.execute(query)
#         return cursor.fetchall()
#     except Exception as e:
#         return [("Error", str(e))]

# @app.route("/", methods=["GET", "POST"])
# def home():
#     sql_query, results = None, None
#     if request.method == "POST":
#         question = request.form["question"]
#         sql_query = model.predict(question)
#         results = execute_sql(sql_query)
#     return render_template("index.html", sql_query=sql_query, results=results)

# if __name__ == "__main__":

#     app.run(debug=True)

from flask import Flask, render_template, request
import sqlite3
from models.text_to_sql import TextToSQL

app = Flask(__name__)
model = TextToSQL()

# DB connection
conn = sqlite3.connect("test.db", check_same_thread=False)
cursor = conn.cursor()

def execute_sql(query):
    try:
        cursor.execute(query)
        results = cursor.fetchall()
        column_names = [description[0] for description in cursor.description] if cursor.description else []
        return column_names, results
    except Exception as e:
        return ["Error", "Details"], [("Error", str(e))]

@app.route("/", methods=["GET", "POST"])
def home():
    sql_query, results, column_names = None, None, None
    if request.method == "POST":
        question = request.form["question"]

        # Convert English question -> SQL
        sql_query = model.predict(question)

        # Execute SQL and fetch results + headers
        column_names, results = execute_sql(sql_query)

    return render_template(
        "index.html",
        sql_query=sql_query,
        results=results,
        column_names=column_names
    )

if __name__ == "__main__":
    app.run(debug=True)






