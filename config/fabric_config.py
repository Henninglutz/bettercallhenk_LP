"""
Fabric Module Configuration
Manages all configuration settings for the HENK fabric scraping and RAG integration.
"""

import os
from typing import Optional
from pydantic import BaseSettings, Field, validator
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
    SCRAPER_DELAY_MIN: float = 1.0  # Minimum delay between requests (seconds)
    SCRAPER_DELAY_MAX: float = 3.0  # Maximum delay between requests (seconds)
    SCRAPER_TIMEOUT: int = 30  # Request timeout (seconds)
    SCRAPER_MAX_RETRIES: int = 3
    SCRAPER_BATCH_SIZE: int = 10  # Number of fabrics to process in parallel
    SCRAPER_HEADLESS: bool = True  # Run browser in headless mode

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
    RAG_CHUNK_SIZE: int = 500  # Characters per chunk
    RAG_CHUNK_OVERLAP: int = 50  # Overlap between chunks
    RAG_TOP_K_RESULTS: int = 5  # Number of similar fabrics to retrieve
    RAG_SIMILARITY_THRESHOLD: float = 0.7  # Minimum similarity score

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

    @validator("FABRIC_STORAGE_PATH", "FABRIC_IMAGE_STORAGE", "FABRIC_DATA_STORAGE")
    def create_directories(cls, v):
        """Ensure storage directories exist"""
        os.makedirs(v, exist_ok=True)
        return v

    @validator("DATABASE_URL")
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
