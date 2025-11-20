#!/bin/bash
# HENK Fabric Module Migration Script
# Verschiebt das Fabric Module von bettercallhenk_LP zu henk.bettercallhenk.de

set -e  # Exit on error

echo "========================================"
echo "HENK Fabric Module Migration"
echo "========================================"
echo ""

# Farben für Output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Konfiguration
LP_REPO_PATH="$(pwd)"
HENK_REPO_URL="https://github.com/Henninglutz/henk.bettercallhenk.de.git"
BRANCH_NAME="claude/fabric-scraping-rag-01QiDoYXKHW9GjAWyfqVHQGG"
TEMP_DIR="/tmp/henk_migration"

echo -e "${BLUE}Schritt 1/7: Vorbereitung...${NC}"
# Cleanup falls vorher abgebrochen
rm -rf "$TEMP_DIR"
mkdir -p "$TEMP_DIR"

echo -e "${BLUE}Schritt 2/7: Klone henk.bettercallhenk.de Repository...${NC}"
cd /tmp
git clone "$HENK_REPO_URL" "$TEMP_DIR/henk.bettercallhenk.de"
cd "$TEMP_DIR/henk.bettercallhenk.de"

echo -e "${BLUE}Schritt 3/7: Erstelle neuen Branch...${NC}"
git checkout -b "$BRANCH_NAME"

echo -e "${BLUE}Schritt 4/7: Kopiere Fabric Module Dateien...${NC}"

# Kopiere alle Fabric Module Verzeichnisse
echo "  → Kopiere modules/"
cp -r "$LP_REPO_PATH/modules" .

echo "  → Kopiere database/"
cp -r "$LP_REPO_PATH/database" .

echo "  → Kopiere config/"
cp -r "$LP_REPO_PATH/config" .

echo "  → Kopiere tests/"
cp -r "$LP_REPO_PATH/tests" .

echo "  → Erstelle storage/ Verzeichnisse"
mkdir -p storage/fabrics/images
mkdir -p storage/fabrics/data

echo "  → Kopiere Dokumentation"
cp "$LP_REPO_PATH/FABRIC_MODULE_README.md" .
cp "$LP_REPO_PATH/QUICKSTART.md" .
cp "$LP_REPO_PATH/app_with_fabric_module.py" .

echo -e "${BLUE}Schritt 5/7: Aktualisiere requirements.txt...${NC}"

# Fabric Module Dependencies
FABRIC_DEPS="
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
"

# Füge Dependencies zu requirements.txt hinzu (falls existiert)
if [ -f "requirements.txt" ]; then
    echo "  → Merge mit existierender requirements.txt"
    echo "$FABRIC_DEPS" >> requirements.txt
    # Entferne Duplikate
    sort -u requirements.txt -o requirements.txt
else
    echo "  → Erstelle neue requirements.txt"
    cat > requirements.txt << 'EOF'
flask
gunicorn
requests
python-dotenv

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
EOF
fi

echo -e "${BLUE}Schritt 6/7: Aktualisiere .env.example...${NC}"

# Fabric Module Env Variables
FABRIC_ENV="
# ============================================================================
# HENK Fabric Module Configuration
# ============================================================================

# Formens B2B Authentication (REQUIRED for fabric scraping)
FORMENS_USERNAME=
FABRIC_SCRAPER_PASSWORD=

# OpenAI API (REQUIRED for RAG and DALL-E)
OPENAI_API_KEY=

# Database Configuration (REQUIRED for persistent storage)
# Format: postgresql://username:password@host:port/database
# Example: postgresql://henk_user:password@localhost:5432/henk_fabrics
DATABASE_URL=

# Storage Paths (Optional - defaults provided)
FABRIC_STORAGE_PATH=./storage/fabrics
FABRIC_IMAGE_STORAGE=./storage/fabrics/images
FABRIC_DATA_STORAGE=./storage/fabrics/data

# Feature Flags
ENABLE_SCRAPING=true
ENABLE_RAG=true
ENABLE_DALLE=true
ENABLE_AUTO_UPDATE=false
AUTO_UPDATE_INTERVAL_HOURS=24

# Logging
LOG_LEVEL=INFO
"

if [ -f ".env.example" ]; then
    echo "  → Erweitere existierende .env.example"
    echo "$FABRIC_ENV" >> .env.example
else
    echo "  → Erstelle neue .env.example"
    echo "$FABRIC_ENV" > .env.example
fi

echo -e "${BLUE}Schritt 7/7: Git Commit und Push...${NC}"

# Git Add
git add -A

# Git Commit
git commit -m "$(cat <<'EOF'
Add complete HENK Fabric Scraping & RAG Integration Module

Migrated from bettercallhenk_LP to henk.bettercallhenk.de

Implemented comprehensive fabric data collection and processing module with:

✨ Features:
- Web scraping from Formens B2B platform with Playwright
- Authentication and rate-limited ethical scraping
- Data processing pipeline for RAG integration
- OpenAI embeddings for semantic fabric search
- DALL-E outfit generation based on fabric data
- PostgreSQL database with pgvector for similarity search
- RESTful API endpoints for all functionality
- Comprehensive unit tests

📁 Project Structure:
- modules/ - Core scraping, processing, and generation logic
- database/ - SQLAlchemy models and schema migrations
- config/ - Configuration management with Pydantic
- tests/ - Unit test suite

🔧 Components:
- fabric_scraper.py - Playwright-based scraper with authentication
- fabric_processor.py - RAG processing with OpenAI embeddings
- outfit_generator.py - DALL-E integration for outfit visualization
- fabric_api.py - Flask blueprint with REST endpoints
- models.py - SQLAlchemy database models
- db_manager.py - Database operations and utilities

🗄️ Database:
- PostgreSQL schema with pgvector extension
- 8 tables with proper indexing and relationships
- Vector similarity search with HNSW indexes
- Automatic triggers for timestamps

📚 Documentation:
- FABRIC_MODULE_README.md - Complete technical documentation
- QUICKSTART.md - 15-minute quick start guide
- app_with_fabric_module.py - Integration example
- Comprehensive API documentation

🧪 Testing:
- test_fabric_module.py - Unit tests for all components
- Test coverage for data models, processing, and generation

This module integrates with HENK's H1-H3 workflow for intelligent
fabric recommendations and outfit visualization.
EOF
)"

# Git Push
echo "  → Pushe zu GitHub..."
git push -u origin "$BRANCH_NAME"

echo ""
echo -e "${GREEN}========================================"
echo -e "✅ Migration erfolgreich abgeschlossen!"
echo -e "========================================${NC}"
echo ""
echo "Branch: $BRANCH_NAME"
echo "Repository: henk.bettercallhenk.de"
echo ""
echo "Pull Request erstellen:"
echo "https://github.com/Henninglutz/henk.bettercallhenk.de/pull/new/$BRANCH_NAME"
echo ""
echo -e "${BLUE}Nächste Schritte:${NC}"
echo "1. Pull Request erstellen und reviewen"
echo "2. Nach Merge: Setup in henk Repo:"
echo "   cd henk.bettercallhenk.de"
echo "   pip install -r requirements.txt"
echo "   playwright install chromium"
echo "   cp .env.example .env  # und ausfüllen"
echo "3. Database setup mit fabric_migrations.sql"
echo "4. Ersten Scraping-Lauf: python modules/fabric_scraper.py"
echo ""

# Cleanup
cd ~
rm -rf "$TEMP_DIR"

echo -e "${GREEN}Fertig! 🎉${NC}"
