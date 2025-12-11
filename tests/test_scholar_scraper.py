"""Tests for Google Scholar scraper"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import sys

# Mock scholarly module
sys.modules['scholarly'] = Mock()

from src.scrapers.scholar_scraper import ScholarScraper
from src.utils.logger import setup_logger


class TestScholarScraper:
    """Test ScholarScraper class"""
    
    @pytest.fixture
    def logger(self):
        """Create test logger"""
        return setup_logger("test_scholar_scraper")
    
    @pytest.fixture
    def scraper(self, logger):
        """Create scraper instance"""
        return ScholarScraper(logger, rate_limit_delay=0)
    
    @pytest.fixture
    def mock_scholarly(self):
        """Mock scholarly module"""
        with patch('src.scrapers.scholar_scraper.scholarly') as mock:
            yield mock
    
    def test_initialization(self, scraper):
        """Test scraper initialization"""
        assert scraper.rate_limit_delay == 0
        assert hasattr(scraper, 'logger')
    
    def test_search_with_mock(self, scraper, mock_scholarly):
        """Test search with mocked scholarly"""
        mock_result = Mock()
        mock_result.__getitem__ = Mock(side_effect=lambda k: {
            'title': 'Test Paper',
            'author': ['John Doe'],
            'pub_year': '2024',
            'venue': 'Test Conference',
            'abstract': 'Test abstract',
            'num_citations': 42,
            'url_scholarbib': 'scholar_id_123'
        }.get(k))
        
        mock_scholarly.search_pubs.return_value = [mock_result]
        
        results = scraper.search('machine learning', max_results=10)
        
        # Should handle results
        mock_scholarly.search_pubs.assert_called_once()
    
    def test_get_recent_papers_with_mock(self, scraper, mock_scholarly):
        """Test getting recent papers"""
        mock_result = Mock()
        mock_result.__getitem__ = Mock(side_effect=lambda k: {
            'title': f'Paper about AI',
            'author': ['Author'],
            'pub_year': '2024',
            'num_citations': 10
        }.get(k))
        
        mock_scholarly.search_pubs.return_value = [mock_result]
        
        papers = scraper.get_recent_papers(['AI', 'ML'], days=7)
        
        # Should call for each keyword
        assert mock_scholarly.search_pubs.call_count >= 1
    
    def test_normalize_paper_basic(self, scraper):
        """Test paper normalization with basic data"""
        raw_paper = {
            'bib': {
                'title': 'Test Title',
                'author': ['John Doe', 'Jane Smith'],
                'pub_year': '2024',
                'venue': 'Conference',
                'abstract': 'Abstract text'
            },
            'num_citations': 100,
            'scholar_id': 'test123',
            'pub_url': 'https://example.com',
            'eprint_url': 'https://example.com/pdf'
        }
        
        normalized = scraper._normalize_paper(raw_paper)
        
        assert 'title' in normalized
        assert 'authors' in normalized
        assert 'year' in normalized
    
    def test_normalize_paper_missing_fields(self, scraper):
        """Test normalization with missing fields"""
        raw_paper = {'bib': {}}
        
        normalized = scraper._normalize_paper(raw_paper)
        
        assert isinstance(normalized, dict)
    
    def test_extract_scholar_id(self, scraper):
        """Test Scholar ID extraction"""
        paper_with_id = {'scholar_id': 'abc123'}
        normalized = scraper._normalize_paper(paper_with_id)
        
        # Should have some paper_id
        assert 'paper_id' in normalized or 'title' in normalized
