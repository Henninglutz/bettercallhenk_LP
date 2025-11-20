# HENK Fabric Module - Migration Guide

Migration des Fabric Moduls von `bettercallhenk_LP` zu `henk.bettercallhenk.de`

## ✅ Automatische Migration (Empfohlen)

### Voraussetzungen
- Git Zugriff auf `henk.bettercallhenk.de` Repository
- GitHub Login konfiguriert

### Schritt 1: Script ausführen

```bash
cd /pfad/zu/bettercallhenk_LP
./migrate_to_henk.sh
```

**Das Script macht:**
1. ✅ Klont henk.bettercallhenk.de Repo
2. ✅ Erstellt neuen Branch `claude/fabric-scraping-rag-01QiDoYXKHW9GjAWyfqVHQGG`
3. ✅ Kopiert alle Fabric Module Dateien:
   - `modules/` → fabric_scraper.py, fabric_processor.py, outfit_generator.py, fabric_api.py
   - `database/` → models.py, db_manager.py, fabric_migrations.sql
   - `config/` → fabric_config.py
   - `tests/` → test_fabric_module.py
   - `storage/` → Verzeichnisstruktur
   - Dokumentation → README, QUICKSTART, Integration-Beispiele
4. ✅ Merged requirements.txt
5. ✅ Aktualisiert .env.example
6. ✅ Committed mit vollständiger Message
7. ✅ Pusht zu GitHub

### Schritt 2: Pull Request erstellen

Nach erfolgreichem Push:

```
https://github.com/Henninglutz/henk.bettercallhenk.de/pull/new/claude/fabric-scraping-rag-01QiDoYXKHW9GjAWyfqVHQGG
```

---

## 🔧 Manuelle Migration (Falls Script fehlschlägt)

### Schritt 1: Henk Repo klonen

```bash
cd ~
git clone https://github.com/Henninglutz/henk.bettercallhenk.de.git
cd henk.bettercallhenk.de
git checkout -b claude/fabric-scraping-rag-01QiDoYXKHW9GjAWyfqVHQGG
```

### Schritt 2: Dateien kopieren

```bash
# Von bettercallhenk_LP kopieren
LP_PATH="/pfad/zu/bettercallhenk_LP"

# Module
cp -r $LP_PATH/modules .
cp -r $LP_PATH/database .
cp -r $LP_PATH/config .
cp -r $LP_PATH/tests .

# Storage Struktur
mkdir -p storage/fabrics/images
mkdir -p storage/fabrics/data

# Dokumentation
cp $LP_PATH/FABRIC_MODULE_README.md .
cp $LP_PATH/QUICKSTART.md .
cp $LP_PATH/app_with_fabric_module.py .
```

### Schritt 3: requirements.txt aktualisieren

Füge hinzu:

```txt
# Fabric Scraping Module
playwright==1.40.0
beautifulsoup4==4.12.2
lxml==4.9.3
aiohttp==3.9.1

# AI & RAG Integration
openai==1.6.1
tiktoken==0.5.2

# Database
psycopg2-binary==2.9.9
sqlalchemy==2.0.23
pgvector==0.2.4

# Image Processing
Pillow==10.1.0

# Data Processing
pandas==2.1.4
numpy==1.26.2

# Utilities
tenacity==8.2.3
pydantic==2.5.3
python-slugify==8.0.1
```

### Schritt 4: .env.example aktualisieren

Füge hinzu:

```env
# ============================================================================
# HENK Fabric Module Configuration
# ============================================================================

# Formens B2B Authentication (REQUIRED for fabric scraping)
FORMENS_USERNAME=
FABRIC_SCRAPER_PASSWORD=

# OpenAI API (REQUIRED for RAG and DALL-E)
OPENAI_API_KEY=

# Database Configuration (REQUIRED for persistent storage)
DATABASE_URL=postgresql://user:password@localhost:5432/henk_fabrics

# Storage Paths (Optional - defaults provided)
FABRIC_STORAGE_PATH=./storage/fabrics
FABRIC_IMAGE_STORAGE=./storage/fabrics/images
FABRIC_DATA_STORAGE=./storage/fabrics/data

# Feature Flags
ENABLE_SCRAPING=true
ENABLE_RAG=true
ENABLE_DALLE=true
ENABLE_AUTO_UPDATE=false

# Logging
LOG_LEVEL=INFO
```

### Schritt 5: Commit & Push

```bash
git add -A
git commit -m "Add HENK Fabric Scraping & RAG Integration Module

Migrated from bettercallhenk_LP repository.

Components:
- Web scraping with Playwright
- RAG processing with OpenAI embeddings
- DALL-E outfit generation
- PostgreSQL database with pgvector
- REST API endpoints
- Complete documentation and tests
"

git push -u origin claude/fabric-scraping-rag-01QiDoYXKHW9GjAWyfqVHQGG
```

---

## 📋 Datei-Checkliste

Stelle sicher, dass folgende Dateien übertragen wurden:

### Modules
- [x] `modules/__init__.py`
- [x] `modules/fabric_scraper.py`
- [x] `modules/fabric_processor.py`
- [x] `modules/outfit_generator.py`
- [x] `modules/fabric_api.py`

### Database
- [x] `database/__init__.py`
- [x] `database/models.py`
- [x] `database/db_manager.py`
- [x] `database/fabric_migrations.sql`

### Config
- [x] `config/__init__.py`
- [x] `config/fabric_config.py`

### Tests
- [x] `tests/__init__.py`
- [x] `tests/test_fabric_module.py`

### Documentation
- [x] `FABRIC_MODULE_README.md`
- [x] `QUICKSTART.md`
- [x] `app_with_fabric_module.py`

### Configuration Files
- [x] `requirements.txt` (updated)
- [x] `.env.example` (updated)

### Directories
- [x] `storage/fabrics/images/`
- [x] `storage/fabrics/data/`

---

## 🚀 Nach der Migration

### 1. Setup in henk.bettercallhenk.de

```bash
cd henk.bettercallhenk.de

# Dependencies installieren
pip install -r requirements.txt
playwright install chromium

# Environment konfigurieren
cp .env.example .env
# → Fülle Credentials aus
```

### 2. Database Setup

```bash
# PostgreSQL Datenbank erstellen
createdb henk_fabrics

# Schema installieren
psql henk_fabrics < database/fabric_migrations.sql
```

### 3. Ersten Scraping-Lauf

```bash
# Fabric Daten scrapen
python modules/fabric_scraper.py

# Embeddings generieren
python modules/fabric_processor.py

# In Datenbank importieren
python database/db_manager.py
```

### 4. Tests ausführen

```bash
python -m pytest tests/ -v
```

### 5. API Integration

Aktualisiere deine main `app.py`:

```python
from modules.fabric_api import register_fabric_api

app = Flask(__name__)
register_fabric_api(app)  # Registriert /api/fabrics/* Endpoints
```

---

## 🔍 Troubleshooting

### Problem: Script schlägt fehl mit Git-Fehler

**Lösung**: Manuelle Migration durchführen (siehe oben)

### Problem: requirements.txt Konflikte

**Lösung**:
```bash
# Duplikate entfernen
sort -u requirements.txt -o requirements.txt

# Oder manuell mergen
```

### Problem: Playwright Installation fehlt

**Lösung**:
```bash
playwright install chromium
playwright install-deps chromium  # System dependencies
```

---

## ✅ Verifizierung

Nach der Migration prüfen:

```bash
# Dateien vorhanden?
ls -la modules/ database/ config/ tests/

# Git Status
git status

# Tests laufen?
python -m pytest tests/ -v

# Import funktioniert?
python -c "from modules.fabric_scraper import FormensScraper; print('✅ OK')"
python -c "from modules.fabric_processor import FabricProcessor; print('✅ OK')"
python -c "from database.models import Fabric; print('✅ OK')"
```

---

## 📞 Support

Bei Problemen:
1. Prüfe Logs in der Console-Ausgabe
2. Verifiziere Git-Zugriff auf henk Repo
3. Review FABRIC_MODULE_README.md für Details
4. Kontaktiere Development Team

---

**Migration erstellt**: 2024-11-20
**Ziel-Branch**: `claude/fabric-scraping-rag-01QiDoYXKHW9GjAWyfqVHQGG`
**Quell-Repo**: `bettercallhenk_LP`
**Ziel-Repo**: `henk.bettercallhenk.de`
