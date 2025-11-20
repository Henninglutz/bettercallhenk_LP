#!/bin/bash
# Quick Fix for Henk Repo - Pydantic v2 Compatibility
# Run this in your henk.bettercallhenk.de directory on your Mac

set -e

echo "=========================================="
echo "HENK Fabric Module - Pydantic v2 Fix"
echo "=========================================="
echo ""

# Check we're in the right directory
if [ ! -f "run_fabric_pipeline.py" ]; then
    echo "❌ Error: run_fabric_pipeline.py not found!"
    echo "Please run this script from henk.bettercallhenk.de directory"
    exit 1
fi

echo "✅ In henk.bettercallhenk.de directory"
echo ""

# Step 1: Install pydantic-settings
echo "Step 1/3: Installing pydantic-settings..."
pip install pydantic-settings>=2.0.0
echo "✅ pydantic-settings installed"
echo ""

# Step 2: Backup old config
echo "Step 2/3: Backing up old config..."
if [ -f "config/fabric_config.py" ]; then
    cp config/fabric_config.py config/fabric_config.py.backup
    echo "✅ Backup created: config/fabric_config.py.backup"
else
    echo "⚠️  No existing config found - will create new one"
fi
echo ""

# Step 3: Update config with Pydantic v2 imports
echo "Step 3/3: Updating config/fabric_config.py..."

cat > config/fabric_config.py << 'EOF'
"""
Fabric Module Configuration - Pydantic v2 Compatible
Manages all configuration settings for the HENK fabric scraping and RAG integration.
"""

import os
from typing import Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class FabricConfig(BaseSettings):
    """Configuration for fabric scraping and processing"""

    # Formens B2B Credentials
    FORMENS_USERNAME: str = Field(default="", env="FORMENS_USERNAME")
    FORMENS_PASSWORD: str = Field(default="", env="FABRIC_SCRAPER_PASSWORD")
    FORMENS_BASE_URL: str = "https://b2b2.formens.ro"
    FORMENS_STOCK_URL: str = "https://b2b2.formens.ro/stocktisue"
    FORMENS_IMAGE_BASE_URL: str = "https://b2b2.formens.ro/documente/marketing"

    # Scraping Settings
    SCRAPER_USER_AGENT: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    SCRAPER_DELAY_MIN: float = 1.0
    SCRAPER_DELAY_MAX: float = 3.0
    SCRAPER_TIMEOUT: int = 30
    SCRAPER_MAX_RETRIES: int = 3
    SCRAPER_BATCH_SIZE: int = 10
    SCRAPER_HEADLESS: bool = True

    # Storage Settings
    FABRIC_STORAGE_PATH: str = Field(default="./storage/fabrics", env="FABRIC_STORAGE_PATH")
    FABRIC_IMAGE_STORAGE: str = Field(default="./storage/fabrics/images", env="FABRIC_IMAGE_STORAGE")
    FABRIC_DATA_STORAGE: str = Field(default="./storage/fabrics/data", env="FABRIC_DATA_STORAGE")

    # Database Settings
    DATABASE_URL: str = Field(default="", env="DATABASE_URL")
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_TIMEOUT: int = 30

    # OpenAI Settings
    OPENAI_API_KEY: str = Field(default="", env="OPENAI_API_KEY")
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"
    OPENAI_EMBEDDING_DIMENSIONS: int = 1536
    OPENAI_DALLE_MODEL: str = "dall-e-3"
    OPENAI_DALLE_SIZE: str = "1024x1024"
    OPENAI_DALLE_QUALITY: str = "standard"

    # RAG Settings
    RAG_CHUNK_SIZE: int = 500
    RAG_CHUNK_OVERLAP: int = 50
    RAG_TOP_K_RESULTS: int = 5
    RAG_SIMILARITY_THRESHOLD: float = 0.7

    # Processing Settings
    IMAGE_MAX_WIDTH: int = 2048
    IMAGE_MAX_HEIGHT: int = 2048
    IMAGE_QUALITY: int = 90
    IMAGE_FORMAT: str = "JPEG"

    # Logging
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Feature Flags
    ENABLE_SCRAPING: bool = Field(default=True, env="ENABLE_SCRAPING")
    ENABLE_RAG: bool = Field(default=True, env="ENABLE_RAG")
    ENABLE_DALLE: bool = Field(default=True, env="ENABLE_DALLE")
    ENABLE_AUTO_UPDATE: bool = Field(default=False, env="ENABLE_AUTO_UPDATE")
    AUTO_UPDATE_INTERVAL_HOURS: int = 24

    class Config:
        env_file = ".env"
        case_sensitive = True

    @field_validator("FABRIC_STORAGE_PATH", "FABRIC_IMAGE_STORAGE", "FABRIC_DATA_STORAGE")
    @classmethod
    def create_directories(cls, v):
        """Ensure storage directories exist"""
        os.makedirs(v, exist_ok=True)
        return v

    @field_validator("DATABASE_URL")
    @classmethod
    def validate_database_url(cls, v):
        """Validate database URL format"""
        if v and not v.startswith(("postgresql://", "postgres://")):
            raise ValueError("DATABASE_URL must be a valid PostgreSQL connection string")
        return v

    def get_formens_credentials(self) -> tuple[str, str]:
        """Get Formens login credentials"""
        if not self.FORMENS_USERNAME or not self.FORMENS_PASSWORD:
            raise ValueError(
                "Formens credentials not configured. "
                "Please set FORMENS_USERNAME and FABRIC_SCRAPER_PASSWORD in .env"
            )
        return self.FORMENS_USERNAME, self.FORMENS_PASSWORD

    def is_openai_configured(self) -> bool:
        """Check if OpenAI is properly configured"""
        return bool(self.OPENAI_API_KEY)

    def is_database_configured(self) -> bool:
        """Check if database is properly configured"""
        return bool(self.DATABASE_URL)


# Global configuration instance
config = FabricConfig()


# Fabric Categories and Classifications
FABRIC_CATEGORIES = {
    "ceremony": {
        "name": "Ceremony Suits",
        "occasions": ["wedding", "formal_event", "gala"],
        "seasons": ["spring", "summer", "fall", "winter"]
    },
    "business": {
        "name": "Business Suits",
        "occasions": ["business", "office", "professional"],
        "seasons": ["spring", "summer", "fall", "winter"]
    },
    "casual": {
        "name": "Casual Wear",
        "occasions": ["casual", "smart_casual", "weekend"],
        "seasons": ["spring", "summer", "fall", "winter"]
    },
    "seasonal": {
        "name": "Seasonal Collections",
        "occasions": ["varied"],
        "seasons": ["spring", "summer", "fall", "winter"]
    }
}

FABRIC_COMPOSITIONS = [
    "wool", "cotton", "linen", "silk", "polyester",
    "wool_blend", "cotton_blend", "cashmere",
    "mohair", "alpaca", "viscose", "synthetic"
]

FABRIC_PATTERNS = [
    "solid", "striped", "checked", "plaid",
    "herringbone", "houndstooth", "pinstripe",
    "windowpane", "birdseye", "twill", "textured"
]

FABRIC_WEIGHTS = {
    "lightweight": {"min": 0, "max": 250, "seasons": ["spring", "summer"]},
    "medium": {"min": 250, "max": 350, "seasons": ["spring", "fall"]},
    "heavyweight": {"min": 350, "max": 600, "seasons": ["fall", "winter"]}
}

FABRIC_FINISHES = [
    "matte", "shiny", "semi_gloss", "brushed",
    "smooth", "textured", "velvet", "satin"
]

# Season to month mapping
SEASONS_MONTHS = {
    "spring": [3, 4, 5],
    "summer": [6, 7, 8],
    "fall": [9, 10, 11],
    "winter": [12, 1, 2]
}
EOF

echo "✅ config/fabric_config.py updated"
echo ""

# Step 4: Verify installation
echo "=========================================="
echo "Verifying Installation..."
echo "=========================================="
echo ""

echo "Test 1: pydantic-settings import..."
python -c "from pydantic_settings import BaseSettings; print('✅ pydantic-settings OK')" || echo "❌ Failed"

echo "Test 2: fabric_config import..."
python -c "from config.fabric_config import config; print('✅ Config import OK')" || echo "❌ Failed"

echo "Test 3: Check configuration..."
python -c "
from config.fabric_config import config
print(f'✅ Database URL configured: {bool(config.DATABASE_URL)}')
print(f'✅ OpenAI configured: {config.is_openai_configured()}')
print(f'✅ Formens configured: {bool(config.FORMENS_USERNAME)}')
" || echo "❌ Failed"

echo ""
echo "=========================================="
echo "✅ Fix Complete!"
echo "=========================================="
echo ""
echo "You can now run:"
echo "  python run_fabric_pipeline.py"
echo ""
echo "This will scrape ALL fabrics from Formens (no test limit)"
echo ""
