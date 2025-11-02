from flask import Flask, render_template, request, jsonify
import sqlite3
from datetime import datetime, date

app = Flask(__name__)

# --- Initialize DB ---
def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS contacts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        phone TEXT NOT NULL,
                        sum_of_digits INTEGER NOT NULL,
                        dob TEXT
                    )''')
    conn.commit()
    conn.close()

# --- Home page ---
@app.route('/')
def home():
    return render_template('index.html')

# --- Add contact ---
@app.route('/add_contact', methods=['POST'])
def add_contact():
    name = request.form['name']
    phone = request.form['phone']
    dob = request.form.get('dob')

    sum_of_digits = sum(int(d) for d in phone if d.isdigit())

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO contacts (name, phone, sum_of_digits, dob) VALUES (?, ?, ?, ?)',
                   (name, phone, sum_of_digits, dob))
    conn.commit()
    conn.close()

    return jsonify({'status': 'success', 'message': 'Contact saved successfully!'})

# --- Retrieve contact ---
@app.route('/get_contact', methods=['POST'])
def get_contact():
    name = request.form['name']

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM contacts WHERE name = ?', (name,))
    result = cursor.fetchone()
    conn.close()

    if result:
        return jsonify({'status': 'success', 'data': result})
    else:
        return jsonify({'status': 'error', 'message': 'No contact found'})

# --- View all contacts ---
@app.route('/get_all', methods=['GET'])
def get_all():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM contacts')
    contacts = cursor.fetchall()
    conn.close()

    contact_list = []
    for c in contacts:
        dob = c[4]
        if dob:
            dob_date = datetime.strptime(dob, "%Y-%m-%d").date()
            days_of_life = (date.today() - dob_date).days
        else:
            days_of_life = None
        contact_list.append({
            'id': c[0],
            'name': c[1],
            'phone': c[2],
            'sum_of_digits': c[3],
            'dob': c[4],
            'days_of_life': days_of_life
        })

    return jsonify(contact_list)

# --- Delete contact ---
@app.route('/delete_contact/<int:id>', methods=['DELETE'])
def delete_contact(id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM contacts WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return jsonify({'status': 'success'})

if __name__ == '__main__':
    init_db()
    app.run(debug=True)