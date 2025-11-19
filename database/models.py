"""
HENK Fabric Database Models
SQLAlchemy models for fabric data and RAG system.
"""

from datetime import datetime
from typing import List, Optional
import uuid

from sqlalchemy import (
    Column, String, Integer, Text, TIMESTAMP, ForeignKey,
    CheckConstraint, UniqueConstraint, Float, ARRAY
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector

Base = declarative_base()


class Fabric(Base):
    """Core fabric information"""
    __tablename__ = 'fabrics'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    fabric_code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(255))
    composition = Column(Text, index=True)
    weight = Column(Integer, CheckConstraint('weight > 0'))  # grams/m²
    color = Column(String(100), index=True)
    pattern = Column(String(100), index=True)
    price_category = Column(String(50))
    stock_status = Column(String(50), index=True)
    supplier = Column(String(100), default='Formens', index=True)
    origin = Column(String(100))
    description = Column(Text)
    care_instructions = Column(Text)
    category = Column(String(100), index=True)

    # Metadata
    scrape_date = Column(TIMESTAMP(timezone=True))
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)
    updated_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    additional_metadata = Column(JSONB, default={})

    # Relationships
    seasons = relationship('FabricSeason', back_populates='fabric', cascade='all, delete-orphan')
    images = relationship('FabricImage', back_populates='fabric', cascade='all, delete-orphan')
    embeddings = relationship('FabricEmbedding', back_populates='fabric', cascade='all, delete-orphan')
    outfit_fabrics = relationship('OutfitFabric', back_populates='fabric')

    def __repr__(self):
        return f"<Fabric(code={self.fabric_code}, name={self.name})>"

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': str(self.id),
            'fabric_code': self.fabric_code,
            'name': self.name,
            'composition': self.composition,
            'weight': self.weight,
            'color': self.color,
            'pattern': self.pattern,
            'price_category': self.price_category,
            'stock_status': self.stock_status,
            'supplier': self.supplier,
            'origin': self.origin,
            'description': self.description,
            'care_instructions': self.care_instructions,
            'category': self.category,
            'scrape_date': self.scrape_date.isoformat() if self.scrape_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'additional_metadata': self.additional_metadata,
            'seasons': [s.season for s in self.seasons] if self.seasons else [],
            'images': [img.to_dict() for img in self.images] if self.images else []
        }


class FabricSeason(Base):
    """Fabric seasons mapping"""
    __tablename__ = 'fabric_seasons'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    fabric_id = Column(UUID(as_uuid=True), ForeignKey('fabrics.id', ondelete='CASCADE'), nullable=False)
    season = Column(
        String(20),
        CheckConstraint("season IN ('spring', 'summer', 'fall', 'winter')"),
        nullable=False
    )
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)

    # Relationships
    fabric = relationship('Fabric', back_populates='seasons')

    __table_args__ = (
        UniqueConstraint('fabric_id', 'season', name='uq_fabric_season'),
    )

    def __repr__(self):
        return f"<FabricSeason(fabric_id={self.fabric_id}, season={self.season})>"


class FabricImage(Base):
    """Fabric images"""
    __tablename__ = 'fabric_images'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    fabric_id = Column(UUID(as_uuid=True), ForeignKey('fabrics.id', ondelete='CASCADE'), nullable=False, index=True)
    image_url = Column(Text)
    local_path = Column(Text)
    image_type = Column(String(50), index=True)  # 'primary', 'detail', 'texture'
    width = Column(Integer)
    height = Column(Integer)
    file_size = Column(Integer)  # bytes
    format = Column(String(10))  # 'JPEG', 'PNG'

    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)
    updated_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    fabric = relationship('Fabric', back_populates='images')

    def __repr__(self):
        return f"<FabricImage(fabric_id={self.fabric_id}, type={self.image_type})>"

    def to_dict(self):
        return {
            'id': str(self.id),
            'fabric_id': str(self.fabric_id),
            'image_url': self.image_url,
            'local_path': self.local_path,
            'image_type': self.image_type,
            'width': self.width,
            'height': self.height,
            'file_size': self.file_size,
            'format': self.format
        }


class FabricCategory(Base):
    """Fabric categories"""
    __tablename__ = 'fabric_categories'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), unique=True, nullable=False)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text)
    parent_id = Column(UUID(as_uuid=True), ForeignKey('fabric_categories.id', ondelete='SET NULL'))
    occasions = Column(JSONB, default=[])

    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)
    updated_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Self-referential relationship
    parent = relationship('FabricCategory', remote_side=[id], backref='children')

    def __repr__(self):
        return f"<FabricCategory(name={self.name}, slug={self.slug})>"

    def to_dict(self):
        return {
            'id': str(self.id),
            'name': self.name,
            'slug': self.slug,
            'description': self.description,
            'parent_id': str(self.parent_id) if self.parent_id else None,
            'occasions': self.occasions
        }


class FabricEmbedding(Base):
    """Fabric embeddings for RAG"""
    __tablename__ = 'fabric_embeddings'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    fabric_id = Column(UUID(as_uuid=True), ForeignKey('fabrics.id', ondelete='CASCADE'), nullable=False, index=True)
    chunk_id = Column(String(255), unique=True, nullable=False)
    chunk_type = Column(
        String(50),
        CheckConstraint("chunk_type IN ('characteristics', 'visual', 'usage', 'technical')"),
        nullable=False,
        index=True
    )
    content = Column(Text, nullable=False)

    # Vector embedding (1536 dimensions for text-embedding-3-small)
    embedding = Column(Vector(1536))

    metadata = Column(JSONB, default={})

    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)
    updated_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    fabric = relationship('Fabric', back_populates='embeddings')

    def __repr__(self):
        return f"<FabricEmbedding(chunk_id={self.chunk_id}, type={self.chunk_type})>"

    def to_dict(self):
        return {
            'id': str(self.id),
            'fabric_id': str(self.fabric_id),
            'chunk_id': self.chunk_id,
            'chunk_type': self.chunk_type,
            'content': self.content,
            'metadata': self.metadata,
            'embedding': self.embedding.tolist() if self.embedding else None
        }


class GeneratedOutfit(Base):
    """DALL-E generated outfits"""
    __tablename__ = 'generated_outfits'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    outfit_id = Column(String(100), unique=True, nullable=False, index=True)

    # Specification
    occasion = Column(String(100), nullable=False, index=True)
    season = Column(String(20), nullable=False, index=True)
    style_preferences = Column(JSONB, default=[])
    color_preferences = Column(JSONB, default=[])
    pattern_preferences = Column(JSONB, default=[])
    additional_notes = Column(Text)

    # Generation details
    dalle_prompt = Column(Text, nullable=False)
    revised_prompt = Column(Text)
    image_url = Column(Text)
    local_image_path = Column(Text)

    # Metadata
    generation_metadata = Column(JSONB, default={})
    generated_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, index=True)
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)

    # Relationships
    outfit_fabrics = relationship('OutfitFabric', back_populates='outfit', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<GeneratedOutfit(outfit_id={self.outfit_id}, occasion={self.occasion})>"

    def to_dict(self):
        return {
            'id': str(self.id),
            'outfit_id': self.outfit_id,
            'occasion': self.occasion,
            'season': self.season,
            'style_preferences': self.style_preferences,
            'color_preferences': self.color_preferences,
            'pattern_preferences': self.pattern_preferences,
            'additional_notes': self.additional_notes,
            'dalle_prompt': self.dalle_prompt,
            'revised_prompt': self.revised_prompt,
            'image_url': self.image_url,
            'local_image_path': self.local_image_path,
            'generation_metadata': self.generation_metadata,
            'generated_at': self.generated_at.isoformat() if self.generated_at else None,
            'fabrics': [of.to_dict() for of in self.outfit_fabrics] if self.outfit_fabrics else []
        }


class OutfitFabric(Base):
    """Outfits to fabrics mapping"""
    __tablename__ = 'outfit_fabrics'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    outfit_id = Column(UUID(as_uuid=True), ForeignKey('generated_outfits.id', ondelete='CASCADE'), nullable=False, index=True)
    fabric_id = Column(UUID(as_uuid=True), ForeignKey('fabrics.id', ondelete='CASCADE'), nullable=False, index=True)
    usage_type = Column(String(50))  # 'jacket', 'trousers', 'vest'
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)

    # Relationships
    outfit = relationship('GeneratedOutfit', back_populates='outfit_fabrics')
    fabric = relationship('Fabric', back_populates='outfit_fabrics')

    __table_args__ = (
        UniqueConstraint('outfit_id', 'fabric_id', 'usage_type', name='uq_outfit_fabric_usage'),
    )

    def __repr__(self):
        return f"<OutfitFabric(outfit_id={self.outfit_id}, fabric_id={self.fabric_id})>"

    def to_dict(self):
        return {
            'id': str(self.id),
            'outfit_id': str(self.outfit_id),
            'fabric_id': str(self.fabric_id),
            'fabric_code': self.fabric.fabric_code if self.fabric else None,
            'usage_type': self.usage_type
        }


class FabricRecommendation(Base):
    """Fabric recommendations tracking"""
    __tablename__ = 'fabric_recommendations'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(String(255), index=True)
    user_query = Column(Text, nullable=False)
    query_embedding = Column(Vector(1536))

    # Results
    recommended_fabrics = Column(JSONB, default=[])  # Array of {fabric_id, score}

    # Feedback
    user_feedback = Column(Integer, CheckConstraint('user_feedback BETWEEN 1 AND 5'))
    selected_fabric_id = Column(UUID(as_uuid=True), ForeignKey('fabrics.id', ondelete='SET NULL'))

    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, index=True)

    # Relationships
    selected_fabric = relationship('Fabric', foreign_keys=[selected_fabric_id])

    def __repr__(self):
        return f"<FabricRecommendation(session={self.session_id}, query={self.user_query[:50]})>"

    def to_dict(self):
        return {
            'id': str(self.id),
            'session_id': self.session_id,
            'user_query': self.user_query,
            'recommended_fabrics': self.recommended_fabrics,
            'user_feedback': self.user_feedback,
            'selected_fabric_id': str(self.selected_fabric_id) if self.selected_fabric_id else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
