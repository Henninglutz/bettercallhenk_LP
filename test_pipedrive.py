#!/usr/bin/env python3
"""
Test script for Pipedrive API integration
Run this to verify your Pipedrive credentials and API integration
"""
import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_pipedrive_connection():
    """Test Pipedrive API connection and create a test lead"""
    api_token = os.getenv('PIPEDRIVE_API_TOKEN')
    domain = os.getenv('PIPEDRIVE_DOMAIN')

    print("=" * 60)
    print("PIPEDRIVE API TEST")
    print("=" * 60)

    # Check credentials
    if not api_token:
        print("❌ PIPEDRIVE_API_TOKEN nicht gesetzt!")
        print("   Bitte .env Datei erstellen und API Token eintragen.")
        return False

    if not domain:
        print("❌ PIPEDRIVE_DOMAIN nicht gesetzt!")
        print("   Bitte .env Datei erstellen und Domain eintragen.")
        return False

    print(f"✓ API Token gefunden: {api_token[:10]}...")
    print(f"✓ Domain: {domain}")
    print()

    base_url = f'https://{domain}.pipedrive.com/api/v1'
    params = {'api_token': api_token}

    # Test 1: Check API connection
    print("Test 1: API-Verbindung testen...")
    try:
        test_response = requests.get(
            f'{base_url}/users/me',
            params=params,
            timeout=10
        )
        if test_response.ok:
            user_data = test_response.json().get('data', {})
            print(f"✓ Verbindung erfolgreich!")
            print(f"  Eingeloggt als: {user_data.get('name')} ({user_data.get('email')})")
        else:
            print(f"❌ API-Fehler: {test_response.status_code}")
            print(f"   Response: {test_response.text}")
            return False
    except Exception as e:
        print(f"❌ Verbindungsfehler: {str(e)}")
        return False

    print()

    # Test 2: Create test person
    print("Test 2: Test-Person erstellen...")
    test_person_data = {
        'name': 'TEST - Better Call HENK Beta User',
        'email': [{'value': 'test@bettercallhenk.de', 'primary': True, 'label': 'work'}],
        'phone': [{'value': '+49123456789', 'primary': True, 'label': 'mobile'}]
    }

    try:
        person_response = requests.post(
            f'{base_url}/persons',
            params=params,
            json=test_person_data,
            timeout=10
        )

        if person_response.ok:
            person_data = person_response.json().get('data', {})
            person_id = person_data.get('id')
            print(f"✓ Test-Person erstellt!")
            print(f"  ID: {person_id}")
            print(f"  Name: {person_data.get('name')}")
        else:
            print(f"❌ Fehler beim Erstellen der Person: {person_response.status_code}")
            print(f"   Response: {person_response.text}")
            return False
    except Exception as e:
        print(f"❌ Fehler: {str(e)}")
        return False

    print()

    # Test 3: Create test lead
    print("Test 3: Test-Lead erstellen...")
    test_lead_data = {
        'title': 'TEST - Beta Anmeldung: Test User',
        'person_id': person_id,
    }

    try:
        lead_response = requests.post(
            f'{base_url}/leads',
            params=params,
            json=test_lead_data,
            timeout=10
        )

        if lead_response.ok:
            lead_data = lead_response.json().get('data', {})
            lead_id = lead_data.get('id')
            print(f"✓ Test-Lead erstellt!")
            print(f"  ID: {lead_id}")
            print(f"  Titel: {lead_data.get('title')}")
        else:
            print(f"❌ Fehler beim Erstellen des Leads: {lead_response.status_code}")
            print(f"   Response: {lead_response.text}")
            return False
    except Exception as e:
        print(f"❌ Fehler: {str(e)}")
        return False

    print()

    # Test 4: Create note for the lead
    print("Test 4: Test-Note für Lead erstellen...")
    test_note_data = {
        'content': 'Use Case: TEST\n\nQuelle: Better Call HENK Beta Landing Page (Test)',
        'lead_id': lead_id,
        'pinned_to_lead_flag': 1
    }

    try:
        note_response = requests.post(
            f'{base_url}/notes',
            params=params,
            json=test_note_data,
            timeout=10
        )

        if note_response.ok:
            note_data = note_response.json().get('data', {})
            print(f"✓ Test-Note erstellt!")
            print(f"  ID: {note_data.get('id')}")
            print(f"  Content: {note_data.get('content')[:50]}...")
        else:
            print(f"❌ Fehler beim Erstellen der Note: {note_response.status_code}")
            print(f"   Response: {note_response.text}")
            return False
    except Exception as e:
        print(f"❌ Fehler: {str(e)}")
        return False

    print()
    print("=" * 60)
    print("✓ ALLE TESTS ERFOLGREICH!")
    print("=" * 60)
    print()
    print("Nächste Schritte:")
    print("1. Überprüfe die Test-Person und den Test-Lead in Pipedrive")
    print("2. Lösche die Test-Einträge wenn gewünscht")
    print("3. Die Integration ist einsatzbereit!")
    print()

    return True


if __name__ == '__main__':
    success = test_pipedrive_connection()
    exit(0 if success else 1)
