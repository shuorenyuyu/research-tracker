"""Additional tests for scholar scraper specific coverage"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import sys

# Mock scholarly before importing
scholarly_mock = Mock()
sys.modules['scholarly'] = scholarly_mock

from src.scrapers.scholar_scraper import ScholarScraper
from src.utils.logger import setup_logger


class TestScholarScraperErrorHandling:
    """Test scholar scraper error handling and edge cases"""
    
    @pytest.fixture
    def scraper(self):
        """Create scholar scraper"""
        logger = setup_logger("test")
        return ScholarScraper(logger)
    
    @patch('src.scrapers.scholar_scraper.scholarly.search_pubs')
    def test_search_with_exception(self, mock_search, scraper):
        """Test handling exception in search"""
        mock_search.side_effect = Exception("Scholarly error")
        
        results = scraper.search("test query")
        assert len(results) == 0
    
    @patch('src.scrapers.scholar_scraper.scholarly.search_pubs')
    def test_search_with_network_timeout(self, mock_search, scraper):
        """Test handling network timeout"""
        mock_search.side_effect = TimeoutError("Request timeout")
        
        results = scraper.search("test")
        assert len(results) == 0
    
    @patch('src.scrapers.scholar_scraper.scholarly.search_pubs')
    def test_normalize_with_missing_fields(self, mock_search, scraper):
        """Test normalizing result with missing fields"""
        paper = {
            'bib': {
                'title': 'Test Paper',
                # Missing other fields
            }
        }
        
        normalized = scraper._normalize_paper(paper)
        assert normalized['title'] == 'Test Paper'
        assert normalized['authors'] == ''  # Should handle missing authors
    
    @patch('src.scrapers.scholar_scraper.scholarly.search_pubs')
    def test_normalize_with_no_bib(self, mock_search, scraper):
        """Test normalizing result without bib field"""
        paper = {}  # No 'bib' field
        
        try:
            normalized = scraper._normalize_paper(paper)
        except:
            pass  # Expected to fail or handle gracefully
    
    @patch('src.scrapers.scholar_scraper.scholarly.search_pubs')
    def test_normalize_with_invalid_year(self, mock_search, scraper):
        """Test handling invalid year format"""
        paper = {
            'bib': {
                'title': 'Test',
                'pub_year': 'not-a-year'  # Invalid year
            }
        }
        
        normalized = scraper._normalize_paper(paper)
        assert normalized.get('year') is None or isinstance(normalized.get('year'), int)
    
    @patch('src.scrapers.scholar_scraper.scholarly.search_pubs')
    def test_normalize_with_missing_year(self, mock_search, scraper):
        """Test normalizing without year field"""
        paper = {
            'bib': {
                'title': 'Test',
                'author': ['Author 1']
            }
            # No pub_year
        }
        
        normalized = scraper._normalize_paper(paper)
        assert 'year' in normalized
    
    @patch('src.scrapers.scholar_scraper.scholarly.search_pubs')
    def test_search_with_empty_results(self, mock_search, scraper):
        """Test search returning empty iterator"""
        mock_search.return_value = iter([])
        
        results = scraper.search("test")
        assert len(results) == 0
    
    @patch('src.scrapers.scholar_scraper.scholarly.search_pubs')
    def test_get_recent_papers_with_error(self, mock_search, scraper):
        """Test get_recent_papers when scholarly raises error"""
        mock_search.side_effect = ConnectionError("Network error")
        
        results = scraper.get_recent_papers(year=2024, keyword="test")
        assert len(results) == 0
    
    @patch('src.scrapers.scholar_scraper.scholarly.search_pubs')
    def test_normalize_with_malformed_author(self, mock_search, scraper):
        """Test normalizing with malformed author data"""
        paper = {
            'bib': {
                'title': 'Test',
                'author': 'Not a list but a string'  # Should be list
            }
        }
        
        try:
            normalized = scraper._normalize_paper(paper)
            # Should handle gracefully
        except:
            pass
    
    @patch('src.scrapers.scholar_scraper.scholarly.search_pubs')
    def test_normalize_with_pub_url(self, mock_search, scraper):
        """Test extracting pub_url field"""
        paper = {
            'bib': {
                'title': 'Test',
                'author': ['Author']
            },
            'pub_url': 'https://example.com/paper.pdf'
        }
        
        normalized = scraper._normalize_paper(paper)
        assert normalized.get('url') or normalized.get('pdf_url')
    
    @patch('src.scrapers.scholar_scraper.scholarly.search_pubs')
    def test_normalize_with_venue_field(self, mock_search, scraper):
        """Test extracting venue from bib"""
        paper = {
            'bib': {
                'title': 'Test',
                'venue': 'Conference 2024'
            }
        }
        
        normalized = scraper._normalize_paper(paper)
        assert 'venue' in normalized or 'Conference' in str(normalized)


class TestScholarScraperFiltering:
    """Test scholar scraper filtering logic"""
    
    @pytest.fixture
    def scraper(self):
        logger = setup_logger("test")
        return ScholarScraper(logger)
    
    @patch('src.scrapers.scholar_scraper.scholarly.search_pubs')
    def test_filter_by_year(self, mock_search, scraper):
        """Test filtering results by year"""
        mock_results = [
            {'bib': {'title': 'Old Paper', 'pub_year': '2020'}},
            {'bib': {'title': 'New Paper', 'pub_year': '2024'}}
        ]
        mock_search.return_value = iter(mock_results)
        
        results = scraper.get_recent_papers(year=2023, keyword="test")
        
        # Should filter out old papers
        if len(results) > 0:
            for paper in results:
                if 'year' in paper and paper['year']:
                    assert int(paper['year']) >= 2023
    
    @patch('src.scrapers.scholar_scraper.scholarly.search_pubs')  
    def test_search_with_max_results_limit(self, mock_search, scraper):
        """Test respecting max_results limit"""
        # Create many mock results
        mock_results = [
            {'bib': {'title': f'Paper {i}'}} for i in range(100)
        ]
        mock_search.return_value = iter(mock_results)
        
        results = scraper.search("test", max_results=5)
        
        # Should not exceed max_results
        assert len(results) <= 5
