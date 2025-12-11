"""Tests for database models"""
import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.database.models import Base, Paper, init_database, get_session


class TestPaper:
    """Test Paper model"""
    
    @pytest.fixture
    def db_session(self):
        """Create in-memory database for testing"""
        engine = create_engine('sqlite:///:memory:')
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        yield session
        session.close()
    
    def test_paper_creation(self, db_session):
        """Test creating a Paper instance"""
        paper = Paper(
            title="Test Paper",
            paper_id="test123",
            source="arxiv",
            authors="John Doe, Jane Smith",
            year=2024,
            abstract="Test abstract",
            citation_count=10
        )
        db_session.add(paper)
        db_session.commit()
        
        assert paper.id is not None
        assert paper.title == "Test Paper"
        assert paper.paper_id == "test123"
        assert paper.source == "arxiv"
        assert paper.citation_count == 10
    
    def test_paper_default_values(self, db_session):
        """Test Paper default values"""
        paper = Paper(
            title="Test",
            paper_id="test"
        )
        db_session.add(paper)
        db_session.commit()
        
        assert paper.citation_count == 0
        assert paper.processed is False
        assert paper.published is False
        assert paper.fetched_at is not None
    
    def test_paper_repr(self, db_session):
        """Test Paper __repr__ method"""
        paper = Paper(
            title="A" * 100,
            paper_id="test",
            year=2024
        )
        repr_str = repr(paper)
        
        assert "Paper" in repr_str
        assert "year=2024" in repr_str
        assert len(repr_str) < 200  # Title should be truncated
    
    def test_paper_to_dict(self, db_session):
        """Test Paper to_dict method"""
        now = datetime.utcnow()
        paper = Paper(
            title="Test Paper",
            paper_id="test123",
            source="arxiv",
            authors="John Doe",
            year=2024,
            abstract="Abstract",
            citation_count=5,
            processed=True,
            published=False,
            fetched_at=now
        )
        
        paper_dict = paper.to_dict()
        
        assert isinstance(paper_dict, dict)
        assert paper_dict['title'] == "Test Paper"
        assert paper_dict['paper_id'] == "test123"
        assert paper_dict['source'] == "arxiv"
        assert paper_dict['citation_count'] == 5
        assert paper_dict['processed'] is True
        assert paper_dict['published'] is False
        assert 'fetched_at' in paper_dict
    
    def test_paper_all_fields(self, db_session):
        """Test Paper with all fields populated"""
        pub_date = datetime(2024, 1, 15)
        fetched = datetime.utcnow()
        
        paper = Paper(
            title="Complete Test Paper",
            paper_id="complete123",
            source="semantic_scholar",
            authors="Author One, Author Two",
            first_author="Author One",
            year=2024,
            publication_date=pub_date,
            venue="Test Conference",
            publisher="Test Publisher",
            abstract="Full abstract text",
            url="https://example.com",
            pdf_url="https://example.com/pdf",
            doi="10.1234/test",
            citation_count=100,
            influential_citation_count=20,
            summary_zh="中文摘要",
            investment_insights="投资洞察",
            keywords="AI, ML",
            fetched_at=fetched,
            processed=True,
            published=True
        )
        
        db_session.add(paper)
        db_session.commit()
        
        assert paper.first_author == "Author One"
        assert paper.venue == "Test Conference"
        assert paper.publisher == "Test Publisher"
        assert paper.doi == "10.1234/test"
        assert paper.influential_citation_count == 20
        assert paper.summary_zh == "中文摘要"
        assert paper.keywords == "AI, ML"


class TestDatabaseFunctions:
    """Test database utility functions"""
    
    def test_init_database(self, tmp_path):
        """Test init_database function"""
        db_path = tmp_path / "test.db"
        db_url = f"sqlite:///{db_path}"
        
        engine = init_database(db_url)
        
        assert engine is not None
        assert db_path.exists()
    
    def test_get_session(self, tmp_path):
        """Test get_session function"""
        db_path = tmp_path / "test_session.db"
        db_url = f"sqlite:///{db_path}"
        
        engine = init_database(db_url)
        session = get_session(engine)
        
        assert session is not None
        session.close()
    
    def test_database_schema_created(self, tmp_path):
        """Test that database schema is created"""
        db_path = tmp_path / "test_schema.db"
        db_url = f"sqlite:///{db_path}"
        
        engine = init_database(db_url)
        
        # Check that papers table exists
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        assert 'papers' in tables
