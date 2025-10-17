from flask import Flask, render_template, request, jsonify
from datetime import datetime
import csv, os

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.post('/api/subscribe')
def subscribe():
    payload = request.get_json(force=True, silent=True) or {}
    row = {
        'ts': datetime.utcnow().isoformat()+'Z',
        'name': payload.get('name',''),
        'email': payload.get('email',''),
        'whatsapp': payload.get('whatsapp',''),
        'usecase': payload.get('usecase','')
    }
    os.makedirs('storage', exist_ok=True)
    path = os.path.join('storage', 'leads.csv')
    exists = os.path.exists(path)
    with open(path, 'a', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=row.keys())
        if not exists: w.writeheader()
        w.writerow(row)
    return jsonify({'ok': True})

if __name__ == '__main__':
    app.run(debug=True, port=8080)
