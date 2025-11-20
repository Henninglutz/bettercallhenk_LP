"""
HENK Database Manager
Manages database connections and provides utility functions for fabric data.
"""

import logging
from contextlib import contextmanager
from typing import List, Optional, Dict, Any, Tuple
import json
from pathlib import Path

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool
import numpy as np

from config.fabric_config import config
from database.models import (
    Base, Fabric, FabricSeason, FabricImage, FabricCategory,
    FabricEmbedding, GeneratedOutfit, OutfitFabric, FabricRecommendation
)
from modules.fabric_scraper import FabricData
from modules.fabric_processor import FabricChunk

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format=config.LOG_FORMAT
)
logger = logging.getLogger(__name__)


class DatabaseManager:
    """
    Manages database connections and provides high-level operations
    for fabric data storage and retrieval.
    """

    def __init__(self, database_url: Optional[str] = None):
        """
        Initialize database manager.

        Args:
            database_url: PostgreSQL connection string (uses config if not provided)
        """
        self.database_url = database_url or config.DATABASE_URL

        if not self.database_url:
            raise ValueError("Database URL not configured. Set DATABASE_URL in .env")

        # Create engine
        self.engine = create_engine(
            self.database_url,
            pool_size=config.DB_POOL_SIZE,
            max_overflow=config.DB_MAX_OVERFLOW,
            pool_timeout=config.DB_POOL_TIMEOUT,
            echo=False  # Set to True for SQL debugging
        )

        # Create session factory
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )

        logger.info("Database manager initialized")

    def create_tables(self):
        """Create all tables in database"""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Error creating tables: {str(e)}")
            raise

    def drop_tables(self):
        """Drop all tables (use with caution!)"""
        try:
            Base.metadata.drop_all(bind=self.engine)
            logger.warning("Database tables dropped")
        except Exception as e:
            logger.error(f"Error dropping tables: {str(e)}")
            raise

    @contextmanager
    def get_session(self) -> Session:
        """
        Get database session context manager.

        Usage:
            with db_manager.get_session() as session:
                # Use session
                pass
        """
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Session error: {str(e)}")
            raise
        finally:
            session.close()

    def save_fabric(self, fabric_data: FabricData, session: Optional[Session] = None) -> Fabric:
        """
        Save fabric data to database.

        Args:
            fabric_data: FabricData object
            session: Optional existing session

        Returns:
            Fabric database model
        """
        def _save(sess: Session) -> Fabric:
            # Check if fabric already exists
            existing = sess.query(Fabric).filter_by(fabric_code=fabric_data.fabric_code).first()

            if existing:
                # Update existing
                logger.info(f"Updating existing fabric {fabric_data.fabric_code}")
                fabric = existing
            else:
                # Create new
                logger.info(f"Creating new fabric {fabric_data.fabric_code}")
                fabric = Fabric()

            # Update fields
            fabric.fabric_code = fabric_data.fabric_code
            fabric.name = fabric_data.name
            fabric.composition = fabric_data.composition
            fabric.weight = fabric_data.weight
            fabric.color = fabric_data.color
            fabric.pattern = fabric_data.pattern
            fabric.price_category = fabric_data.price_category
            fabric.stock_status = fabric_data.stock_status
            fabric.supplier = fabric_data.supplier
            fabric.origin = fabric_data.origin
            fabric.description = fabric_data.description
            fabric.care_instructions = fabric_data.care_instructions
            fabric.category = fabric_data.category
            fabric.scrape_date = fabric_data.scrape_date
            fabric.additional_metadata = fabric_data.additional_metadata or {}

            if not existing:
                sess.add(fabric)
                sess.flush()  # Get ID

            # Save seasons
            if fabric_data.season:
                # Remove old seasons
                sess.query(FabricSeason).filter_by(fabric_id=fabric.id).delete()

                for season in fabric_data.season:
                    fabric_season = FabricSeason(
                        fabric_id=fabric.id,
                        season=season
                    )
                    sess.add(fabric_season)

            # Save images
            if fabric_data.local_image_paths:
                # Remove old images
                sess.query(FabricImage).filter_by(fabric_id=fabric.id).delete()

                for i, local_path in enumerate(fabric_data.local_image_paths):
                    image_url = fabric_data.image_urls[i] if i < len(fabric_data.image_urls) else None

                    fabric_image = FabricImage(
                        fabric_id=fabric.id,
                        image_url=image_url,
                        local_path=local_path,
                        image_type='primary' if i == 0 else 'additional'
                    )
                    sess.add(fabric_image)

            sess.commit()
            return fabric

        if session:
            return _save(session)
        else:
            with self.get_session() as sess:
                return _save(sess)

    def save_fabrics_batch(self, fabrics: List[FabricData]) -> int:
        """
        Save multiple fabrics in a batch.

        Args:
            fabrics: List of FabricData objects

        Returns:
            Number of fabrics saved
        """
        with self.get_session() as session:
            count = 0
            for fabric_data in fabrics:
                try:
                    self.save_fabric(fabric_data, session)
                    count += 1
                except Exception as e:
                    logger.error(f"Error saving fabric {fabric_data.fabric_code}: {str(e)}")
                    continue

            logger.info(f"Saved {count}/{len(fabrics)} fabrics to database")
            return count

    def save_embedding(self, chunk: FabricChunk, session: Optional[Session] = None) -> FabricEmbedding:
        """
        Save fabric embedding to database.

        Args:
            chunk: FabricChunk with embedding
            session: Optional existing session

        Returns:
            FabricEmbedding database model
        """
        def _save(sess: Session) -> FabricEmbedding:
            # Get fabric
            fabric = sess.query(Fabric).filter_by(fabric_code=chunk.fabric_code).first()
            if not fabric:
                raise ValueError(f"Fabric {chunk.fabric_code} not found in database")

            # Check if embedding exists
            existing = sess.query(FabricEmbedding).filter_by(chunk_id=chunk.chunk_id).first()

            if existing:
                embedding = existing
            else:
                embedding = FabricEmbedding()

            # Update fields
            embedding.fabric_id = fabric.id
            embedding.chunk_id = chunk.chunk_id
            embedding.chunk_type = chunk.chunk_type
            embedding.content = chunk.content
            embedding.embedding = chunk.embedding
            embedding.embedding_metadata = chunk.metadata

            if not existing:
                sess.add(embedding)

            sess.commit()
            return embedding

        if session:
            return _save(session)
        else:
            with self.get_session() as sess:
                return _save(sess)

    def save_embeddings_batch(self, chunks: List[FabricChunk]) -> int:
        """
        Save multiple embeddings in a batch.

        Args:
            chunks: List of FabricChunk objects

        Returns:
            Number of embeddings saved
        """
        with self.get_session() as session:
            count = 0
            for chunk in chunks:
                try:
                    self.save_embedding(chunk, session)
                    count += 1
                except Exception as e:
                    logger.error(f"Error saving embedding {chunk.chunk_id}: {str(e)}")
                    continue

            logger.info(f"Saved {count}/{len(chunks)} embeddings to database")
            return count

    def search_fabrics_by_vector(
        self,
        query_embedding: List[float],
        limit: int = 5,
        threshold: float = 0.7
    ) -> List[Tuple[Fabric, float]]:
        """
        Search fabrics by vector similarity.

        Args:
            query_embedding: Query vector
            limit: Maximum results
            threshold: Minimum similarity score

        Returns:
            List of (Fabric, similarity_score) tuples
        """
        with self.get_session() as session:
            # Use cosine distance (1 - cosine similarity)
            # pgvector <=> operator returns cosine distance
            query = text("""
                SELECT DISTINCT ON (f.id)
                    f.*,
                    1 - (fe.embedding <=> :embedding) AS similarity
                FROM fabrics f
                JOIN fabric_embeddings fe ON f.id = fe.fabric_id
                WHERE 1 - (fe.embedding <=> :embedding) >= :threshold
                ORDER BY f.id, fe.embedding <=> :embedding
                LIMIT :limit
            """)

            results = session.execute(
                query,
                {
                    'embedding': query_embedding,
                    'threshold': threshold,
                    'limit': limit
                }
            ).fetchall()

            # Convert to Fabric objects
            fabrics_with_scores = []
            for row in results:
                fabric = session.query(Fabric).get(row.id)
                if fabric:
                    fabrics_with_scores.append((fabric, float(row.similarity)))

            return fabrics_with_scores

    def get_fabric_by_code(self, fabric_code: str) -> Optional[Fabric]:
        """Get fabric by code"""
        with self.get_session() as session:
            return session.query(Fabric).filter_by(fabric_code=fabric_code).first()

    def get_all_fabrics(self, limit: Optional[int] = None) -> List[Fabric]:
        """Get all fabrics"""
        with self.get_session() as session:
            query = session.query(Fabric)
            if limit:
                query = query.limit(limit)
            return query.all()

    def get_fabrics_by_category(self, category: str) -> List[Fabric]:
        """Get fabrics by category"""
        with self.get_session() as session:
            return session.query(Fabric).filter_by(category=category).all()

    def get_fabrics_by_season(self, season: str) -> List[Fabric]:
        """Get fabrics by season"""
        with self.get_session() as session:
            return session.query(Fabric).join(FabricSeason).filter(
                FabricSeason.season == season
            ).all()

    def import_from_json(self, json_path: Path) -> int:
        """
        Import fabric data from JSON file.

        Args:
            json_path: Path to JSON file

        Returns:
            Number of fabrics imported
        """
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            fabrics = [FabricData(**fabric_dict) for fabric_dict in data.get('fabrics', [])]

            count = self.save_fabrics_batch(fabrics)
            logger.info(f"Imported {count} fabrics from {json_path}")

            return count

        except Exception as e:
            logger.error(f"Error importing from JSON: {str(e)}")
            return 0

    def import_embeddings_from_json(self, json_path: Path) -> int:
        """
        Import embeddings from JSON file.

        Args:
            json_path: Path to processed JSON file

        Returns:
            Number of embeddings imported
        """
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            chunks = []
            for chunk_data in data.get('chunks', []):
                chunk = FabricChunk(
                    fabric_code=chunk_data['fabric_code'],
                    chunk_id=chunk_data['chunk_id'],
                    content=chunk_data['content'],
                    chunk_type=chunk_data['chunk_type'],
                    metadata=chunk_data['metadata'],
                    embedding=chunk_data.get('embedding')
                )
                chunks.append(chunk)

            count = self.save_embeddings_batch(chunks)
            logger.info(f"Imported {count} embeddings from {json_path}")

            return count

        except Exception as e:
            logger.error(f"Error importing embeddings: {str(e)}")
            return 0

    def get_stats(self) -> Dict[str, int]:
        """Get database statistics"""
        with self.get_session() as session:
            stats = {
                'total_fabrics': session.query(Fabric).count(),
                'total_embeddings': session.query(FabricEmbedding).count(),
                'total_images': session.query(FabricImage).count(),
                'total_outfits': session.query(GeneratedOutfit).count(),
                'total_categories': session.query(FabricCategory).count()
            }

            return stats


def main():
    """Example usage and testing"""
    try:
        # Initialize database manager
        db = DatabaseManager()

        # Create tables
        logger.info("Creating database tables...")
        db.create_tables()

        # Get stats
        stats = db.get_stats()
        logger.info(f"Database stats: {stats}")

        # Import data if available
        fabrics_path = Path(config.FABRIC_DATA_STORAGE) / "fabrics_latest.json"
        if fabrics_path.exists():
            logger.info(f"Importing fabrics from {fabrics_path}")
            count = db.import_from_json(fabrics_path)
            logger.info(f"Imported {count} fabrics")

        # Import embeddings if available
        embeddings_path = Path(config.FABRIC_DATA_STORAGE) / "processed_latest.json"
        if embeddings_path.exists():
            logger.info(f"Importing embeddings from {embeddings_path}")
            count = db.import_embeddings_from_json(embeddings_path)
            logger.info(f"Imported {count} embeddings")

        # Get updated stats
        stats = db.get_stats()
        logger.info(f"Updated database stats: {stats}")

    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise


if __name__ == "__main__":
    main()
