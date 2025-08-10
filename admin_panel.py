import os
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import sqlite3

DB = "bot.db"
ADMIN_SECRET = os.getenv('supersecret')

app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)

def query(sql, args=(), fetch=True):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute(sql, args)
    if fetch:
        rows = cur.fetchall()
    else:
        rows = None
    conn.commit()
    conn.close()
    return rows

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/api/users')
def api_users():
    secret = request.args.get('secret')
    if secret != ADMIN_SECRET:
        return jsonify({"error": "unauthorized"}), 401
    rows = query('SELECT telegram_id, username, first_name, banned, is_premium, created_at FROM users ORDER BY created_at DESC LIMIT 200')
    users = [{"telegram_id": r[0], "username": r[1], "first_name": r[2], "banned": r[3], "is_premium": r[4], "created_at": r[5]} for r in rows]
    return jsonify(users)

@app.route('/api/ban', methods=['POST'])
def api_ban():
    data = request.json
    if data.get('secret') != ADMIN_SECRET:
        return jsonify({"error": "unauthorized"}), 401
    tg = data.get('telegram_id')
    query('UPDATE users SET banned=1 WHERE telegram_id=?', (tg,), fetch=False)
    return jsonify({"ok": True})

@app.route('/api/unban', methods=['POST'])
def api_unban():
    data = request.json
    if data.get('secret') != ADMIN_SECRET:
        return jsonify({"error": "unauthorized"}), 401
    tg = data.get('telegram_id')
    query('UPDATE users SET banned=0 WHERE telegram_id=?', (tg,), fetch=False)
    return jsonify({"ok": True})

@app.route('/api/stats')
def api_stats():
    secret = request.args.get('secret')
    if secret != ADMIN_SECRET:
        return jsonify({"error": "unauthorized"}), 401
    total = query('SELECT COUNT(*) FROM users')[0][0]
    banned = query('SELECT COUNT(*) FROM users WHERE banned=1')[0][0]
    premium = query('SELECT COUNT(*) FROM users WHERE is_premium=1')[0][0]
    return jsonify({"total": total, "banned": banned, "premium": premium})

if __name__ == "__main__":
    # For local testing only; Railway will run via main.py entrypoint
    app.run(host="0.0.0.0", port=5000, debug=True)
