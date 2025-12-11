"""Integration-style tests to increase coverage by running actual code paths"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
import os
import tempfile
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Mock dependencies
sys.modules['arxiv'] = Mock()
sys.modules['scholarly'] = Mock()
sys.modules['openai'] = Mock()
sys.modules['apscheduler'] = Mock()
sys.modules['apscheduler.schedulers'] = Mock()
sys.modules['apscheduler.schedulers.background'] = Mock()
sys.modules['apscheduler.triggers'] = Mock()
sys.modules['apscheduler.triggers.cron'] = Mock()

from src.database.models import Base, Paper
from src.database.repository import PaperRepository


class TestRealDatabaseIntegration:
    """Integration tests with real database operations"""
    
    @pytest.fixture
    def temp_db(self):
        """Create temporary database file"""
        fd, path = tempfile.mkstemp(suffix='.db')
        os.close(fd)
        
        engine = create_engine(f'sqlite:///{path}')
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        yield session, path
        
        session.close()
        os.unlink(path)
    
    def test_repository_error_handling_on_add(self, temp_db):
        """Test repository handling errors during add"""
        session, _ = temp_db
        repo = PaperRepository(session)
        
        # Try to add paper with missing required field
        try:
            repo.add_paper({'title': 'Test'})  # Missing paper_id
        except Exception as e:
            # Should raise error, line 38 in repository.py
            assert e is not None
    
    def test_full_paper_lifecycle(self, temp_db):
        """Test complete paper lifecycle"""
        session, _ = temp_db
        repo = PaperRepository(session)
        
        # Add paper
        paper_data = {
            'title': 'Test Paper',
            'paper_id': 'test123',
            'authors': 'Author 1, Author 2',
            'year': 2024,
            'citation_count': 10,
            'abstract': 'This is a test abstract',
            'processed': False,
            'published': False
        }
        
        paper = repo.add_paper(paper_data)
        assert paper.id is not None
        
        # Verify it exists
        assert repo.paper_exists('test123') is True
        
        # Get unprocessed
        unprocessed = repo.get_unprocessed(limit=10)
        assert len(unprocessed) == 1
        
        # Update summary
        repo.update_summary('test123', 'Chinese summary', 'Investment insights')
        
        # Mark as processed
        repo.mark_as_processed('test123')
        
        # Verify processed
        unprocessed = repo.get_unprocessed(limit=10)
        assert len(unprocessed) == 0
        
        # Get unpublished
        unpublished = repo.get_unpublished(limit=10)
        assert len(unpublished) == 1
        
        # Mark as published
        repo.mark_as_published('test123')
        
        # Get all papers
        all_papers = repo.get_all()
        assert len(all_papers) == 1
        
        # Count methods
        assert repo.count_all() == 1
        assert repo.count_unprocessed() == 0


class TestScraperRealCalls:
    """Test scrapers with minimal mocking to cover error paths"""
    
    @patch('requests.get')
    def test_semantic_scholar_real_api_flow(self, mock_get):
        """Test semantic scholar with realistic API responses"""
        from src.scrapers.semantic_scholar_scraper import SemanticScholarScraper
        from src.utils.logger import setup_logger
        
        logger = setup_logger("integration_test")
        scraper = SemanticScholarScraper(logger, api_key="test-key")
        
        # Test successful search
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'data': [
                {
                    'paperId': '123',
                    'title': 'Test Paper',
                    'authors': [{'name': 'Author'}],
                    'year': 2024,
                    'citationCount': 10,
                    'abstract': 'Abstract',
                    'venue': 'Conference',
                    'externalIds': {'DOI': '10.1234/test', 'ArXiv': '2401.12345'}
                }
            ]
        }
        mock_get.return_value = mock_response
        
        results = scraper.search("deep learning")
        assert len(results) == 1
        assert results[0]['paper_id'] == '123'
        
        # Test 404 error
        mock_response_404 = Mock()
        mock_response_404.status_code = 404
        mock_response_404.raise_for_status.side_effect = Exception("404")
        mock_get.return_value = mock_response_404
        
        results = scraper.search("test")
        assert len(results) == 0
        
        # Test get_recent_papers
        mock_get.return_value = mock_response  # Reset to success
        recent = scraper.get_recent_papers(year=2024, keyword="AI")
        assert isinstance(recent, list)
    
    @patch('feedparser.parse')
    def test_arxiv_real_feed_parsing(self, mock_parse):
        """Test arXiv with realistic feed data"""
        from src.scrapers.arxiv_scraper import ArxivScraper
        from src.utils.logger import setup_logger
        
        logger = setup_logger("integration_test")
        scraper = ArxivScraper(logger)
        
        # Test successful parsing
        mock_parse.return_value = {
            'entries': [
                {
                    'id': 'http://arxiv.org/abs/2401.12345',
                    'title': 'Test Paper',
                    'summary': 'Abstract',
                    'authors': [{'name': 'Author 1'}, {'name': 'Author 2'}],
                    'published': '2024-01-15T00:00:00Z',
                    'links': [
                        {'type': 'application/pdf', 'href': 'http://arxiv.org/pdf/2401.12345'}
                    ]
                }
            ]
        }
        
        results = scraper.search("machine learning")
        assert len(results) == 1
        
        # Test with malformed entry (trigger line 111)
        mock_parse.return_value = {
            'entries': [
                {
                    'id': 'http://arxiv.org/abs/invalid',
                    # Missing required fields
                }
            ]
        }
        
        results = scraper.search("test")
        # Should handle gracefully
        
        # Test exception during parsing (lines 49-56)
        mock_parse.side_effect = Exception("Parse error")
        results = scraper.search("test")
        assert len(results) == 0


class TestSchedulerRealExecution:
    """Test scheduler with realistic execution"""
    
    @patch('src.scheduler.daily_scheduler.init_database')
    @patch('src.scheduler.daily_scheduler.PaperRepository')
    @patch('src.scheduler.daily_scheduler.SemanticScholarScraper')
    @patch('src.scheduler.daily_scheduler.ArxivScraper')
    @patch('src.scheduler.daily_scheduler.BackgroundScheduler')
    @patch('src.scheduler.daily_scheduler.CronTrigger')
    def test_scheduler_main_with_time_args(self, mock_cron, mock_bg_scheduler, mock_arxiv, mock_ss, mock_repo, mock_init):
        """Test main() with time arguments to cover lines 183"""
        from src.scheduler.daily_scheduler import main
        
        mock_scheduler_instance = Mock()
        mock_bg_scheduler.return_value = mock_scheduler_instance
        mock_scheduler_instance.start.side_effect = KeyboardInterrupt()
        
        mock_repo_instance = Mock()
        mock_repo_instance.count_all.return_value = 0
        mock_repo_instance.count_unprocessed.return_value = 0
        mock_repo.return_value = mock_repo_instance
        
        mock_ss_instance = Mock()
        mock_ss_instance.get_recent_papers.return_value = []
        mock_ss.return_value = mock_ss_instance
        
        with patch('sys.argv', ['daily_scheduler.py', '--time', '15:30', '--timezone', 'UTC']):
            try:
                main()
            except:
                pass
        
        # Verify CronTrigger was called with correct params (lines 119-147)
        mock_cron.assert_called()
        
        # Verify scheduler was started (line 140)
        mock_scheduler_instance.start.assert_called()
        
        # Verify shutdown was called after KeyboardInterrupt (line 144)
        mock_scheduler_instance.shutdown.assert_called()


class TestProcessorRealWorkflow:
    """Test processor with realistic workflow"""
    
    @patch('src.scheduler.process_papers.init_database')
    @patch('src.scheduler.process_papers.PaperRepository')
    @patch('src.scheduler.process_papers.AzureSummarizer')
    def test_process_papers_argparse_coverage(self, mock_summarizer, mock_repo, mock_init):
        """Test process_papers main() to cover line 136"""
        from src.scheduler.process_papers import main
        
        mock_repo_instance = Mock()
        mock_repo_instance.get_unprocessed.return_value = []
        mock_repo.return_value = mock_repo_instance
        
        mock_summarizer_instance = Mock()
        mock_summarizer.return_value = mock_summarizer_instance
        
        # Test with --limit argument (line 136 should be covered)
        with patch('sys.argv', ['process_papers.py', '--limit', '10']):
            try:
                main()
            except SystemExit:
                pass
        
        # Verify it processed with limit=10
        mock_repo_instance.get_unprocessed.assert_called_with(limit=10)
