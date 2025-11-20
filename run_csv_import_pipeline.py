"""
CSV Import Pipeline
Complete workflow: CSV Import → Image Download → RAG Processing → Database Import
"""

import asyncio
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from modules.fabric_csv_importer import FabricCSVImporter
from modules.fabric_processor import FabricProcessor
from database.db_manager import DatabaseManager
from config.fabric_config import config

import logging

logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format=config.LOG_FORMAT
)
logger = logging.getLogger(__name__)


async def csv_import_pipeline(csv_path: str):
    """Complete CSV import pipeline"""

    print("=" * 70)
    print("HENK FABRIC CSV IMPORT PIPELINE")
    print("=" * 70)
    print()

    # Step 1: Import CSV and download images
    print("📥 STEP 1/4: Importing CSV and downloading images...")
    async with FabricCSVImporter() as importer:
        stats = await importer.import_csv(csv_path)
        json_output = stats['output_file']

    print(f"✅ Imported {stats['total_fabrics']} fabrics")
    print(f"✅ Downloaded {stats['images_downloaded']} images")
    print()

    # Step 2: Process with RAG
    print("🧠 STEP 2/4: Generating RAG embeddings...")
    import json

    with open(json_output, 'r', encoding='utf-8') as f:
        fabrics = json.load(f)

    processor = FabricProcessor()
    processed_chunks = await processor.process_batch(fabrics)

    print(f"✅ Generated {len(processed_chunks)} embeddings")
    print()

    # Step 3: Import to database
    print("💾 STEP 3/4: Importing to database...")
    db = DatabaseManager()

    # Import fabrics
    imported_count = 0
    for fabric in fabrics:
        try:
            db.save_fabric(fabric)
            imported_count += 1
        except Exception as e:
            logger.error(f"Error importing fabric {fabric.get('fabric_code')}: {e}")

    # Import embeddings
    embeddings_imported = 0
    for chunk in processed_chunks:
        try:
            # Find fabric by code
            fabric_data = next(
                (f for f in fabrics if f['fabric_code'] == chunk.fabric_code),
                None
            )
            if fabric_data:
                db.save_embedding(fabric_data, chunk)
                embeddings_imported += 1
        except Exception as e:
            logger.error(f"Error importing embedding: {e}")

    print(f"✅ Imported {imported_count} fabrics and {embeddings_imported} embeddings")
    print()

    # Step 4: Statistics
    print("📊 STEP 4/4: Final Statistics...")
    try:
        db_stats = db.get_stats()
        print(f"Total fabrics in database: {db_stats.get('total_fabrics', 0)}")
        print(f"Total embeddings: {db_stats.get('total_embeddings', 0)}")
        print(f"Fabrics with images: {db_stats.get('fabrics_with_images', 0)}")
    except Exception as e:
        logger.warning(f"Could not fetch database stats: {e}")

    print()
    print("=" * 70)
    print("✅ CSV IMPORT PIPELINE COMPLETE!")
    print("=" * 70)
    print()
    print("Next steps:")
    print("1. Verify data in database")
    print("2. Test RAG search: python -m tests.test_rag_search")
    print("3. Ready for H1-H3 integration!")
    print()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python run_csv_import_pipeline.py <path_to_csv>")
        print()
        print("Example:")
        print("  python run_csv_import_pipeline.py ~/Schreibtisch/fabrics_export_v1.csv")
        print()
        sys.exit(1)

    csv_path = sys.argv[1]

    if not os.path.exists(csv_path):
        print(f"❌ Error: CSV file not found: {csv_path}")
        sys.exit(1)

    asyncio.run(csv_import_pipeline(csv_path))
