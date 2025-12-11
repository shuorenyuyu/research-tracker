"""Additional comprehensive tests to reach 99% coverage"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Mock dependencies
sys.modules['arxiv'] = Mock()
sys.modules['scholarly'] = Mock()
sys.modules['openai'] = Mock()

from src.database.models import Paper, get_session, Base
from src.scrapers.base_scraper import BaseScraper


class TestPaperModelToDict:
    """Test Paper.to_dict() edge cases"""
    
    def test_paper_to_dict_with_future_dates(self):
        """Test to_dict with future dates (edge case)"""
        future_date = datetime.utcnow() + timedelta(days=365)
        
        paper = Paper(
            title="Future Paper",
            paper_id="future1",
            publication_date=future_date,
            fetched_at=future_date
        )
        
        paper_dict = paper.to_dict()
        assert paper_dict['publication_date'] == future_date.isoformat()
        assert paper_dict['fetched_at'] == future_date.isoformat()
    
    def test_paper_to_dict_with_empty_strings(self):
        """Test to_dict with empty string fields"""
        paper = Paper(
            title="",  # Empty title
            paper_id="empty1",
            authors="",
            abstract="",
            venue=""
        )
        
        paper_dict = paper.to_dict()
        assert paper_dict['title'] == ""
        assert paper_dict['authors'] == ""
    
    def test_paper_to_dict_with_very_long_strings(self):
        """Test to_dict with very long text fields"""
        long_text = "A" * 10000
        
        paper = Paper(
            title=long_text,
            paper_id="long1",
            abstract=long_text
        )
        
        paper_dict = paper.to_dict()
        assert len(paper_dict['title']) == 10000
        assert len(paper_dict['abstract']) == 10000
    
    def test_paper_to_dict_all_none_values(self):
        """Test to_dict with all optional fields as None"""
        paper = Paper(
            title="Minimal",
            paper_id="minimal1",
            authors=None,
            year=None,
            venue=None,
            abstract=None,
            url=None,
            pdf_url=None,
            doi=None,
            citation_count=None,
            summary_zh=None,
            investment_insights=None,
            keywords=None,
            publication_date=None,
            fetched_at=None
        )
        
        paper_dict = paper.to_dict()
        # Should handle None values gracefully
        assert 'title' in paper_dict
        assert paper_dict['title'] == "Minimal"


class TestGetSession:
    """Test get_session() function"""
    
    @patch('src.database.models.init_database')
    def test_get_session_when_not_initialized(self, mock_init):
        """Test get_session() calls init_database if not initialized"""
        from src.database import models
        
        # Reset global state
        models._Session = None
        
        # Mock the initialization to set up _Session
        def mock_init_db(db_path=None):
            engine = create_engine('sqlite:///:memory:')
            Base.metadata.create_all(engine)
            models._Session = sessionmaker(bind=engine)
        
        mock_init.side_effect = mock_init_db
        
        session = get_session()
        
        # Verify init_database was called
        mock_init.assert_called_once()
        assert session is not None


class ConcreteScraperForTest(BaseScraper):
    """Concrete implementation for testing abstract methods"""
    
    def search(self, query: str, max_results: int = 50):
        return []
    
    def get_recent_papers(self, keywords, days: int = 1):
        return []


class TestBaseScraperAbstract:
    """Test BaseScraper abstract methods"""
    
    def test_cannot_instantiate_base_scraper(self):
        """Test that BaseScraper cannot be instantiated directly"""
        logger = Mock()
        
        with pytest.raises(TypeError):
            BaseScraper(logger)
    
    def test_concrete_scraper_implements_methods(self):
        """Test that concrete scraper can be instantiated"""
        logger = Mock()
        
        scraper = ConcreteScraperForTest(logger)
        assert scraper.logger == logger
    
    def test_concrete_scraper_search(self):
        """Test that concrete scraper implements search"""
        logger = Mock()
        scraper = ConcreteScraperForTest(logger)
        
        results = scraper.search("test query")
        assert isinstance(results, list)
    
    def test_concrete_scraper_get_recent(self):
        """Test that concrete scraper implements get_recent_papers"""
        logger = Mock()
        scraper = ConcreteScraperForTest(logger)
        
        results = scraper.get_recent_papers(["test"])
        assert isinstance(results, list)


class TestRepositoryCountMethods:
    """Test repository count methods"""
    
    @pytest.fixture
    def db_session(self):
        """Create in-memory database"""
        engine = create_engine('sqlite:///:memory:')
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        yield session
        session.close()
    
    @pytest.fixture
    def repo(self, db_session):
        """Create repository"""
        from src.database.repository import PaperRepository
        return PaperRepository(db_session)
    
    def test_count_all_with_empty_database(self, repo):
        """Test count_all with no papers"""
        count = repo.count_all()
        assert count == 0
    
    def test_count_unprocessed_edge_case(self, repo):
        """Test count_unprocessed with mixed data"""
        # Add processed paper
        repo.add_paper({
            'title': 'Processed',
            'paper_id': 'proc1',
            'processed': True
        })
        
        # Add unprocessed paper
        repo.add_paper({
            'title': 'Unprocessed',
            'paper_id': 'unproc1',
            'processed': False
        })
        
        count = repo.count_unprocessed()
        assert count == 1
    
    def test_get_all_papers_pagination(self, repo):
        """Test get_all() edge case"""
        # Add many papers
        for i in range(10):
            repo.add_paper({
                'title': f'Paper {i}',
                'paper_id': f'id{i}'
            })
        
        all_papers = repo.get_all()
        assert len(all_papers) == 10


class TestAzureSummarizerInitialization:
    """Test AzureSummarizer initialization edge cases"""
    
    @patch.dict('os.environ', {}, clear=True)
    def test_initialization_without_environment(self):
        """Test initialization when env vars are missing"""
        from src.processors.azure_summarizer import AzureSummarizer
        
        with pytest.raises(Exception):
            summarizer = AzureSummarizer()
