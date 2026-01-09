# 🚀 VPS Update – Neuer Branch mit erweiterten Features

## Problem-Diagnose

Die Landing Page auf dem VPS zeigt:
- ✅ **Text wird aktualisiert** (neue Content-Version)
- ❌ **KEINE BILDER** (poster.png, Slider-Bilder, Outfit-Galerie)
- ❓ **Formular muss geprüft werden**

## Root Cause

Der VPS läuft noch auf dem alten Branch:
```
claude/original-form-corrected-images-ibbxc
```

Der neue Branch mit allen Features ist:
```
claude/update-landing-page-4oO6F
```

## Lösung (2 Optionen)

### ⚡ Option 1: Automatisches Update-Script (EMPFOHLEN)

**Auf dem VPS ausführen:**

```bash
# Via SSH auf VPS verbinden
ssh root@YOUR_VPS_IP

# Update-Script herunterladen und ausführen
cd /opt/bettercallhenk_LP
git fetch origin claude/update-landing-page-4oO6F
git checkout claude/update-landing-page-4oO6F
git pull origin claude/update-landing-page-4oO6F

# Script ausführen
bash update_vps.sh
```

Das Script führt automatisch alle notwendigen Schritte aus!

---

### 🔧 Option 2: Manuelle Schritte

Falls das Script nicht funktioniert:

#### 1. Branch wechseln

```bash
cd /opt/bettercallhenk_LP
git fetch --all
git checkout claude/update-landing-page-4oO6F
git pull origin claude/update-landing-page-4oO6F
```

#### 2. Bilder prüfen

```bash
# Prüfe ob Bilder existieren
ls -lh static/images/poster.png
ls -lh static/images/real-suits/

# Permissions prüfen (sollte www-data gehören)
ls -la static/images/
```

#### 3. Service-Name identifizieren

```bash
# Finde den richtigen Service-Namen
systemctl list-units | grep bettercallhenk
```

Mögliche Namen:
- `bettercallhenk.service` (laut DEPLOYMENT.md)
- `bettercallhenk-landing.service` (User-Angabe)

#### 4. Service neu starten

```bash
# Ersetze SERVICE_NAME mit dem tatsächlichen Namen
sudo systemctl restart SERVICE_NAME
sudo systemctl status SERVICE_NAME
```

#### 5. Nginx neu laden

```bash
sudo nginx -t
sudo systemctl reload nginx
```

---

## 🔍 Troubleshooting: Bilder werden nicht angezeigt

### A) Prüfe ob Bilder im Repository vorhanden sind

```bash
cd /opt/bettercallhenk_LP

# Alle Bilder anzeigen
find static/images/ -type f -name "*.jpg" -o -name "*.png"
```

**Erwartetes Ergebnis:**
```
static/images/poster.png
static/images/Slider1.png
static/images/slider2.png
static/images/slider3.png
static/images/slider4.png
static/images/real-suits/outfit1.jpg
static/images/real-suits/outfit2.jpg
static/images/real-suits/outfit3.jpg
static/images/real-suits/outfit4.jpg
static/images/real-suits/outfit5.jpg
```

### B) Prüfe Permissions

```bash
# Alle Dateien sollten www-data gehören
ls -la /opt/bettercallhenk_LP/static/

# Falls nicht, Permissions korrigieren:
sudo chown -R www-data:www-data /opt/bettercallhenk_LP
```

### C) Prüfe Flask App

```bash
# Läuft die App überhaupt?
journalctl -u SERVICE_NAME -f

# Auf welchem Port?
netstat -tulpn | grep python
```

**Erwarteter Port:** 8080 (laut DEPLOYMENT.md)
**User-Angabe:** 8082 ⚠️ (stimmt nicht mit Doku überein!)

### D) Prüfe Nginx Konfiguration

```bash
# Nginx Config anzeigen
cat /etc/nginx/sites-available/bettercallhenk
```

**Wichtig:** Die `/static` Location muss korrekt sein:

```nginx
location /static {
    alias /opt/bettercallhenk_LP/static;
    expires 30d;
    add_header Cache-Control "public, immutable";
}
```

### E) Teste Static Files direkt

```bash
# Direkt im Browser testen:
curl -I http://YOUR_DOMAIN/static/images/poster.png
```

**Erwartetes Ergebnis:** `HTTP/1.1 200 OK`
**Fehler-Ergebnis:** `HTTP/1.1 404 Not Found` → Nginx findet Dateien nicht

### F) Nginx Error Logs prüfen

```bash
tail -f /var/log/nginx/error.log
```

Dann im Browser die Seite neu laden und schauen ob Fehler erscheinen.

---

## 🎯 Was ist jetzt im neuen Branch?

### ✅ Implementierte Features

1. **H1-Überschrift** statt `<h2>` für "Wer ist HENK?"
2. **Ausführlicher Content-Abschnitt:**
   - 5 Absätze über KI-gestützte Maßkonfektion
   - Vorteile für Kunden
   - Feature-Box mit allen Services
3. **Outfit-Galerie** mit allen 5 real-suits Bildern (outfit1-5.jpg)
4. **Pipedrive WebForms** bereits eingebunden (Zeile 207 in index.html)
5. **Aktualisierte Meta-Description** (kein "Beta Version 2025" mehr)

### 📁 Vollständige Bilderliste im Repository

**Hero-Bereich:**
- `static/images/poster.png` ✅

**Mood & Styles Galerie (Slider 1):**
- `static/images/Slider1.png` ✅
- `static/images/slider2.png` ✅
- `static/images/slider3.png` ✅
- `static/images/slider4.png` ✅

**Produzierte Outfits Galerie (Slider 2):**
- `static/images/real-suits/outfit1.jpg` ✅
- `static/images/real-suits/outfit2.jpg` ✅
- `static/images/real-suits/outfit3.jpg` ✅
- `static/images/real-suits/outfit4.jpg` ✅
- `static/images/real-suits/outfit5.jpg` ✅

### 🧪 Pipedrive WebForms Test

Das Formular ist eingebunden in `templates/index.html` Zeile 207:

```html
<div class="pipedriveWebForms" data-pd-webforms="https://webforms.pipedrive.com/f/2Xgr5U657aFmCYcBV75vnAsI9b58mkwBvmg4cYJDfpu2MZXFL0xFtoKCT7gSuQKfp">
  <script src="https://webforms.pipedrive.com/f/loader"></script>
</div>
```

**Prüfung nach VPS-Update:**
1. Öffne Landing Page im Browser
2. Scrolle zum Footer-Bereich (#signup)
3. Das Pipedrive-Formular sollte angezeigt werden
4. Teste eine Anmeldung (mit Test-Daten)
5. Prüfe in Pipedrive ob der Lead angekommen ist

---

## 📞 Nächste Schritte nach Update

1. **Im Browser testen:**
   - https://YOUR_DOMAIN/
   - Bilder sollten sichtbar sein
   - Formular sollte funktionieren

2. **Logs überwachen:**
   ```bash
   journalctl -u SERVICE_NAME -f
   ```

3. **Bei Problemen:**
   - Siehe Troubleshooting-Sektion oben
   - Prüfe Nginx error.log
   - Prüfe App-Logs

---

## ⚠️ Wichtige Hinweise

### Port-Diskrepanz
- **DEPLOYMENT.md sagt:** Port 8080
- **User sagt:** Port 8082
- **→ Bitte prüfen:** Welcher Port läuft wirklich?

### Service-Name-Diskrepanz
- **DEPLOYMENT.md sagt:** `bettercallhenk.service`
- **User sagt:** `bettercallhenk-landing.service`
- **→ Bitte prüfen:** Welcher Service läuft wirklich?

```bash
# Prüfe aktive Services
systemctl list-units --type=service | grep bettercallhenk
```

---

## 📊 Status-Check Checklist

Nach dem Update folgende Punkte prüfen:

```
[ ] Branch ist claude/update-landing-page-4oO6F
[ ] poster.png wird angezeigt
[ ] Slider1-4.png werden in Galerie 1 angezeigt
[ ] outfit1-5.jpg werden in Galerie 2 angezeigt
[ ] Pipedrive WebForms wird angezeigt
[ ] Formular funktioniert (Test-Anmeldung)
[ ] Texte sind aktualisiert (ausführlicher HENK-Abschnitt)
[ ] Meta-Description ist aktualisiert (kein "Beta Version 2025")
[ ] Service läuft ohne Fehler
[ ] Nginx läuft ohne Fehler
```

---

Bei Fragen oder Problemen: Logs posten!
