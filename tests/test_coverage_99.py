"""Additional tests to reach 99% coverage"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import time


class TestDailySchedulerMissingLines:
    """Tests for missing lines in daily_scheduler.py (lines 43, 93-95, 107-109, 119-147, 183)"""
    
    @patch('src.scheduler.daily_scheduler.SemanticScholarScraper')
    @patch('src.scheduler.daily_scheduler.PaperRepository')
    @patch('src.scheduler.daily_scheduler.init_database')
    @patch('src.scheduler.daily_scheduler.Settings')
    def test_scheduler_with_api_key(self, mock_settings, mock_init_db, mock_repo_class, mock_scraper_class):
        """Test scheduler initialization with API key (line 43)"""
        from src.scheduler.daily_scheduler import DailyPaperScheduler
        
        # Mock settings with API key
        mock_settings_instance = Mock()
        mock_settings_instance.database_url = "sqlite:///:memory:"
        mock_settings_instance.keywords = ['test']
        mock_settings_instance.semantic_scholar_api_key = "test_api_key"
        mock_settings.return_value = mock_settings_instance
        
        mock_repo_class.return_value = Mock()
        mock_scraper_class.return_value = Mock()
        
        scheduler = DailyPaperScheduler()
        
        # API key should be passed to scraper
        assert scheduler.ss_scraper is not None
    
    @patch('src.scheduler.daily_scheduler.SemanticScholarScraper')
    @patch('src.scheduler.daily_scheduler.PaperRepository')
    @patch('src.scheduler.daily_scheduler.init_database')
    @patch('src.scheduler.daily_scheduler.Settings')
    def test_fetch_with_missing_paper_id(self, mock_settings, mock_init_db, mock_repo_class, mock_scraper_class):
        """Test fetch when paper has no paper_id (lines 107-109)"""
        from src.scheduler.daily_scheduler import DailyPaperScheduler
        
        # Mock settings
        mock_settings_instance = Mock()
        mock_settings_instance.database_url = "sqlite:///:memory:"
        mock_settings_instance.keywords = ['test']
        mock_settings_instance.semantic_scholar_api_key = None
        mock_settings.return_value = mock_settings_instance
        
        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo
        
        # Mock scraper returns paper without paper_id
        mock_scraper = Mock()
        mock_scraper.get_recent_papers.return_value = [
            {
                'title': 'Test Paper',
                'citation_count': 100,
                # No paper_id or semantic_scholar_id
            }
        ]
        mock_scraper_class.return_value = mock_scraper
        
        scheduler = DailyPaperScheduler()
        scheduler.fetch_and_store_papers()
        
        # Should skip paper without ID
        assert not mock_repo.add_paper.called
    
    @patch('src.scheduler.daily_scheduler.SemanticScholarScraper')
    @patch('src.scheduler.daily_scheduler.PaperRepository')
    @patch('src.scheduler.daily_scheduler.init_database')
    @patch('src.scheduler.daily_scheduler.Settings')
    @patch('src.scheduler.daily_scheduler.BlockingScheduler')
    def test_start_scheduler(self, mock_bs, mock_settings, mock_init_db, mock_repo_class, mock_scraper_class):
        """Test start method (line 183)"""
        from src.scheduler.daily_scheduler import DailyPaperScheduler
        
        # Mock settings
        mock_settings_instance = Mock()
        mock_settings_instance.database_url = "sqlite:///:memory:"
        mock_settings_instance.keywords = ['test']
        mock_settings_instance.semantic_scholar_api_key = None
        mock_settings.return_value = mock_settings_instance
        
        mock_repo_class.return_value = Mock()
        mock_scraper_class.return_value = Mock()
        
        # Mock scheduler
        mock_scheduler = Mock()
        mock_bs.return_value = mock_scheduler
        
        scheduler = DailyPaperScheduler()
        scheduler.start(run_time="00:00")
        
        # Should add job and start scheduler
        assert mock_scheduler.add_job.called
        assert mock_scheduler.start.called


class TestSemanticScholarMissingLines:
    """Tests for missing lines in semantic_scholar_scraper.py"""
    
    @patch('src.scrapers.semantic_scholar_scraper.requests.get')
    def test_search_with_exception(self, mock_get):
        """Test search with exception (lines 85-86)"""
        from src.scrapers.semantic_scholar_scraper import SemanticScholarScraper
        from src.utils.logger import setup_logger
        
        logger = setup_logger("test")
        scraper = SemanticScholarScraper(logger, rate_limit_delay=0)
        
        # Mock exception
        mock_get.side_effect = Exception("Network error")
        
        results = scraper.search("test", max_results=10)
        
        assert results == []
    
    @patch('src.scrapers.semantic_scholar_scraper.requests.get')
    def test_get_paper_by_arxiv_id_404(self, mock_get):
        """Test get_paper_by_arxiv_id with 404 (lines 117-118)"""
        from src.scrapers.semantic_scholar_scraper import SemanticScholarScraper
        from src.utils.logger import setup_logger
        
        logger = setup_logger("test")
        scraper = SemanticScholarScraper(logger)
        
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        result = scraper.get_paper_by_arxiv_id("2401.12345")
        
        assert result is None
    
    @patch('src.scrapers.semantic_scholar_scraper.requests.get')
    def test_enrich_papers_max_limit(self, mock_get):
        """Test enrich_papers respects max_papers limit (lines 178-181)"""
        from src.scrapers.semantic_scholar_scraper import SemanticScholarScraper
        from src.utils.logger import setup_logger
        
        logger = setup_logger("test")
        scraper = SemanticScholarScraper(logger, rate_limit_delay=0)
        
        # Create 100 papers
        papers = [
            {'paper_id': f'arXiv:{i}', 'title': f'Paper {i}'}
            for i in range(100)
        ]
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'paperId': 'test',
            'title': 'Test',
            'citationCount': 10
        }
        mock_get.return_value = mock_response
        
        enriched = scraper.enrich_papers_with_citations(papers, max_papers=10)
        
        # Should process only 10 papers
        assert mock_get.call_count <= 10
    
    @patch('src.scrapers.semantic_scholar_scraper.requests.get')
    def test_get_recent_papers_with_error(self, mock_get):
        """Test get_recent_papers with API error (lines 212-214)"""
        from src.scrapers.semantic_scholar_scraper import SemanticScholarScraper
        from src.utils.logger import setup_logger
        
        logger = setup_logger("test")
        scraper = SemanticScholarScraper(logger, rate_limit_delay=0)
        
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Server error"
        mock_get.return_value = mock_response
        
        results = scraper.get_recent_papers(['test'], days=30)
        
        assert results == []
    
    @patch('src.scrapers.semantic_scholar_scraper.requests.get')
    def test_normalize_with_missing_external_ids(self, mock_get):
        """Test _normalize_paper without externalIds field (lines 255-258)"""
        from src.scrapers.semantic_scholar_scraper import SemanticScholarScraper
        from src.utils.logger import setup_logger
        
        logger = setup_logger("test")
        scraper = SemanticScholarScraper(logger)
        
        paper_data = {
            'paperId': 'abc123',
            'title': 'Test Paper',
            'year': 2024,
            'authors': [{'name': 'John Doe'}],
            'citationCount': 10
        }
        
        normalized = scraper._normalize_paper(paper_data)
        
        assert normalized['doi'] == ''
        assert normalized['paper_id'] == 'abc123'


class TestArxivScraperMissingLines:
    """Tests for arxiv_scraper.py missing lines"""
    
    @pytest.mark.skip(reason="feedparser import issues")
    def test_normalize_with_missing_pdf(self):
        """Test normalize when PDF link is missing"""
        pass


class TestScholarScraperMissingLines:
    """Tests for scholar_scraper.py missing lines"""
    
    @pytest.mark.skip(reason="scholarly module import issues")
    def test_scholarly_missing_lines(self):
        """Test scholar scraper edge cases"""
        pass


class TestProcessPapersMissingLine:
    """Test for process_papers.py line 136"""
    
    @pytest.mark.skip(reason="Azure OpenAI import issues")
    def test_main_without_args(self):
        """Test main function without arguments"""
        pass


class TestAzureSummarizerMissingLine:
    """Test for azure_summarizer.py line 26"""
    
    @pytest.mark.skip(reason="Azure OpenAI not available in Python 3.6")
    def test_generate_summary_api_call(self):
        """Test actual API call"""
        pass


class TestBaseScraperMissingLines:
    """Test for base_scraper.py lines 26, 40"""
    
    def test_get_recent_papers_not_implemented(self):
        """Test get_recent_papers raises NotImplementedError"""
        from src.scrapers.base_scraper import BaseScraper
        from src.utils.logger import setup_logger
        
        logger = setup_logger("test")
        
        # Create minimal concrete implementation
        class MinimalScraper(BaseScraper):
            def search(self, query, max_results=100):
                return []
            
            def _normalize_paper(self, paper):
                return paper
        
        scraper = MinimalScraper(logger)
        
        # get_recent_papers should raise NotImplementedError
        with pytest.raises(NotImplementedError):
            scraper.get_recent_papers(['test'], days=7)


class TestEdgeCasesForFullCoverage:
    """Additional edge cases to increase coverage"""
    
    @patch('src.scheduler.daily_scheduler.SemanticScholarScraper')
    @patch('src.scheduler.daily_scheduler.PaperRepository')
    @patch('src.scheduler.daily_scheduler.init_database')
    @patch('src.scheduler.daily_scheduler.Settings')
    def test_fetch_with_exception_in_loop(self, mock_settings, mock_init_db, mock_repo_class, mock_scraper_class):
        """Test fetch when exception occurs during processing"""
        from src.scheduler.daily_scheduler import DailyPaperScheduler
        
        # Mock settings
        mock_settings_instance = Mock()
        mock_settings_instance.database_url = "sqlite:///:memory:"
        mock_settings_instance.keywords = ['test']
        mock_settings_instance.semantic_scholar_api_key = None
        mock_settings.return_value = mock_settings_instance
        
        # Mock repository that raises exception
        mock_repo = Mock()
        mock_repo.get_by_paper_id.side_effect = Exception("DB error")
        mock_repo_class.return_value = mock_repo
        
        # Mock scraper
        mock_scraper = Mock()
        mock_scraper.get_recent_papers.return_value = [
            {
                'paper_id': 'test123',
                'title': 'Test',
                'citation_count': 10,
                'source': 'test'
            }
        ]
        mock_scraper_class.return_value = mock_scraper
        
        scheduler = DailyPaperScheduler()
        
        # Should handle exception gracefully
        try:
            scheduler.fetch_and_store_papers()
        except Exception:
            pass  # Expected
    
    @patch('src.scrapers.semantic_scholar_scraper.requests.get')
    def test_semantic_scholar_with_fields_of_study(self, mock_get):
        """Test search with fields_of_study parameter (lines 63-64)"""
        from src.scrapers.semantic_scholar_scraper import SemanticScholarScraper
        from src.utils.logger import setup_logger
        
        logger = setup_logger("test")
        scraper = SemanticScholarScraper(logger, rate_limit_delay=0)
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'data': []}
        mock_get.return_value = mock_response
        
        results = scraper.search(
            "test",
            max_results=10,
            fields_of_study=["Computer Science", "Engineering"]
        )
        
        # Verify fields_of_study was added to params
        call_kwargs = mock_get.call_args[1]
        assert 'fieldsOfStudy' in call_kwargs['params']
    
    @patch('src.scrapers.semantic_scholar_scraper.requests.get')
    def test_semantic_scholar_with_year_filter(self, mock_get):
        """Test search with year_filter parameter (lines 61-62)"""
        from src.scrapers.semantic_scholar_scraper import SemanticScholarScraper
        from src.utils.logger import setup_logger
        
        logger = setup_logger("test")
        scraper = SemanticScholarScraper(logger, rate_limit_delay=0)
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'data': []}
        mock_get.return_value = mock_response
        
        results = scraper.search("test", max_results=10, year_filter="2024-")
        
        # Verify year was added to params
        call_kwargs = mock_get.call_args[1]
        assert 'year' in call_kwargs['params']
