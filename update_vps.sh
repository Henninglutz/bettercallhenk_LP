#!/bin/bash
# VPS Update Script für Better Call HENK Landing Page
# Dieses Script muss AUF DEM VPS ausgeführt werden!

set -e  # Bei Fehler abbrechen

echo "🔄 Starting VPS update process..."

# 1. Zum Repository-Verzeichnis wechseln
cd /opt/bettercallhenk_LP

# 2. Aktuellen Status anzeigen
echo "📊 Current git status:"
git status
echo ""
echo "📍 Current branch:"
git branch --show-current
echo ""

# 3. Alle Änderungen fetchen
echo "📥 Fetching all branches from remote..."
git fetch --all

# 4. Zum richtigen Branch wechseln
echo "🔀 Switching to branch: claude/update-landing-page-4oO6F"
git checkout claude/update-landing-page-4oO6F

# 5. Latest changes pullen
echo "⬇️  Pulling latest changes..."
git pull origin claude/update-landing-page-4oO6F

# 6. Prüfe ob Bilder vorhanden sind
echo "🖼️  Checking images..."
if [ -f "static/images/poster.png" ]; then
    echo "✅ poster.png found"
else
    echo "❌ poster.png MISSING!"
fi

if [ -d "static/images/real-suits" ]; then
    echo "✅ real-suits directory found"
    ls -lh static/images/real-suits/
else
    echo "❌ real-suits directory MISSING!"
fi

# 7. Prüfe Python Dependencies
echo "📦 Checking Python dependencies..."
source venv/bin/activate
pip install -r requirements.txt --quiet

# 8. Prüfe welcher Service läuft
echo "🔍 Checking service status..."
if systemctl is-active --quiet bettercallhenk.service; then
    echo "✅ Service bettercallhenk.service is running"
    SERVICE_NAME="bettercallhenk.service"
elif systemctl is-active --quiet bettercallhenk-landing.service; then
    echo "✅ Service bettercallhenk-landing.service is running"
    SERVICE_NAME="bettercallhenk-landing.service"
else
    echo "❌ No service found running!"
    SERVICE_NAME="unknown"
fi

# 9. Restart Service
if [ "$SERVICE_NAME" != "unknown" ]; then
    echo "♻️  Restarting service: $SERVICE_NAME"
    sudo systemctl restart $SERVICE_NAME
    sleep 2
    sudo systemctl status $SERVICE_NAME --no-pager
else
    echo "⚠️  Cannot restart - service name unknown!"
    echo "Please check: systemctl list-units | grep bettercallhenk"
fi

# 10. Prüfe Nginx Config
echo "🌐 Checking Nginx configuration..."
if nginx -t 2>&1 | grep -q "successful"; then
    echo "✅ Nginx config is valid"
    sudo systemctl reload nginx
else
    echo "❌ Nginx config has errors!"
    nginx -t
fi

# 11. Finale Checks
echo ""
echo "🎯 Final checks:"
echo "-----------------------------------"
echo "Repository: $(pwd)"
echo "Branch: $(git branch --show-current)"
echo "Latest commit: $(git log -1 --oneline)"
echo "Service: $SERVICE_NAME"
echo ""
echo "🔍 Test URLs (check in browser):"
echo "   - Main page: http://your-domain.com/"
echo "   - Static test: http://your-domain.com/static/images/poster.png"
echo ""
echo "✅ Update complete!"
echo ""
echo "If images still don't show, check:"
echo "1. Permissions: ls -la /opt/bettercallhenk_LP/static/"
echo "2. Nginx logs: tail -f /var/log/nginx/error.log"
echo "3. App logs: journalctl -u $SERVICE_NAME -f"
