"""Tests for Semantic Scholar scraper"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from src.scrapers.semantic_scholar_scraper import SemanticScholarScraper
from src.utils.logger import setup_logger


class TestSemanticScholarScraper:
    """Test SemanticScholarScraper class"""
    
    @pytest.fixture
    def logger(self):
        """Create test logger"""
        return setup_logger("test_ss_scraper")
    
    @pytest.fixture
    def scraper(self, logger):
        """Create scraper instance"""
        return SemanticScholarScraper(logger, rate_limit_delay=0)
    
    @pytest.fixture
    def scraper_with_key(self, logger):
        """Create scraper with API key"""
        return SemanticScholarScraper(logger, rate_limit_delay=0, api_key="test_key")
    
    @pytest.fixture
    def sample_ss_paper(self):
        """Sample Semantic Scholar paper response"""
        return {
            'paperId': 'abc123',
            'externalIds': {'ArXiv': '2401.12345', 'DOI': '10.1234/test'},
            'title': 'Test Paper',
            'abstract': 'Test abstract',
            'venue': 'Test Conference',
            'year': 2024,
            'authors': [{'name': 'John Doe'}, {'name': 'Jane Smith'}],
            'citationCount': 42,
            'influentialCitationCount': 10,
            'publicationDate': '2024-01-15',
            'url': 'https://semanticscholar.org/paper/abc123',
            'openAccessPdf': {'url': 'https://example.com/paper.pdf'}
        }
    
    def test_initialization(self, scraper):
        """Test scraper initialization"""
        assert scraper.rate_limit_delay == 0
        assert scraper.api_key is None
    
    def test_initialization_with_api_key(self, scraper_with_key):
        """Test scraper initialization with API key"""
        assert scraper_with_key.api_key == "test_key"
        assert 'x-api-key' in scraper_with_key.headers
    
    @patch('requests.get')
    def test_search_success(self, mock_get, scraper, sample_ss_paper):
        """Test successful search"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'data': [sample_ss_paper]
        }
        mock_get.return_value = mock_response
        
        results = scraper.search('machine learning')
        
        assert len(results) == 1
        assert results[0]['title'] == 'Test Paper'
        assert results[0]['citation_count'] == 42
    
    @patch('requests.get')
    def test_search_with_filters(self, mock_get, scraper):
        """Test search with year and field filters"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'data': []}
        mock_get.return_value = mock_response
        
        scraper.search(
            'AI',
            max_results=50,
            year_filter='2024-',
            fields_of_study=['Computer Science']
        )
        
        call_args = mock_get.call_args
        params = call_args[1]['params']
        assert params['year'] == '2024-'
        assert 'Computer Science' in params['fieldsOfStudy']
    
    @patch('requests.get')
    def test_search_api_error(self, mock_get, scraper):
        """Test search with API error"""
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.json.return_value = {'message': 'Rate limited'}
        mock_get.return_value = mock_response
        
        results = scraper.search('test query')
        
        assert len(results) == 0
    
    @patch('requests.get')
    def test_get_paper_by_arxiv_id(self, mock_get, scraper, sample_ss_paper):
        """Test getting paper by arXiv ID"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_ss_paper
        mock_get.return_value = mock_response
        
        paper = scraper.get_paper_by_arxiv_id('2401.12345v1')
        
        assert paper is not None
        assert paper['title'] == 'Test Paper'
        # Should strip version number
        assert 'arXiv:2401.12345' in mock_get.call_args[0][0]
    
    @patch('requests.get')
    def test_get_paper_by_arxiv_id_not_found(self, mock_get, scraper):
        """Test getting non-existent paper"""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        paper = scraper.get_paper_by_arxiv_id('nonexistent')
        
        assert paper is None
    
    def test_normalize_paper(self, scraper, sample_ss_paper):
        """Test paper normalization"""
        normalized = scraper._normalize_paper(sample_ss_paper)
        
        assert normalized['title'] == 'Test Paper'
        assert normalized['paper_id'] == '2401.12345'  # Should use arXiv ID
        assert normalized['source'] == 'arxiv'
        assert normalized['authors'] == 'John Doe, Jane Smith'
        assert normalized['citation_count'] == 42
        assert normalized['year'] == 2024
    
    def test_normalize_paper_without_arxiv(self, scraper):
        """Test normalizing paper without arXiv ID"""
        paper = {
            'paperId': 'ss123',
            'title': 'Test',
            'externalIds': {},
            'year': 2024,
            'authors': [],
            'citationCount': 5
        }
        
        normalized = scraper._normalize_paper(paper)
        
        assert normalized['paper_id'] == 'ss123'
        assert normalized['source'] == 'semantic_scholar'
    
    @patch('requests.get')
    def test_get_recent_papers(self, mock_get, scraper, sample_ss_paper):
        """Test getting recent papers"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'data': [sample_ss_paper]}
        mock_get.return_value = mock_response
        
        papers = scraper.get_recent_papers(['AI', 'ML'])
        
        assert len(papers) > 0
        # Should only use first keyword (optimization)
        assert mock_get.call_count == 1
    
    @patch('requests.get')
    def test_enrich_papers_with_citations(self, mock_get, scraper):
        """Test enriching papers with citation data"""
        papers = [
            {'paper_id': '2401.001', 'title': 'Paper 1'},
            {'paper_id': '2401.002', 'title': 'Paper 2'}
        ]
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'paperId': 'test',
            'citationCount': 100
        }
        mock_get.return_value = mock_response
        
        enriched = scraper.enrich_papers_with_citations(papers, max_papers=2)
        
        assert len(enriched) == 2
    
    @patch('src.scrapers.semantic_scholar_scraper.requests.get')
    def test_get_with_retry(self, mock_get, scraper, sample_ss_paper):
        """Test retry logic"""
        # First call fails with HTTPError, second succeeds
        import requests
        mock_response_fail = Mock()
        mock_response_fail.status_code = 500
        mock_response_fail.raise_for_status.side_effect = requests.HTTPError("500 Server Error")
        
        mock_response_success = Mock()
        mock_response_success.status_code = 200
        mock_response_success.json.return_value = sample_ss_paper
        mock_response_success.raise_for_status.return_value = None
        
        mock_get.side_effect = [mock_response_fail, mock_response_success]
        
        paper = scraper._get_with_retry('2401.12345', max_retries=3)
        
        assert paper is not None
        assert mock_get.call_count == 2
    
    def test_base_url(self, scraper):
        """Test BASE_URL is set"""
        assert hasattr(scraper, 'BASE_URL')
        assert 'semanticscholar.org' in scraper.BASE_URL
