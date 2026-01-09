# VPS Deployment Anleitung – Better Call HENK Landing Page

Diese Anleitung zeigt dir, wie du die Landing Page auf einem VPS (Virtual Private Server) veröffentlichst.

## Voraussetzungen

- VPS mit Ubuntu/Debian (empfohlen: Ubuntu 22.04 LTS)
- Root- oder Sudo-Zugriff
- Domain (z.B. bettercallhenk.de)

---

## 1. VPS vorbereiten

### SSH-Verbindung aufbauen

```bash
ssh root@DEINE_VPS_IP
```

### System aktualisieren

```bash
apt update && apt upgrade -y
```

### Python und notwendige Pakete installieren

```bash
apt install -y python3 python3-pip python3-venv nginx git
```

---

## 2. Anwendung auf den Server bringen

### Repository klonen

```bash
cd /opt
git clone https://github.com/Henninglutz/bettercallhenk_LP.git
cd bettercallhenk_LP
```

**Wichtig:** Wechsle zum richtigen Branch:

```bash
git checkout claude/original-form-corrected-images-ibbxc
```

### Python Virtual Environment erstellen

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Optional: .env Datei erstellen (falls Pipedrive API benötigt)

```bash
cp .env.example .env
nano .env
```

Füge deine Pipedrive API Credentials ein (falls gewünscht):
```
PIPEDRIVE_API_TOKEN=dein_token_hier
PIPEDRIVE_DOMAIN=deine_firma
```

---

## 3. Systemd Service einrichten

### Service-Datei erstellen

```bash
nano /etc/systemd/system/bettercallhenk.service
```

Füge folgenden Inhalt ein:

```ini
[Unit]
Description=Better Call HENK Landing Page
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/bettercallhenk_LP
Environment="PATH=/opt/bettercallhenk_LP/venv/bin"
ExecStart=/opt/bettercallhenk_LP/venv/bin/python app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Berechtigungen setzen

```bash
chown -R www-data:www-data /opt/bettercallhenk_LP
```

### Service aktivieren und starten

```bash
systemctl daemon-reload
systemctl enable bettercallhenk.service
systemctl start bettercallhenk.service
```

### Status prüfen

```bash
systemctl status bettercallhenk.service
```

Die App läuft jetzt auf `localhost:8080`

---

## 4. Nginx Reverse Proxy einrichten

### Nginx Konfiguration erstellen

```bash
nano /etc/nginx/sites-available/bettercallhenk
```

Füge folgenden Inhalt ein (ersetze `bettercallhenk.de` mit deiner Domain):

```nginx
server {
    listen 80;
    server_name bettercallhenk.de www.bettercallhenk.de;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /opt/bettercallhenk_LP/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    client_max_body_size 10M;
}
```

### Konfiguration aktivieren

```bash
ln -s /etc/nginx/sites-available/bettercallhenk /etc/nginx/sites-enabled/
nginx -t  # Konfiguration testen
systemctl restart nginx
```

---

## 5. SSL-Zertifikat mit Let's Encrypt (HTTPS)

### Certbot installieren

```bash
apt install -y certbot python3-certbot-nginx
```

### SSL-Zertifikat erstellen

```bash
certbot --nginx -d bettercallhenk.de -d www.bettercallhenk.de
```

Folge den Anweisungen. Certbot konfiguriert automatisch HTTPS.

### Auto-Renewal testen

```bash
certbot renew --dry-run
```

---

## 6. Domain einrichten

Bei deinem Domain-Anbieter (z.B. Namecheap, GoDaddy, etc.):

1. Gehe zu DNS-Einstellungen
2. Erstelle folgende A-Records:

```
Type    Name    Value           TTL
A       @       DEINE_VPS_IP    Automatic
A       www     DEINE_VPS_IP    Automatic
```

**Hinweis:** DNS-Änderungen können bis zu 24h dauern, sind aber meist nach 15-30 Minuten aktiv.

---

## 7. Logs und Monitoring

### App-Logs anzeigen

```bash
journalctl -u bettercallhenk.service -f
```

### Nginx Logs

```bash
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

### Service neu starten (bei Änderungen)

```bash
systemctl restart bettercallhenk.service
```

---

## 8. Updates deployen

Wenn du Änderungen am Code machst:

```bash
cd /opt/bettercallhenk_LP
git pull origin claude/original-form-corrected-images-ibbxc
systemctl restart bettercallhenk.service
```

---

## 9. Firewall einrichten (empfohlen)

```bash
ufw allow 22    # SSH
ufw allow 80    # HTTP
ufw allow 443   # HTTPS
ufw enable
ufw status
```

---

## Troubleshooting

### App startet nicht

```bash
# Logs prüfen
journalctl -u bettercallhenk.service -n 50

# Manuell testen
cd /opt/bettercallhenk_LP
source venv/bin/activate
python app.py
```

### Nginx zeigt 502 Bad Gateway

```bash
# Prüfe ob die App läuft
systemctl status bettercallhenk.service

# Prüfe ob Port 8080 offen ist
netstat -tulpn | grep 8080
```

### Domain zeigt nichts an

1. Prüfe DNS: `dig bettercallhenk.de` oder `nslookup bettercallhenk.de`
2. Prüfe Nginx: `systemctl status nginx`
3. Prüfe Firewall: `ufw status`

---

## Alternative: Gunicorn statt Flask Development Server

Für Produktion empfohlen!

### Gunicorn installieren

```bash
source /opt/bettercallhenk_LP/venv/bin/activate
pip install gunicorn
```

### Service-Datei anpassen

```bash
nano /etc/systemd/system/bettercallhenk.service
```

Ändere die `ExecStart` Zeile:

```ini
ExecStart=/opt/bettercallhenk_LP/venv/bin/gunicorn -w 4 -b 127.0.0.1:8080 app:app
```

```bash
systemctl daemon-reload
systemctl restart bettercallhenk.service
```

---

## Kontakt

Bei Fragen: henk@bettercallhenk.de
