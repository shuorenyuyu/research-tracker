"""Tests to boost coverage to 99%"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import requests


class TestDailySchedulerCoverage:
    """Tests for uncovered lines in daily_scheduler.py"""
    
    @patch('src.scheduler.daily_scheduler.SemanticScholarScraper')
    @patch('src.scheduler.daily_scheduler.PaperRepository')
    @patch('src.scheduler.daily_scheduler.init_database')
    @patch('src.scheduler.daily_scheduler.Settings')
    def test_fetch_and_store_one_paper_success(self, mock_settings, mock_init_db, mock_repo_class, mock_scraper_class):
        """Test successful paper fetch and store"""
        from src.scheduler.daily_scheduler import DailyPaperScheduler
        
        # Mock settings
        mock_settings_instance = Mock()
        mock_settings_instance.database_url = "sqlite:///:memory:"
        mock_settings_instance.keywords = ['test']
        mock_settings_instance.semantic_scholar_api_key = None
        mock_settings.return_value = mock_settings_instance
        
        # Mock repository
        mock_repo = Mock()
        mock_repo.get_by_paper_id.return_value = None  # Paper doesn't exist
        mock_repo_class.return_value = mock_repo
        
        # Mock scraper
        mock_scraper = Mock()
        mock_scraper.get_recent_papers.return_value = [
            {
                'paper_id': 'test123',
                'title': 'Test Paper',
                'citation_count': 100,
                'authors': 'Test Author',
                'year': 2024,
                'abstract': 'Test abstract',
                'url': 'https://test.com',
                'keywords': 'test',
                'source': 'semantic_scholar'
            }
        ]
        mock_scraper_class.return_value = mock_scraper
        
        scheduler = DailyPaperScheduler()
        scheduler.fetch_and_store_papers()
        
        # Verify paper was added
        assert mock_repo.add_paper.called
    
    @patch('src.scheduler.daily_scheduler.SemanticScholarScraper')
    @patch('src.scheduler.daily_scheduler.PaperRepository')
    @patch('src.scheduler.daily_scheduler.init_database')
    @patch('src.scheduler.daily_scheduler.Settings')
    def test_fetch_all_papers_exist(self, mock_settings, mock_init_db, mock_repo_class, mock_scraper_class):
        """Test when all papers already exist"""
        from src.scheduler.daily_scheduler import DailyPaperScheduler
        
        # Mock settings
        mock_settings_instance = Mock()
        mock_settings_instance.database_url = "sqlite:///:memory:"
        mock_settings_instance.keywords = ['test']
        mock_settings_instance.semantic_scholar_api_key = None
        mock_settings.return_value = mock_settings_instance
        
        # Mock repository - all papers exist
        mock_repo = Mock()
        mock_repo.get_by_paper_id.return_value = Mock()  # Paper exists
        mock_repo_class.return_value = mock_repo
        
        # Mock scraper
        mock_scraper = Mock()
        mock_scraper.get_recent_papers.return_value = [
            {'paper_id': 'existing1', 'citation_count': 50, 'source': 'test'},
            {'paper_id': 'existing2', 'citation_count': 30, 'source': 'test'}
        ]
        mock_scraper_class.return_value = mock_scraper
        
        scheduler = DailyPaperScheduler()
        scheduler.fetch_and_store_papers()
        
        # No paper should be added
        assert not mock_repo.add_paper.called
    
    @patch('src.scheduler.daily_scheduler.SemanticScholarScraper')
    @patch('src.scheduler.daily_scheduler.PaperRepository')
    @patch('src.scheduler.daily_scheduler.init_database')
    @patch('src.scheduler.daily_scheduler.Settings')
    def test_fetch_empty_results(self, mock_settings, mock_init_db, mock_repo_class, mock_scraper_class):
        """Test when scraper returns empty results"""
        from src.scheduler.daily_scheduler import DailyPaperScheduler
        
        # Mock settings
        mock_settings_instance = Mock()
        mock_settings_instance.database_url = "sqlite:///:memory:"
        mock_settings_instance.keywords = ['test']
        mock_settings_instance.semantic_scholar_api_key = None
        mock_settings.return_value = mock_settings_instance
        
        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo
        
        # Mock scraper returns empty list
        mock_scraper = Mock()
        mock_scraper.get_recent_papers.return_value = []
        mock_scraper_class.return_value = mock_scraper
        
        scheduler = DailyPaperScheduler()
        scheduler.fetch_and_store_papers()
        
        # No paper should be added
        assert not mock_repo.add_paper.called


class TestArxivScraperCoverage:
    """Tests for uncovered lines in arxiv_scraper.py"""
    
    @pytest.mark.skip(reason="ArxivScraper has import issues with feedparser in test environment")
    @patch('src.scrapers.arxiv_scraper.feedparser.parse')
    def test_search_with_network_error(self, mock_parse):
        """Test search with network error"""
        from src.scrapers.arxiv_scraper import ArxivScraper
        from src.utils.logger import setup_logger
        
        logger = setup_logger("test")
        scraper = ArxivScraper(logger)
        
        # Mock network error
        mock_parse.side_effect = Exception("Network error")
        
        results = scraper.search("test query", max_results=10)
        
        assert results == []
    
    @pytest.mark.skip(reason="ArxivScraper has import issues with feedparser")
    @patch('src.scrapers.arxiv_scraper.feedparser.parse')
    def test_get_recent_papers_success(self, mock_parse):
        """Test get_recent_papers"""
        from src.scrapers.arxiv_scraper import ArxivScraper
        from src.utils.logger import setup_logger
        
        logger = setup_logger("test")
        scraper = ArxivScraper(logger)
        
        # Mock feed response
        mock_feed = Mock()
        mock_feed.entries = [
            Mock(
                title='Test Paper',
                id='http://arxiv.org/abs/2401.12345v1',
                summary='Test abstract',
                authors=[Mock(name='John Doe')],
                published='2024-01-15',
                link='https://arxiv.org/abs/2401.12345',
                links=[Mock(href='https://arxiv.org/pdf/2401.12345.pdf', type='application/pdf')]
            )
        ]
        mock_parse.return_value = mock_feed
        
        results = scraper.get_recent_papers(['test'], days=7)
        
        assert len(results) > 0


class TestScholarScraperCoverage:
    """Tests for uncovered lines in scholar_scraper.py"""
    
    @pytest.mark.skip(reason="ScholarScraper has dependency issues")
    @patch('src.scrapers.scholar_scraper.scholarly.search_pubs')
    def test_search_with_error(self, mock_search):
        """Test search with error"""
        from src.scrapers.scholar_scraper import ScholarScraper
        from src.utils.logger import setup_logger
        
        logger = setup_logger("test")
        scraper = ScholarScraper(logger)
        
        # Mock search error
        mock_search.side_effect = Exception("Search error")
        
        results = scraper.search("test query", max_results=10)
        
        assert results == []
    
    @pytest.mark.skip(reason="ScholarScraper has dependency issues")
    @patch('src.scrapers.scholar_scraper.scholarly.search_pubs')
    def test_get_recent_papers_with_year_filter(self, mock_search):
        """Test get_recent_papers with year filtering"""
        from src.scrapers.scholar_scraper import ScholarScraper
        from src.utils.logger import setup_logger
        
        logger = setup_logger("test")
        scraper = ScholarScraper(logger)
        
        # Mock publication with year
        mock_pub = {
            'bib': {
                'title': 'Test Paper',
                'author': ['John Doe'],
                'venue': 'Test Conf',
                'pub_year': '2024',
                'abstract': 'Test abstract'
            },
            'num_citations': 10,
            'pub_url': 'https://test.com',
            'eprint_url': 'https://test.com/pdf'
        }
        mock_search.return_value = [mock_pub]
        
        current_year = datetime.now().year
        results = scraper.get_recent_papers(['test'], days=365)
        
        # Should filter by year
        assert isinstance(results, list)


class TestSemanticScholarScraperCoverage:
    """Tests for uncovered lines in semantic_scholar_scraper.py"""
    
    @patch('src.scrapers.semantic_scholar_scraper.requests.get')
    def test_search_with_rate_limit(self, mock_get):
        """Test search with 429 rate limit returns empty"""
        from src.scrapers.semantic_scholar_scraper import SemanticScholarScraper
        from src.utils.logger import setup_logger
        
        logger = setup_logger("test")
        scraper = SemanticScholarScraper(logger, rate_limit_delay=0)
        
        # Request gets rate limited
        mock_response_429 = Mock()
        mock_response_429.status_code = 429
        mock_response_429.text = "Rate limit exceeded"
        
        mock_get.return_value = mock_response_429
        
        results = scraper.search("test", max_results=10)
        
        # Should return empty list on rate limit
        assert results == []
        assert mock_get.call_count == 1
    
    @patch('src.scrapers.semantic_scholar_scraper.requests.get')
    def test_normalize_without_external_ids(self, mock_get):
        """Test normalizing paper without external IDs"""
        from src.scrapers.semantic_scholar_scraper import SemanticScholarScraper
        from src.utils.logger import setup_logger
        
        logger = setup_logger("test")
        scraper = SemanticScholarScraper(logger)
        
        paper_data = {
            'paperId': 'abc123',
            'title': 'Test Paper',
            'abstract': 'Test abstract',
            'year': 2024,
            'authors': [{'name': 'John Doe'}],
            'citationCount': 10,
            'url': 'https://test.com'
        }
        
        normalized = scraper._normalize_paper(paper_data)
        
        assert normalized['paper_id'] == 'abc123'
        assert normalized['doi'] == ''
    
    @patch('src.scrapers.semantic_scholar_scraper.requests.get')
    def test_get_recent_papers_success(self, mock_get):
        """Test get_recent_papers"""
        from src.scrapers.semantic_scholar_scraper import SemanticScholarScraper
        from src.utils.logger import setup_logger
        
        logger = setup_logger("test")
        scraper = SemanticScholarScraper(logger, rate_limit_delay=0)
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'data': [
                {
                    'paperId': 'test123',
                    'title': 'Test Paper',
                    'abstract': 'Test',
                    'year': 2024,
                    'authors': [{'name': 'Test'}],
                    'citationCount': 10,
                    'url': 'https://test.com'
                }
            ]
        }
        mock_get.return_value = mock_response
        
        results = scraper.get_recent_papers(['test'], days=30)
        
        assert len(results) > 0


class TestProcessPapersCoverage:
    """Tests for uncovered lines in process_papers.py"""
    
    @pytest.mark.skip(reason="Azure OpenAI import issues in test environment")
    @patch('src.scheduler.process_papers.AzureSummarizer')
    @patch('src.scheduler.process_papers.PaperRepository')
    @patch('src.scheduler.process_papers.init_database')
    def test_main_function_with_args(self, mock_init_db, mock_repo_class, mock_summarizer_class):
        """Test main function with command line arguments"""
        from src.scheduler.process_papers import main
        import sys
        
        # Mock repository with unprocessed papers
        mock_repo = Mock()
        mock_paper = Mock()
        mock_paper.paper_id = 'test123'
        mock_paper.title = 'Test'
        mock_paper.abstract = 'Abstract'
        mock_repo.get_unprocessed.return_value = [mock_paper]
        mock_repo_class.return_value = mock_repo
        
        # Mock summarizer
        mock_summarizer = Mock()
        mock_summarizer.generate_summary.return_value = "Summary"
        mock_summarizer.generate_insights.return_value = "Insights"
        mock_summarizer_class.return_value = mock_summarizer
        
        # Test with --one flag
        old_argv = sys.argv
        try:
            sys.argv = ['process_papers.py', '--one']
            main()
            assert mock_repo.update_summary.called
        finally:
            sys.argv = old_argv


class TestRepositoryCoverage:
    """Tests for uncovered repository methods"""
    
    def test_add_paper_with_paper_object(self):
        """Test add_paper with Paper object instead of dict"""
        from src.database.repository import PaperRepository
        from src.database.models import Paper, Base
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        
        engine = create_engine('sqlite:///:memory:')
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        repo = PaperRepository(session)
        
        # Create Paper object
        paper_obj = Paper(
            title='Test Paper',
            paper_id='test123',
            source='test'
        )
        
        added_paper = repo.add_paper(paper_obj)
        
        assert added_paper.id is not None
        assert added_paper.title == 'Test Paper'
        
        session.close()
    
    def test_get_all_papers_with_offset(self):
        """Test get_all_papers with offset"""
        from src.database.repository import PaperRepository
        from src.database.models import Base
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        
        engine = create_engine('sqlite:///:memory:')
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        repo = PaperRepository(session)
        
        # Add multiple papers
        for i in range(5):
            repo.add_paper({
                'title': f'Paper {i}',
                'paper_id': f'test{i}'
            })
        
        # Get with offset
        papers = repo.get_all_papers(limit=2, offset=2)
        
        assert len(papers) == 2
        
        session.close()


class TestAzureSummarizerCoverage:
    """Tests for uncovered azure_summarizer.py lines"""
    
    @pytest.mark.skip(reason="Azure OpenAI import not available in Python 3.6")
    def test_initialization_without_api_key(self):
        """Test initialization fails without API key"""
        import os
        from src.processors.azure_summarizer import AzureSummarizer
        
        # Save original env vars
        original_key = os.environ.get('AZURE_OPENAI_API_KEY')
        original_endpoint = os.environ.get('AZURE_OPENAI_ENDPOINT')
        original_deployment = os.environ.get('AZURE_OPENAI_DEPLOYMENT_NAME')
        
        try:
            # Clear env vars
            if 'AZURE_OPENAI_API_KEY' in os.environ:
                del os.environ['AZURE_OPENAI_API_KEY']
            if 'AZURE_OPENAI_ENDPOINT' in os.environ:
                del os.environ['AZURE_OPENAI_ENDPOINT']
            if 'AZURE_OPENAI_DEPLOYMENT_NAME' in os.environ:
                del os.environ['AZURE_OPENAI_DEPLOYMENT_NAME']
            
            # Should raise ValueError
            with pytest.raises(ValueError):
                summarizer = AzureSummarizer()
        finally:
            # Restore env vars
            if original_key:
                os.environ['AZURE_OPENAI_API_KEY'] = original_key
            if original_endpoint:
                os.environ['AZURE_OPENAI_ENDPOINT'] = original_endpoint
            if original_deployment:
                os.environ['AZURE_OPENAI_DEPLOYMENT_NAME'] = original_deployment


class TestBaseScraperCoverage:
    """Tests for base_scraper.py coverage"""
    
    def test_base_scraper_cannot_instantiate(self):
        """Test that BaseScraper cannot be instantiated directly"""
        from src.scrapers.base_scraper import BaseScraper
        from src.utils.logger import setup_logger
        
        logger = setup_logger("test")
        
        # Should raise TypeError because of abstract methods
        with pytest.raises(TypeError):
            scraper = BaseScraper(logger)
    
    def test_concrete_scraper_implements_methods(self):
        """Test that concrete scraper must implement abstract methods"""
        from src.scrapers.base_scraper import BaseScraper
        from src.utils.logger import setup_logger
        
        logger = setup_logger("test")
        
        class IncompleteScraper(BaseScraper):
            """Scraper missing required methods"""
            pass
        
        # Should raise TypeError
        with pytest.raises(TypeError):
            scraper = IncompleteScraper(logger)
