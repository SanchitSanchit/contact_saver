from flask import Flask, render_template, request, jsonify
import sqlite3, os
from datetime import datetime, date

app = Flask(__name__)

# === Database setup ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Add date_of_birth column if not exists
    c.execute('''CREATE TABLE IF NOT EXISTS contacts
                 (name TEXT, phone TEXT, sum_of_digits INTEGER, date_of_birth TEXT)''')
    try:
        # For backward compatibility if old DB exists
        c.execute("ALTER TABLE contacts ADD COLUMN date_of_birth TEXT")
    except sqlite3.OperationalError:
        pass
    conn.commit()
    conn.close()

# === Utility ===
def sum_digits(number_str):
    return sum(int(ch) for ch in number_str if ch.isdigit())

def calculate_days_of_life(dob_str):
    try:
        dob = datetime.strptime(dob_str, "%Y-%m-%d").date()
        today = date.today()
        return (today - dob).days
    except Exception:
        return None

# === Routes ===
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/save', methods=['POST'])
def save():
    name = request.form['name'].strip()
    phone = request.form['phone'].strip()
    dob = request.form.get('dob', '').strip()

    total = sum_digits(phone)

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO contacts VALUES (?, ?, ?, ?)", (name, phone, total, dob))
    conn.commit()
    conn.close()

    return f"✅ Data saved for {name}. Sum of digits = {total}"

@app.route('/retrieve', methods=['GET'])
def retrieve():
    name = request.args.get('name').strip()

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM contacts WHERE LOWER(name) = LOWER(?)", (name,))
    results = c.fetchall()
    conn.close()

    if results:
        data = []
        for r in results:
            days = calculate_days_of_life(r[3]) if r[3] else None
            data.append({
                "name": r[0],
                "phone": r[1],
                "sum": r[2],
                "dob": r[3],
                "days_of_life": days
            })
        return jsonify(data)
    else:
        return "❌ No record found for that name."

@app.route('/all', methods=['GET'])
def all_contacts():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT rowid, * FROM contacts ORDER BY name ASC")
    results = c.fetchall()
    conn.close()

    data = []
    for r in results:
        days = calculate_days_of_life(r[4]) if r[4] else None
        data.append({
            "id": r[0],
            "name": r[1],
            "phone": r[2],
            "sum": r[3],
            "dob": r[4],
            "days_of_life": days
        })

    return jsonify(data)

@app.route('/delete', methods=['POST'])
def delete_contact():
    contact_id = request.form['id']
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM contacts WHERE rowid = ?", (contact_id,))
    conn.commit()
    conn.close()
    return "✅ Record deleted successfully."

# === Start App ===
if __name__ == '__main__':
    init_db()
    app.run(debug=True)