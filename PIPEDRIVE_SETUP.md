# Pipedrive CRM Integration - Setup Anleitung

Die Landing Page kann Beta-Anmeldungen automatisch an Pipedrive senden. Die Integration ist **optional** und funktioniert parallel zur CSV-Speicherung.

## Option 1: Pipedrive API Integration (empfohlen)

### Voraussetzungen
- Pipedrive Account
- API-Zugriff aktiviert

### Setup-Schritte

1. **API-Token generieren**
   - Melde dich bei Pipedrive an
   - Gehe zu: **Einstellungen** → **Persönliche Einstellungen** → **API**
   - Kopiere deinen API-Token

2. **Umgebungsvariablen konfigurieren**
   - Kopiere `.env.example` zu `.env`:
     ```bash
     cp .env.example .env
     ```
   - Fülle die Werte in `.env` aus:
     ```env
     PIPEDRIVE_API_TOKEN=dein_api_token_hier
     PIPEDRIVE_DOMAIN=deine-firma
     ```
     (Wenn deine Pipedrive-URL `deine-firma.pipedrive.com` ist, verwende nur `deine-firma`)

3. **Dependencies installieren**
   ```bash
   pip install -r requirements.txt
   ```

4. **Server neu starten**
   ```bash
   python app.py
   ```

### Was passiert bei einer Anmeldung?

Bei jeder Beta-Anmeldung wird automatisch:
1. **Person erstellt** mit:
   - Name (wenn angegeben, sonst Email)
   - Email-Adresse
   - WhatsApp-Telefonnummer

2. **Lead erstellt** mit:
   - Titel: "Beta Anmeldung: [Name/Email]"
   - Verknüpfung zur Person
   - Use Case als Notiz (wenn angegeben)

3. **CSV-Backup** wird weiterhin in `storage/leads.csv` gespeichert

### Fehlerbehandlung
- Wenn Pipedrive nicht erreichbar ist, wird die Anmeldung trotzdem in CSV gespeichert
- Fehler werden im Server-Log ausgegeben
- Der Nutzer bekommt immer eine Erfolgsbestätigung

---

## Option 2: Pipedrive Web Forms (Alternative)

Falls du die **LeadBooster**-Funktion in Pipedrive hast, kannst du auch Web Forms verwenden:

### Setup-Schritte

1. **Web Form erstellen**
   - Gehe in Pipedrive zu: **Leads** → **Web Forms** → **New Web Form**
   - Erstelle Felder für:
     - Name
     - Email
     - WhatsApp
     - Use Case

2. **Embed-Code kopieren**
   - Klicke auf "Embed the form"
   - Kopiere den Embed-Code

3. **In Landing Page einfügen**
   - Ersetze das bestehende Formular in `templates/index.html` (Zeile 185-201)
   - Füge den Pipedrive Embed-Code ein

**Nachteil:** Du verlierst die lokale CSV-Speicherung als Backup.

---

## Option 3: Zapier/Make Integration

Für fortgeschrittene Workflows kannst du auch Zapier oder Make.com verwenden:

1. **Webhook in Zapier/Make erstellen**
2. **Webhook-URL in `app.py` hinzufügen**
3. **Zap/Scenario konfigurieren**: Webhook → Pipedrive

---

## Empfehlung

**Für die meisten Anwendungsfälle: Option 1 (API Integration)**

Vorteile:
- ✓ Einfaches Setup (nur .env konfigurieren)
- ✓ CSV-Backup bleibt erhalten
- ✓ Keine zusätzlichen Kosten (LeadBooster nicht nötig)
- ✓ Vollständige Kontrolle über die Daten
- ✓ Fehlerresistent (funktioniert auch ohne Pipedrive)

---

## Testen

Teste die Integration mit einer Test-Anmeldung:

```bash
# Server starten
python app.py

# In Browser öffnen
http://localhost:8080

# Formular ausfüllen und abschicken
```

Überprüfe:
1. CSV-Datei: `storage/leads.csv`
2. Pipedrive → Leads (neue Einträge sollten erscheinen)
3. Server-Log für Fehler

---

## Troubleshooting

### "Pipedrive Person Error: 401"
→ API-Token ist ungültig oder falsch konfiguriert

### "Pipedrive Person Error: 404"
→ PIPEDRIVE_DOMAIN ist falsch (prüfe deine Pipedrive-URL)

### Keine Fehlermeldung, aber kein Lead in Pipedrive
→ Prüfe ob `.env` Datei vorhanden ist und geladen wird
→ Prüfe Server-Log für Meldungen

### CSV wird erstellt, aber Pipedrive bleibt leer
→ Das ist in Ordnung! Pipedrive ist optional
→ Konfiguriere `.env` um Pipedrive zu aktivieren
