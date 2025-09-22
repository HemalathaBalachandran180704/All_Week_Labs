import requests
import sqlite3
import urllib3

# --- Disable SSL warnings since we're using verify=False ---
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- Hugging Face API settings ---
API_URL = "https://router.huggingface.co/v1/chat/completions"
API_TOKEN = "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"  # replace with your token
HEADERS = {"Authorization": f"Bearer {API_TOKEN}"}

# --- Database file ---
DB_PATH = "nlp_to_sql.db"


class TextToSQL:
    def __init__(self):
        self.api_url = API_URL
        self.headers = HEADERS

    def query(self, nl_query: str):
        """Call Hugging Face API to convert NL to SQL."""
        payload = {
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are an expert SQL query generator. "
                        "Convert the user's natural language request into a valid SQL query. "
                        "Use the following database schema:\n\n"
                        "1. stores(id INTEGER PK, name TEXT, location TEXT, phone TEXT, email TEXT, created_at TIMESTAMP)\n"
                        "2. users(id INTEGER PK, username TEXT UNIQUE, password TEXT, role TEXT CHECK ['admin','manager','staff','technician'], "
                        "full_name TEXT, email TEXT, store_id INTEGER FK stores(id), created_at TIMESTAMP, last_login TIMESTAMP)\n"
                        "3. user_stores(id INTEGER PK, user_id INTEGER FK users(id), store_id INTEGER FK stores(id), is_primary BOOLEAN, assigned_at TIMESTAMP)\n"
                        "4. store_technicians(id INTEGER PK, store_id INTEGER FK stores(id), technician_id INTEGER FK users(id), assigned_at TIMESTAMP, is_active BOOLEAN, UNIQUE technician_id)\n"
                        "5. customers(id INTEGER PK, name TEXT, phone TEXT, email TEXT, address TEXT, store_id INTEGER FK stores(id), created_at TIMESTAMP)\n"
                        "6. jobs(id INTEGER PK, customer_id INTEGER FK customers(id), device_type TEXT, device_model TEXT, device_password_type TEXT, "
                        "device_password TEXT, notification_methods TEXT, problem_description TEXT, deposit_cost REAL, raw_cost REAL, estimate_cost REAL, "
                        "actual_cost REAL, payment_status TEXT, payment_method TEXT, status TEXT, store_id INTEGER FK stores(id), assigned_by INTEGER FK users(id), "
                        "created_at TIMESTAMP, updated_at TIMESTAMP, completed_at TIMESTAMP, started_at TIMESTAMP)\n"
                        "7. job_notes(id INTEGER PK, job_id INTEGER FK jobs(id), note TEXT, created_at TIMESTAMP)\n"
                        "8. job_photos(id INTEGER PK, job_id INTEGER FK jobs(id), photo BLOB, uploaded_at TIMESTAMP)\n"
                        "9. technician_assignments(id INTEGER PK, technician_id INTEGER FK users(id), assigned_by INTEGER FK users(id), "
                        "assigned_at TIMESTAMP, started_at TIMESTAMP, completed_at TIMESTAMP, status TEXT, notes TEXT)\n"
                        "10. assignment_jobs(id INTEGER PK, assignment_id INTEGER FK technician_assignments(id), job_id INTEGER FK jobs(id))\n"
                        "11. old_mobiles(id INTEGER PK, customer_name TEXT, customer_phone TEXT, customer_email TEXT, aadhar_number TEXT, "
                        "customer_address TEXT, mobile_brand TEXT, mobile_model TEXT, imei_number TEXT, repair_status TEXT, warranty_status TEXT, "
                        "repair_description TEXT, estimated_value REAL, purchase_date DATE, accessories_included TEXT, notes TEXT, store_id INTEGER FK stores(id), "
                        "created_at TIMESTAMP, updated_at TIMESTAMP)\n\n"
                        "Return only the SQL query without explanations."
                    )
                },
                {
                    "role": "user",
                    "content": nl_query
                }
            ],
            "model": "meta-llama/Llama-3.1-8B-Instruct:cerebras"
        }
        try:
            response = requests.post(self.api_url, headers=self.headers, json=payload, verify=False)
            return response.json()
        except Exception as e:
            return {"error": str(e)}

    def predict(self, nl_query: str):
        """Return SQL string from NL query."""
        response = self.query(nl_query)
        try:
            return response["choices"][0]["message"]["content"]
        except Exception as e:
            return f"Error parsing response: {e}\nFull response: {response}"


# --- SQLite execution ---
def execute_sql(sql_query: str):
    """Execute a SQL query on the local SQLite DB."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        cur.execute(sql_query)
        rows = cur.fetchall()
    except Exception as e:
        rows = f"Error executing SQL: {e}"
    conn.close()
    return rows


# --- Main loop ---
if __name__ == "__main__":
    print("NL→SQL with LLaMA-3.1 (Hugging Face)")
    print("Type 'exit' to quit.\n")

    model = TextToSQL()

    while True:
        nl_query = input("NL> ").strip()
        if nl_query.lower() in ("exit", "quit"):
            break

        sql_query = model.predict(nl_query)
        print("\nGenerated SQL:\n", sql_query)

        results = execute_sql(sql_query)
        print("\nQuery Results:")
        if isinstance(results, list):
            for r in results:
                print(dict(r))  # print as dict for readability
        else:
            print(results)

        print("\n" + "-"*50 + "\n")