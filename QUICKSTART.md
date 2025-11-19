# HENK Fabric Module - Quick Start Guide

Get up and running with the HENK fabric module in 15 minutes.

## Prerequisites

- Python 3.9+
- PostgreSQL 14+ with pgvector extension
- Formens B2B account credentials
- OpenAI API key

## Step 1: Install Dependencies (2 minutes)

```bash
# Install Python packages
pip install -r requirements.txt

# Install Playwright browser
playwright install chromium
```

## Step 2: Set Up Database (3 minutes)

```bash
# Create PostgreSQL database
createdb henk_fabrics

# Run migrations to set up schema
psql henk_fabrics < database/fabric_migrations.sql
```

Verify installation:
```bash
psql henk_fabrics -c "\dx"  # Should show pgvector extension
```

## Step 3: Configure Environment (2 minutes)

Create `.env` file from template:

```bash
cp .env.example .env
```

Edit `.env` and add your credentials:

```env
# Required
FORMENS_USERNAME=your_formens_username
FABRIC_SCRAPER_PASSWORD=your_formens_password
OPENAI_API_KEY=sk-your-openai-key
DATABASE_URL=postgresql://user:password@localhost:5432/henk_fabrics

# Optional (defaults provided)
LOG_LEVEL=INFO
ENABLE_SCRAPING=true
ENABLE_RAG=true
ENABLE_DALLE=true
```

## Step 4: Scrape Fabric Data (5 minutes)

Run the scraper to collect fabric data:

```bash
python modules/fabric_scraper.py
```

This will:
- Authenticate to Formens B2B
- Scrape fabric listings
- Download fabric images
- Save data to `storage/fabrics/data/fabrics_latest.json`

**Note**: First run may take 5-10 minutes depending on data volume.

## Step 5: Process Data for RAG (2 minutes)

Generate embeddings for semantic search:

```bash
python modules/fabric_processor.py
```

This will:
- Load scraped fabric data
- Create optimized chunks
- Generate OpenAI embeddings
- Save to `storage/fabrics/data/processed_latest.json`

## Step 6: Import to Database (1 minute)

Load data into PostgreSQL:

```bash
python database/db_manager.py
```

This will:
- Create database tables
- Import fabric data
- Import embeddings with vectors
- Display statistics

## Step 7: Test the API

Start the Flask app:

```bash
python app.py
```

Test endpoints:

```bash
# Health check
curl http://localhost:8080/api/fabrics/health

# Get all fabrics
curl http://localhost:8080/api/fabrics/?limit=5

# Search fabrics (RAG)
curl -X POST http://localhost:8080/api/fabrics/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "lightweight summer fabric for wedding",
    "limit": 3
  }'

# Generate outfit
curl -X POST http://localhost:8080/api/fabrics/outfits/generate \
  -H "Content-Type: application/json" \
  -d '{
    "occasion": "wedding",
    "season": "summer",
    "style_preferences": ["classic", "elegant"],
    "color_preferences": ["navy"],
    "use_rag": true
  }'
```

## Step 8: Integrate with Your App

Update your `app.py`:

```python
from flask import Flask
from modules.fabric_api import register_fabric_api

app = Flask(__name__)

# Register fabric API
register_fabric_api(app)

# Your existing routes
@app.route('/')
def home():
    return render_template('index.html')

# ... rest of your app

if __name__ == '__main__':
    app.run(debug=True, port=8080)
```

## Quick Examples

### Example 1: Find Fabrics for a Client

```python
from modules.fabric_processor import FabricProcessor
from pathlib import Path
import asyncio

async def find_fabrics():
    processor = FabricProcessor()

    # Load processed data
    chunks = processor.load_processed_data(
        Path('storage/fabrics/data/processed_latest.json')
    )

    # Search for suitable fabrics
    results = await processor.similarity_search(
        query="heavyweight winter fabric for formal suit",
        chunks=chunks,
        top_k=5
    )

    # Display results
    for chunk, score in results:
        print(f"Score: {score:.3f}")
        print(f"Fabric: {chunk.fabric_code}")
        print(f"Details: {chunk.content}")
        print("---")

asyncio.run(find_fabrics())
```

### Example 2: Generate Client Outfit

```python
from modules.outfit_generator import OutfitGenerator, OutfitSpec
import asyncio

async def generate_client_outfit():
    generator = OutfitGenerator()

    # Client preferences from HENK's H3 phase
    spec = OutfitSpec(
        occasion='wedding',
        season='summer',
        style_preferences=['modern', 'elegant'],
        color_preferences=['navy', 'light grey'],
        pattern_preferences=['subtle texture'],
        additional_notes='Groom outfit for beach wedding'
    )

    # Generate with automatic fabric selection via RAG
    outfit = await generator.generate_outfit(spec, use_rag=True)

    print(f"Generated: {outfit.outfit_id}")
    print(f"Prompt: {outfit.dalle_prompt}")
    print(f"Image: {outfit.local_image_path}")
    print(f"Fabrics: {outfit.fabrics_used}")

asyncio.run(generate_client_outfit())
```

### Example 3: Database Queries

```python
from database.db_manager import DatabaseManager

db = DatabaseManager()

# Get fabrics by season
summer_fabrics = db.get_fabrics_by_season('summer')
print(f"Found {len(summer_fabrics)} summer fabrics")

# Get specific fabric
fabric = db.get_fabric_by_code('34C4054')
print(fabric.to_dict())

# Vector search
from openai import OpenAI
client = OpenAI()

response = client.embeddings.create(
    model="text-embedding-3-small",
    input="navy wool for business suit",
    dimensions=1536
)

results = db.search_fabrics_by_vector(
    query_embedding=response.data[0].embedding,
    limit=5,
    threshold=0.7
)

for fabric, score in results:
    print(f"{fabric.fabric_code}: {score:.3f}")
```

## Troubleshooting

### Issue: Scraper fails to authenticate

**Solution**:
1. Verify credentials in `.env`
2. Run with headless mode off to debug:
   ```python
   # In fabric_config.py or .env
   SCRAPER_HEADLESS=false
   ```
3. Check if Formens website structure changed

### Issue: No embeddings generated

**Solution**:
1. Verify OpenAI API key: `echo $OPENAI_API_KEY`
2. Check OpenAI credits/limits
3. Look for errors in logs

### Issue: Database connection fails

**Solution**:
1. Check PostgreSQL is running: `pg_isready`
2. Verify DATABASE_URL format
3. Test connection: `psql $DATABASE_URL`
4. Check pgvector is installed: `psql -c "SELECT * FROM pg_extension WHERE extname = 'vector';"`

### Issue: Import fails

**Solution**:
1. Check Python path: `export PYTHONPATH=$PYTHONPATH:$(pwd)`
2. Verify __init__.py files exist
3. Check import statements match file structure

## Next Steps

1. **Automate Scraping**: Set up daily cron job
   ```bash
   0 2 * * * /path/to/python /path/to/modules/fabric_scraper.py
   ```

2. **Add Frontend**: Create UI for fabric search and outfit generation

3. **Enhance RAG**: Fine-tune similarity thresholds, add filters

4. **Monitor**: Set up logging and error tracking

5. **Scale**: Use Redis caching, optimize database queries

## Resources

- Full documentation: `FABRIC_MODULE_README.md`
- API documentation: See API Endpoints section
- Database schema: `database/fabric_migrations.sql`
- Configuration: `config/fabric_config.py`
- Tests: `python -m pytest tests/`

## Support

For issues or questions:
1. Check logs: `tail -f henk.log`
2. Review documentation
3. Run tests: `python -m pytest tests/ -v`
4. Contact development team

---

**Estimated Total Time**: 15 minutes
**Status**: ✅ Ready for development
