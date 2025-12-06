"""Database models for storing research papers"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

Base = declarative_base()


class Paper(Base):
    """Research paper model"""
    
    __tablename__ = "papers"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Identifiers
    title = Column(String(500), nullable=False, index=True)
    paper_id = Column(String(100), unique=True, index=True)  # Scholar ID or arXiv ID
    source = Column(String(50))  # 'scholar' or 'arxiv'
    
    # Authors and affiliations
    authors = Column(Text)  # JSON string or comma-separated
    first_author = Column(String(200))
    
    # Publication details
    year = Column(Integer, index=True)
    publication_date = Column(DateTime)
    venue = Column(String(300))  # Journal or conference
    publisher = Column(String(200))
    
    # Content
    abstract = Column(Text)
    url = Column(String(500))
    pdf_url = Column(String(500))
    
    # Metrics
    citation_count = Column(Integer, default=0)
    
    # AI-generated content (Phase 2)
    summary_zh = Column(Text)  # Chinese summary
    investment_insights = Column(Text)  # Investment analysis
    keywords = Column(Text)  # Extracted keywords
    
    # Metadata
    fetched_at = Column(DateTime, default=datetime.utcnow, index=True)
    processed = Column(Boolean, default=False)
    published = Column(Boolean, default=False)
    
    def __repr__(self):
        return f"<Paper(id={self.id}, title='{self.title[:50]}...', year={self.year})>"
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "title": self.title,
            "paper_id": self.paper_id,
            "source": self.source,
            "authors": self.authors,
            "first_author": self.first_author,
            "year": self.year,
            "publication_date": self.publication_date.isoformat() if self.publication_date else None,
            "venue": self.venue,
            "abstract": self.abstract,
            "url": self.url,
            "pdf_url": self.pdf_url,
            "citation_count": self.citation_count,
            "summary_zh": self.summary_zh,
            "keywords": self.keywords,
            "fetched_at": self.fetched_at.isoformat() if self.fetched_at else None,
            "processed": self.processed,
            "published": self.published
        }


def init_database(database_url: str):
    """Initialize database and create tables"""
    engine = create_engine(database_url)
    Base.metadata.create_all(engine)
    return engine


def get_session(engine):
    """Get database session"""
    Session = sessionmaker(bind=engine)
    return Session()
