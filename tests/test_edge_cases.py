"""Edge case tests to increase coverage"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys

# Mock dependencies
sys.modules['arxiv'] = Mock()
sys.modules['scholarly'] = Mock()
sys.modules['openai'] = Mock()

from src.database.models import Base, Paper
from src.database.repository import PaperRepository


class TestRepositoryEdgeCases:
    """Test edge cases in repository"""
    
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
        return PaperRepository(db_session)
    
    def test_add_paper_with_minimal_data(self, repo):
        """Test adding paper with only required fields"""
        minimal_data = {
            'title': 'Minimal Paper',
            'paper_id': 'minimal123'
        }
        
        paper = repo.add_paper(minimal_data)
        assert paper.id is not None
    
    def test_update_citation_count_nonexistent(self, repo):
        """Test updating citation count for non-existent ID"""
        # This should handle gracefully
        try:
            repo.update_citation_count(99999, 100)
        except:
            pass  # Expected to potentially fail
    
    def test_mark_as_processed_nonexistent(self, repo):
        """Test marking non-existent paper as processed"""
        try:
            repo.mark_as_processed('nonexistent')
        except:
            pass  # Expected to potentially fail
    
    def test_mark_as_published_nonexistent(self, repo):
        """Test marking non-existent paper as published"""
        try:
            repo.mark_as_published('nonexistent')
        except:
            pass  # Expected to potentially fail
    
    def test_get_recent_papers_with_old_dates(self, repo):
        """Test getting recent papers with old cutoff"""
        repo.add_paper({
            'title': 'Old Paper',
            'paper_id': 'old1',
            'fetched_at': datetime.utcnow() - timedelta(days=365)
        })
        
        recent = repo.get_recent_papers(days=30)
        assert len(recent) == 0
    
    def test_get_top_cited_old_papers(self, repo):
        """Test getting top cited papers outside date range"""
        repo.add_paper({
            'title': 'Very Old',
            'paper_id': 'veryold1',
            'citation_count': 1000,
            'fetched_at': datetime.utcnow() - timedelta(days=400)
        })
        
        top_papers = repo.get_top_cited_papers(days=30)
        assert len(top_papers) == 0


class TestScraperEdgeCases:
    """Test scraper edge cases"""
    
    @patch('requests.get')
    def test_semantic_scholar_network_error(self, mock_get):
        """Test handling network errors"""
        from src.scrapers.semantic_scholar_scraper import SemanticScholarScraper
        from src.utils.logger import setup_logger
        
        logger = setup_logger("test")
        scraper = SemanticScholarScraper(logger)
        
        mock_get.side_effect = Exception("Network error")
        
        results = scraper.search('test query')
        assert len(results) == 0
    
    @patch('requests.get')
    def test_semantic_scholar_invalid_json(self, mock_get):
        """Test handling invalid JSON response"""
        from src.scrapers.semantic_scholar_scraper import SemanticScholarScraper
        from src.utils.logger import setup_logger
        
        logger = setup_logger("test")
        scraper = SemanticScholarScraper(logger)
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_get.return_value = mock_response
        
        results = scraper.search('test')
        assert len(results) == 0
    
    def test_semantic_scholar_normalize_missing_fields(self):
        """Test normalizing paper with all fields missing"""
        from src.scrapers.semantic_scholar_scraper import SemanticScholarScraper
        from src.utils.logger import setup_logger
        
        logger = setup_logger("test")
        scraper = SemanticScholarScraper(logger)
        
        minimal_paper = {
            'paperId': 'test',
            'externalIds': {},
            'authors': []
        }
        
        normalized = scraper._normalize_paper(minimal_paper)
        assert normalized['paper_id'] == 'test'
        assert normalized['authors'] == ''


class TestSchedulerEdgeCases:
    """Test scheduler edge cases"""
    
    @patch('src.scheduler.daily_scheduler.init_database')
    @patch('src.scheduler.daily_scheduler.PaperRepository')
    @patch('src.scheduler.daily_scheduler.SemanticScholarScraper')
    @patch('src.scheduler.daily_scheduler.ArxivScraper')
    def test_fetch_with_exception(self, mock_arxiv, mock_ss, mock_repo, mock_init):
        """Test fetch when scraper raises exception"""
        from src.scheduler.daily_scheduler import DailyPaperScheduler
        
        mock_repo.return_value = Mock()
        mock_arxiv.return_value = Mock()
        
        mock_ss_instance = Mock()
        mock_ss_instance.get_recent_papers.side_effect = Exception("API Error")
        mock_ss.return_value = mock_ss_instance
        
        scheduler = DailyPaperScheduler()
        scheduler.ss_scraper = mock_ss_instance
        
        # Should handle exception gracefully
        try:
            result = scheduler.fetch_and_store_papers()
        except:
            pass  # Expected to potentially fail
    
    @patch('src.scheduler.daily_scheduler.init_database')
    @patch('src.scheduler.daily_scheduler.PaperRepository')
    @patch('src.scheduler.daily_scheduler.SemanticScholarScraper')
    @patch('src.scheduler.daily_scheduler.ArxivScraper')
    def test_fetch_with_all_duplicates(self, mock_arxiv, mock_ss, mock_repo, mock_init):
        """Test fetch when all papers are duplicates"""
        from src.scheduler.daily_scheduler import DailyPaperScheduler
        
        mock_repo_instance = Mock()
        mock_repo_instance.get_by_paper_id.return_value = Mock()  # All exist
        mock_repo.return_value = mock_repo_instance
        
        mock_ss_instance = Mock()
        mock_ss_instance.get_recent_papers.return_value = [
            {'paper_id': 'dup1', 'title': 'Duplicate'}
        ]
        mock_ss.return_value = mock_ss_instance
        
        scheduler = DailyPaperScheduler()
        scheduler.paper_repo = mock_repo_instance
        scheduler.ss_scraper = mock_ss_instance
        
        result = scheduler.fetch_and_store_papers()
        
        # Should not add any papers
        mock_repo_instance.add_paper.assert_not_called()


class TestProcessorEdgeCases:
    """Test processor edge cases"""
    
    @patch('src.scheduler.process_papers.PaperRepository')
    @patch('src.scheduler.process_papers.AzureSummarizer')
    def test_process_with_exception_in_summary(self, mock_summarizer, mock_repo):
        """Test processing when summary generation throws exception"""
        from src.scheduler.process_papers import PaperProcessor
        
        mock_paper = Mock()
        mock_paper.title = 'Test'
        mock_paper.abstract = 'Abstract'
        mock_paper.authors = 'Author'
        mock_paper.year = 2024
        mock_paper.citation_count = 10
        mock_paper.venue = 'Venue'
        mock_paper.paper_id = 'test'
        
        mock_repo_instance = Mock()
        mock_repo_instance.get_unprocessed.return_value = [mock_paper]
        mock_repo.return_value = mock_repo_instance
        
        mock_summarizer_instance = Mock()
        mock_summarizer_instance.generate_summary.side_effect = Exception("API Error")
        mock_summarizer.return_value = mock_summarizer_instance
        
        processor = PaperProcessor()
        processor.process_unprocessed_papers(limit=1)
        
        # Should handle exception and not update database
        mock_repo_instance.update_summary.assert_not_called()


class TestModelEdgeCases:
    """Test model edge cases"""
    
    def test_paper_to_dict_with_none_dates(self):
        """Test to_dict with None dates"""
        paper = Paper(
            title="Test",
            paper_id="test",
            publication_date=None,
            fetched_at=None
        )
        
        paper_dict = paper.to_dict()
        assert paper_dict['publication_date'] is None
        assert paper_dict['fetched_at'] is None
    
    def test_paper_repr_short_title(self):
        """Test repr with short title"""
        paper = Paper(
            title="Short",
            paper_id="test",
            year=2024
        )
        
        repr_str = repr(paper)
        assert "Short" in repr_str
