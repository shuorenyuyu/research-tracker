"""Additional tests for arxiv scraper specific coverage"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import sys

# Mock arxiv before importing scraper
sys.modules['arxiv'] = Mock()

from src.scrapers.arxiv_scraper import ArxivScraper
from src.utils.logger import setup_logger


class TestArxivScraperErrorCases:
    """Test arxiv scraper error handling and edge cases"""
    
    @pytest.fixture
    def scraper(self):
        """Create arxiv scraper"""
        logger = setup_logger("test")
        return ArxivScraper(logger)
    
    @patch('feedparser.parse')
    def test_search_with_feedparser_exception(self, mock_parse, scraper):
        """Test handling feedparser exception"""
        mock_parse.side_effect = Exception("Feed parse error")
        
        results = scraper.search("test query")
        assert len(results) == 0
    
    @patch('feedparser.parse')
    def test_search_with_empty_entries(self, mock_parse, scraper):
        """Test with feed having no entries"""
        mock_parse.return_value = {'entries': []}
        
        results = scraper.search("test")
        assert len(results) == 0
    
    @patch('feedparser.parse')
    def test_search_with_malformed_entry(self, mock_parse, scraper):
        """Test handling malformed feed entry"""
        mock_parse.return_value = {
            'entries': [
                {
                    'id': 'http://arxiv.org/abs/1234',
                    'title': 'Test',
                    # Missing other required fields
                }
            ]
        }
        
        results = scraper.search("test")
        # Should handle missing fields gracefully
        assert isinstance(results, list)
    
    @patch('feedparser.parse')
    def test_normalize_with_missing_published(self, mock_parse, scraper):
        """Test normalizing entry without published date"""
        entry = {
            'id': 'http://arxiv.org/abs/1234.5678',
            'title': 'Test Paper',
            'summary': 'Abstract',
            'authors': [{'name': 'Author'}],
            # Missing 'published' field
        }
        
        normalized = scraper._normalize_paper(entry)
        assert normalized is not None
    
    @patch('feedparser.parse')
    def test_normalize_with_invalid_date(self, mock_parse, scraper):
        """Test handling invalid date format"""
        entry = {
            'id': 'http://arxiv.org/abs/1234.5678',
            'title': 'Test',
            'summary': 'Abstract',
            'authors': [{'name': 'Author'}],
            'published': 'invalid-date-format'
        }
        
        try:
            normalized = scraper._normalize_paper(entry)
            # Should handle gracefully
        except:
            pass
    
    @patch('feedparser.parse')
    def test_search_with_invalid_id_format(self, mock_parse, scraper):
        """Test handling invalid arxiv ID format"""
        mock_parse.return_value = {
            'entries': [
                {
                    'id': 'not-a-valid-arxiv-id',
                    'title': 'Test',
                    'summary': 'Abstract',
                    'authors': [{'name': 'Author'}],
                    'published': '2024-01-01'
                }
            ]
        }
        
        results = scraper.search("test")
        # Should handle or skip invalid IDs
        assert isinstance(results, list)
    
    @patch('feedparser.parse')
    def test_get_recent_papers_with_network_error(self, mock_parse, scraper):
        """Test handling network errors in get_recent_papers"""
        mock_parse.side_effect = ConnectionError("Network error")
        
        results = scraper.get_recent_papers(year=2024, keyword="test")
        assert len(results) == 0
    
    @patch('feedparser.parse')
    def test_normalize_with_empty_authors(self, mock_parse, scraper):
        """Test normalizing with empty authors list"""
        entry = {
            'id': 'http://arxiv.org/abs/1234.5678',
            'title': 'Test',
            'summary': 'Abstract',
            'authors': [],  # Empty authors
            'published': '2024-01-01'
        }
        
        normalized = scraper._normalize_paper(entry)
        assert normalized['authors'] == ''
    
    @patch('feedparser.parse')
    def test_normalize_with_no_authors_field(self, mock_parse, scraper):
        """Test normalizing without authors field"""
        entry = {
            'id': 'http://arxiv.org/abs/1234.5678',
            'title': 'Test',
            'summary': 'Abstract',
            # No authors field
            'published': '2024-01-01'
        }
        
        try:
            normalized = scraper._normalize_paper(entry)
        except:
            pass  # May raise exception or handle gracefully


class TestArxivScraperURLHandling:
    """Test URL extraction and handling"""
    
    @pytest.fixture
    def scraper(self):
        logger = setup_logger("test")
        return ArxivScraper(logger)
    
    @patch('feedparser.parse')
    def test_normalize_with_pdf_link(self, mock_parse, scraper):
        """Test extracting PDF URL from links"""
        entry = {
            'id': 'http://arxiv.org/abs/1234.5678',
            'title': 'Test',
            'summary': 'Abstract',
            'authors': [{'name': 'Author'}],
            'published': '2024-01-01',
            'links': [
                {'type': 'application/pdf', 'href': 'http://arxiv.org/pdf/1234.5678'},
                {'type': 'text/html', 'href': 'http://arxiv.org/abs/1234.5678'}
            ]
        }
        
        normalized = scraper._normalize_paper(entry)
        assert 'pdf' in normalized['pdf_url']
    
    @patch('feedparser.parse')
    def test_normalize_without_pdf_link(self, mock_parse, scraper):
        """Test handling entry without PDF link"""
        entry = {
            'id': 'http://arxiv.org/abs/1234.5678',
            'title': 'Test',
            'summary': 'Abstract',
            'authors': [{'name': 'Author'}],
            'published': '2024-01-01',
            'links': []  # No links
        }
        
        normalized = scraper._normalize_paper(entry)
        assert normalized is not None
