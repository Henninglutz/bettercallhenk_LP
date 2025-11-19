"""
HENK Fabric Module Tests
Unit tests for fabric scraping, processing, and RAG integration.
"""

import unittest
import asyncio
import json
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
import tempfile

from modules.fabric_scraper import FabricData, FormensScraper
from modules.fabric_processor import FabricProcessor, FabricChunk
from modules.outfit_generator import OutfitGenerator, OutfitSpec
from config.fabric_config import config


class TestFabricData(unittest.TestCase):
    """Test FabricData dataclass"""

    def test_fabric_data_creation(self):
        """Test creating FabricData"""
        fabric = FabricData(
            fabric_code="34C4054",
            name="Test Fabric",
            composition="100% Wool",
            weight=280,
            color="Navy"
        )

        self.assertEqual(fabric.fabric_code, "34C4054")
        self.assertEqual(fabric.name, "Test Fabric")
        self.assertEqual(fabric.weight, 280)

    def test_fabric_data_to_dict(self):
        """Test converting FabricData to dict"""
        fabric = FabricData(
            fabric_code="34C4054",
            name="Test Fabric"
        )

        data = fabric.to_dict()

        self.assertIsInstance(data, dict)
        self.assertEqual(data['fabric_code'], "34C4054")
        self.assertIn('scrape_date', data)

    def test_fabric_data_to_json(self):
        """Test converting FabricData to JSON"""
        fabric = FabricData(
            fabric_code="34C4054",
            name="Test Fabric"
        )

        json_str = fabric.to_json()

        self.assertIsInstance(json_str, str)
        parsed = json.loads(json_str)
        self.assertEqual(parsed['fabric_code'], "34C4054")


class TestFabricProcessor(unittest.TestCase):
    """Test FabricProcessor"""

    def setUp(self):
        """Set up test fixtures"""
        self.processor = FabricProcessor()

        self.test_fabric = FabricData(
            fabric_code="TEST001",
            name="Test Wool Fabric",
            composition="100% Wool",
            weight=280,
            color="Navy Blue",
            pattern="Solid",
            season=["fall", "winter"],
            category="business"
        )

    def test_create_fabric_chunks(self):
        """Test creating chunks from fabric data"""
        chunks = self.processor._create_fabric_chunks(self.test_fabric)

        self.assertGreater(len(chunks), 0)

        # Check chunk types
        chunk_types = [c.chunk_type for c in chunks]
        self.assertIn('characteristics', chunk_types)
        self.assertIn('visual', chunk_types)

    def test_chunk_content(self):
        """Test chunk content generation"""
        chunks = self.processor._create_fabric_chunks(self.test_fabric)

        # Find characteristics chunk
        char_chunk = next((c for c in chunks if c.chunk_type == 'characteristics'), None)
        self.assertIsNotNone(char_chunk)
        self.assertIn('TEST001', char_chunk.content)
        self.assertIn('Wool', char_chunk.content)

    def test_infer_composition(self):
        """Test composition inference"""
        fabric = FabricData(
            fabric_code="TEST002",
            name="Premium Wool Suit Fabric"
        )

        composition = self.processor._infer_composition(fabric)
        self.assertIsNotNone(composition)
        self.assertIn('Wool', composition)

    def test_categorize_weight(self):
        """Test weight categorization"""
        self.assertEqual(
            self.processor._categorize_weight(200),
            "Lightweight"
        )
        self.assertEqual(
            self.processor._categorize_weight(300),
            "Medium"
        )
        self.assertEqual(
            self.processor._categorize_weight(400),
            "Heavyweight"
        )

    def test_infer_seasons_from_weight(self):
        """Test season inference from weight"""
        # Lightweight
        seasons = self.processor._infer_seasons_from_weight(200)
        self.assertIn('summer', seasons)

        # Heavyweight
        seasons = self.processor._infer_seasons_from_weight(400)
        self.assertIn('winter', seasons)

    def test_generate_care_instructions(self):
        """Test care instructions generation"""
        fabric = FabricData(
            fabric_code="TEST003",
            composition="100% Wool"
        )

        care = self.processor._generate_care_instructions(fabric)
        self.assertIsNotNone(care)
        self.assertIn('dry clean', care.lower())

    @unittest.skipIf(not config.is_openai_configured(), "OpenAI not configured")
    def test_generate_embeddings(self):
        """Test embedding generation (requires OpenAI)"""
        chunks = self.processor._create_fabric_chunks(self.test_fabric)

        # Run async test
        async def run_test():
            embedded_chunks = await self.processor._generate_embeddings(chunks)
            self.assertEqual(len(embedded_chunks), len(chunks))

            if embedded_chunks:
                self.assertIsNotNone(embedded_chunks[0].embedding)
                self.assertEqual(
                    len(embedded_chunks[0].embedding),
                    config.OPENAI_EMBEDDING_DIMENSIONS
                )

        asyncio.run(run_test())


class TestOutfitGenerator(unittest.TestCase):
    """Test OutfitGenerator"""

    def setUp(self):
        """Set up test fixtures"""
        self.generator = OutfitGenerator()

        self.test_spec = OutfitSpec(
            occasion="wedding",
            season="summer",
            style_preferences=["classic", "elegant"],
            color_preferences=["navy", "light blue"],
            pattern_preferences=["solid"]
        )

        self.test_fabric = FabricData(
            fabric_code="TEST001",
            composition="100% Wool",
            weight=250,
            color="Navy",
            pattern="Solid",
            season=["summer"]
        )

    def test_outfit_spec_creation(self):
        """Test creating OutfitSpec"""
        spec = OutfitSpec(
            occasion="wedding",
            season="summer",
            style_preferences=["classic"]
        )

        self.assertEqual(spec.occasion, "wedding")
        self.assertEqual(spec.season, "summer")

    def test_build_dalle_prompt(self):
        """Test DALL-E prompt generation"""
        prompt = self.generator._build_dalle_prompt(self.test_spec)

        self.assertIsInstance(prompt, str)
        self.assertIn("wedding", prompt.lower())
        self.assertIn("summer", prompt.lower())
        self.assertLess(len(prompt), 1000)  # Check length limit

    def test_fabric_to_description(self):
        """Test fabric to description conversion"""
        desc = self.generator._fabric_to_description(self.test_fabric)

        self.assertIsInstance(desc, str)
        self.assertIn("wool", desc.lower())

    def test_get_occasion_description(self):
        """Test occasion description"""
        desc = self.generator._get_occasion_description("wedding")
        self.assertIn("wedding", desc.lower())

        desc = self.generator._get_occasion_description("business")
        self.assertIn("business", desc.lower())

    def test_get_season_description(self):
        """Test season description"""
        desc = self.generator._get_season_description("summer")
        self.assertIn("summer", desc.lower())

    def test_create_variant_spec(self):
        """Test variant spec creation"""
        variant = self.generator._create_variant_spec(self.test_spec, 0)

        self.assertEqual(variant.occasion, self.test_spec.occasion)
        self.assertEqual(variant.season, self.test_spec.season)
        # Style preferences should be modified
        self.assertNotEqual(variant.style_preferences, self.test_spec.style_preferences)

    def test_generate_outfit_id(self):
        """Test outfit ID generation"""
        outfit_id = self.generator._generate_outfit_id(self.test_spec)

        self.assertIsInstance(outfit_id, str)
        self.assertTrue(outfit_id.startswith("OUTFIT_"))


class TestFabricScraper(unittest.TestCase):
    """Test FabricScraper"""

    def test_extract_fabric_code(self):
        """Test fabric code extraction from text"""
        import re

        text = "Premium fabric 34C4054 in navy color"
        match = re.search(r'\b([A-Z0-9]{6,8})\b', text)

        self.assertIsNotNone(match)
        self.assertEqual(match.group(1), "34C4054")

    def test_image_url_construction(self):
        """Test image URL construction"""
        fabric_code = "34C4054"
        category = "Ceremony Suits"
        base_url = "https://b2b2.formens.ro/documente/marketing"

        expected_url = f"{base_url}/{category}/05._{fabric_code}.jpg"

        self.assertIn(fabric_code, expected_url)
        self.assertTrue(expected_url.startswith("https://"))


class TestDatabaseIntegration(unittest.TestCase):
    """Test database integration (requires DATABASE_URL)"""

    @unittest.skipIf(not config.is_database_configured(), "Database not configured")
    def test_database_connection(self):
        """Test database connection"""
        from database.db_manager import DatabaseManager

        db = DatabaseManager()
        self.assertIsNotNone(db.engine)

    @unittest.skipIf(not config.is_database_configured(), "Database not configured")
    def test_get_stats(self):
        """Test getting database stats"""
        from database.db_manager import DatabaseManager

        db = DatabaseManager()
        stats = db.get_stats()

        self.assertIsInstance(stats, dict)
        self.assertIn('total_fabrics', stats)


class TestConfiguration(unittest.TestCase):
    """Test configuration"""

    def test_config_loading(self):
        """Test config loads properly"""
        self.assertIsNotNone(config)
        self.assertIsNotNone(config.FORMENS_BASE_URL)

    def test_storage_paths(self):
        """Test storage paths are created"""
        self.assertTrue(Path(config.FABRIC_STORAGE_PATH).exists())
        self.assertTrue(Path(config.FABRIC_IMAGE_STORAGE).exists())

    def test_fabric_categories(self):
        """Test fabric categories are defined"""
        from config.fabric_config import FABRIC_CATEGORIES

        self.assertGreater(len(FABRIC_CATEGORIES), 0)
        self.assertIn('ceremony', FABRIC_CATEGORIES)


def run_tests():
    """Run all tests"""
    unittest.main(verbosity=2)


if __name__ == "__main__":
    run_tests()
