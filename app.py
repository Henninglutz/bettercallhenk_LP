from flask import Flask, render_template, request, jsonify
from datetime import datetime
import csv, os, requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

def send_to_pipedrive(data):
    """
    Send lead data to Pipedrive CRM (optional).
    Returns True if successful, False otherwise.
    """
    api_token = os.getenv('PIPEDRIVE_API_TOKEN')
    domain = os.getenv('PIPEDRIVE_DOMAIN')

    # Skip if Pipedrive is not configured
    if not api_token or not domain:
        return False

    try:
        base_url = f'https://{domain}.pipedrive.com/api/v1'
        params = {'api_token': api_token}

        # Step 1: Create Person in Pipedrive
        person_data = {
            'name': data.get('name') or data.get('email', 'Beta User'),
            'email': [{'value': data.get('email'), 'primary': True, 'label': 'work'}] if data.get('email') else [],
            'phone': [{'value': data.get('whatsapp'), 'primary': True, 'label': 'mobile'}] if data.get('whatsapp') else []
        }

        person_response = requests.post(
            f'{base_url}/persons',
            params=params,
            json=person_data,
            timeout=10
        )

        if not person_response.ok:
            print(f"Pipedrive Person Error: {person_response.status_code}")
            return False

        person_id = person_response.json().get('data', {}).get('id')

        # Step 2: Create Lead in Pipedrive
        lead_data = {
            'title': f'Beta Anmeldung: {data.get("name") or data.get("email")}',
            'person_id': person_id,
        }

        # Add use case as note if provided
        if data.get('usecase'):
            lead_data['note'] = f"Use Case: {data.get('usecase')}\n\nQuelle: Better Call HENK Beta Landing Page"
        else:
            lead_data['note'] = 'Quelle: Better Call HENK Beta Landing Page'

        lead_response = requests.post(
            f'{base_url}/leads',
            params=params,
            json=lead_data,
            timeout=10
        )

        if lead_response.ok:
            print(f"✓ Pipedrive Lead created for {data.get('email')}")
            return True
        else:
            print(f"Pipedrive Lead Error: {lead_response.status_code}")
            return False

    except Exception as e:
        print(f"Pipedrive Error: {str(e)}")
        return False

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

    # Save to CSV (primary storage)
    os.makedirs('storage', exist_ok=True)
    path = os.path.join('storage', 'leads.csv')
    exists = os.path.exists(path)
    with open(path, 'a', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=row.keys())
        if not exists: w.writeheader()
        w.writerow(row)

    # Send to Pipedrive (optional, non-blocking)
    send_to_pipedrive(payload)

    return jsonify({'ok': True})

if __name__ == '__main__':
    app.run(debug=True, port=8080)
