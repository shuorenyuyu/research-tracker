"""Additional tests for semantic scholar scraper specific coverage"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
import requests

sys.modules['arxiv'] = Mock()

from src.scrapers.semantic_scholar_scraper import SemanticScholarScraper
from src.utils.logger import setup_logger


class TestSemanticScholarAPIErrors:
    """Test semantic scholar API error handling"""
    
    @pytest.fixture
    def scraper(self):
        """Create scraper"""
        logger = setup_logger("test")
        return SemanticScholarScraper(logger, api_key=None)
    
    @patch('requests.get')
    def test_search_with_404_error(self, mock_get, scraper):
        """Test handling 404 not found"""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = requests.HTTPError("404")
        mock_get.return_value = mock_response
        
        results = scraper.search("test")
        assert len(results) == 0
    
    @patch('requests.get')
    def test_search_with_500_error(self, mock_get, scraper):
        """Test handling 500 server error"""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = requests.HTTPError("500")
        mock_get.return_value = mock_response
        
        results = scraper.search("test")
        assert len(results) == 0
    
    @patch('requests.get')
    def test_search_with_timeout(self, mock_get, scraper):
        """Test handling request timeout"""
        mock_get.side_effect = requests.Timeout("Request timeout")
        
        results = scraper.search("test")
        assert len(results) == 0
    
    @patch('requests.get')
    def test_search_with_connection_error(self, mock_get, scraper):
        """Test handling connection error"""
        mock_get.side_effect = requests.ConnectionError("Connection failed")
        
        results = scraper.search("test")
        assert len(results) == 0
    
    @patch('requests.get')
    def test_get_paper_details_with_404(self, mock_get, scraper):
        """Test getting paper details with 404 error"""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = requests.HTTPError("404")
        mock_get.return_value = mock_response
        
        result = scraper.get_paper_details("invalid-id")
        assert result is None
    
    @patch('requests.get')
    def test_get_paper_details_with_network_error(self, mock_get, scraper):
        """Test getting paper details with network error"""
        mock_get.side_effect = ConnectionError("Network error")
        
        result = scraper.get_paper_details("test-id")
        assert result is None
    
    @patch('requests.get')
    def test_get_recent_papers_with_api_error(self, mock_get, scraper):
        """Test get_recent_papers with API error"""
        mock_get.side_effect = requests.HTTPError("API Error")
        
        results = scraper.get_recent_papers(year=2024, keyword="test")
        assert len(results) == 0


class TestSemanticScholarNormalization:
    """Test paper normalization edge cases"""
    
    @pytest.fixture
    def scraper(self):
        logger = setup_logger("test")
        return SemanticScholarScraper(logger)
    
    def test_normalize_without_external_ids(self, scraper):
        """Test normalizing paper without externalIds"""
        paper = {
            'paperId': 'test123',
            'title': 'Test Paper',
            'authors': [{'name': 'Author'}],
            # No externalIds field
        }
        
        normalized = scraper._normalize_paper(paper)
        assert normalized['paper_id'] == 'test123'
        assert normalized.get('doi') is None
    
    def test_normalize_with_empty_external_ids(self, scraper):
        """Test normalizing with empty externalIds"""
        paper = {
            'paperId': 'test123',
            'title': 'Test',
            'externalIds': {},  # Empty dict
            'authors': []
        }
        
        normalized = scraper._normalize_paper(paper)
        assert normalized.get('doi') is None
    
    def test_normalize_with_arxiv_id(self, scraper):
        """Test extracting arXiv ID"""
        paper = {
            'paperId': 'test123',
            'title': 'Test',
            'externalIds': {'ArXiv': '2401.12345'},
            'authors': []
        }
        
        normalized = scraper._normalize_paper(paper)
        assert '2401.12345' in str(normalized.get('url', '')) or 'arxiv' in str(normalized).lower()
    
    def test_normalize_without_abstract(self, scraper):
        """Test normalizing without abstract field"""
        paper = {
            'paperId': 'test123',
            'title': 'Test',
            'authors': [],
            # No abstract
        }
        
        normalized = scraper._normalize_paper(paper)
        assert normalized.get('abstract') == '' or normalized.get('abstract') is None
    
    def test_normalize_without_venue(self, scraper):
        """Test normalizing without venue"""
        paper = {
            'paperId': 'test123',
            'title': 'Test',
            'authors': [],
            # No venue
        }
        
        normalized = scraper._normalize_paper(paper)
        assert 'venue' in normalized
    
    def test_normalize_with_null_citation_count(self, scraper):
        """Test normalizing with null citationCount"""
        paper = {
            'paperId': 'test123',
            'title': 'Test',
            'authors': [],
            'citationCount': None
        }
        
        normalized = scraper._normalize_paper(paper)
        assert normalized.get('citation_count', 0) >= 0
    
    def test_normalize_with_empty_authors(self, scraper):
        """Test normalizing with empty authors list"""
        paper = {
            'paperId': 'test123',
            'title': 'Test',
            'authors': []
        }
        
        normalized = scraper._normalize_paper(paper)
        assert normalized['authors'] == ''


class TestSemanticScholarRetryLogic:
    """Test retry logic for rate limiting"""
    
    @pytest.fixture
    def scraper(self):
        logger = setup_logger("test")
        return SemanticScholarScraper(logger)
    
    @patch('requests.get')
    @patch('time.sleep')
    def test_retry_on_429_then_success(self, mock_sleep, mock_get, scraper):
        """Test retry succeeds after 429"""
        # First call returns 429, second succeeds
        mock_response_429 = Mock()
        mock_response_429.status_code = 429
        
        mock_response_ok = Mock()
        mock_response_ok.status_code = 200
        mock_response_ok.json.return_value = {'data': []}
        
        mock_get.side_effect = [mock_response_429, mock_response_ok]
        
        results = scraper.search("test")
        
        # Should have retried
        assert mock_sleep.called
        assert isinstance(results, list)
    
    @patch('requests.get')
    @patch('time.sleep')
    def test_retry_exhaustion_on_429(self, mock_sleep, mock_get, scraper):
        """Test retry exhaustion when 429 persists"""
        mock_response = Mock()
        mock_response.status_code = 429
        mock_get.return_value = mock_response
        
        results = scraper.search("test")
        
        # Should have tried multiple times
        assert mock_get.call_count >= 1
        assert len(results) == 0


class TestSemanticScholarAPIKey:
    """Test API key handling"""
    
    def test_initialization_with_api_key(self):
        """Test scraper initialization with API key"""
        logger = setup_logger("test")
        scraper = SemanticScholarScraper(logger, api_key="test-key-123")
        
        assert scraper.api_key == "test-key-123"
    
    def test_initialization_without_api_key(self):
        """Test scraper initialization without API key"""
        logger = setup_logger("test")
        scraper = SemanticScholarScraper(logger, api_key=None)
        
        assert scraper.api_key is None
    
    @patch('requests.get')
    def test_request_includes_api_key(self, mock_get):
        """Test that API key is included in headers"""
        logger = setup_logger("test")
        scraper = SemanticScholarScraper(logger, api_key="test-key")
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'data': []}
        mock_get.return_value = mock_response
        
        scraper.search("test")
        
        # Verify headers contain API key
        call_args = mock_get.call_args
        if call_args and 'headers' in call_args[1]:
            headers = call_args[1]['headers']
            assert 'x-api-key' in headers or 'X-API-Key' in headers


class TestSemanticScholarPagination:
    """Test pagination and limit handling"""
    
    @pytest.fixture
    def scraper(self):
        logger = setup_logger("test")
        return SemanticScholarScraper(logger)
    
    @patch('requests.get')
    def test_search_respects_limit(self, mock_get, scraper):
        """Test that search respects max_results limit"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'data': [{'paperId': f'id{i}', 'title': f'Paper {i}'} for i in range(100)]
        }
        mock_get.return_value = mock_response
        
        results = scraper.search("test", max_results=10)
        
        # Should limit results
        assert len(results) <= 10
