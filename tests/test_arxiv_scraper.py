"""Tests for arXiv scraper"""
import pytest
from unittest.mock import Mock, patch
from datetime import datetime
import sys

# Mock arxiv module to avoid Python version issues
sys.modules['arxiv'] = Mock()

from src.scrapers.arxiv_scraper import ArxivScraper
from src.utils.logger import setup_logger


class TestArxivScraper:
    """Test ArxivScraper class"""
    
    @pytest.fixture
    def logger(self):
        """Create test logger"""
        return setup_logger("test_arxiv_scraper")
    
    @pytest.fixture
    def scraper(self, logger):
        """Create scraper instance"""
        return ArxivScraper(logger, rate_limit_delay=0)
    
    @pytest.fixture
    def sample_arxiv_entry(self):
        """Sample arXiv feed entry"""
        entry = Mock()
        entry.id = 'http://arxiv.org/abs/2401.12345v1'
        entry.title = 'Test Paper Title'
        entry.summary = 'Test abstract content'
        entry.published = '2024-01-15T10:00:00Z'
        entry.updated = '2024-01-16T10:00:00Z'
        
        author1 = Mock()
        author1.name = 'John Doe'
        author2 = Mock()
        author2.name = 'Jane Smith'
        entry.authors = [author1, author2]
        
        link1 = Mock()
        link1.rel = 'alternate'
        link2 = Mock()
        link2.rel = 'related'
        link2.title = 'pdf'
        link2.href = 'https://arxiv.org/pdf/2401.12345'
        entry.links = [link1, link2]
        
        tag1 = Mock()
        tag1.term = 'cs.AI'
        tag2 = Mock()
        tag2.term = 'cs.LG'
        entry.tags = [tag1, tag2]
        
        return entry
    
    def test_initialization(self, scraper):
        """Test scraper initialization"""
        assert scraper.rate_limit_delay == 0
        assert hasattr(scraper, 'BASE_URL')
    
    @patch('feedparser.parse')
    def test_search_success(self, mock_parse, scraper, sample_arxiv_entry):
        """Test successful search"""
        mock_feed = Mock()
        mock_feed.entries = [sample_arxiv_entry]
        mock_parse.return_value = mock_feed
        
        results = scraper.search('machine learning', max_results=10)
        
        assert len(results) == 1
        assert results[0]['title'] == 'Test Paper Title'
        assert results[0]['paper_id'] == '2401.12345v1'
    
    @patch('feedparser.parse')
    def test_search_with_max_results(self, mock_parse, scraper, sample_arxiv_entry):
        """Test search with max_results parameter"""
        mock_feed = Mock()
        mock_feed.entries = [sample_arxiv_entry] * 5
        mock_parse.return_value = mock_feed
        
        results = scraper.search('AI', max_results=3)
        
        # Should limit results
        assert len(results) <= 3
    
    @patch('feedparser.parse')
    def test_search_empty_results(self, mock_parse, scraper):
        """Test search with no results"""
        mock_feed = Mock()
        mock_feed.entries = []
        mock_parse.return_value = mock_feed
        
        results = scraper.search('nonexistent query')
        
        assert len(results) == 0
    
    @patch('feedparser.parse')
    def test_get_recent_papers(self, mock_parse, scraper, sample_arxiv_entry):
        """Test getting recent papers"""
        mock_feed = Mock()
        mock_feed.entries = [sample_arxiv_entry]
        mock_parse.return_value = mock_feed
        
        papers = scraper.get_recent_papers(['AI', 'ML'], days=7)
        
        assert len(papers) > 0
        # Should call parse for each keyword
        assert mock_parse.call_count >= 1
    
    @patch('feedparser.parse')
    def test_get_recent_papers_deduplication(self, mock_parse, scraper, sample_arxiv_entry):
        """Test that duplicate papers are removed"""
        mock_feed = Mock()
        # Same paper appears multiple times
        mock_feed.entries = [sample_arxiv_entry, sample_arxiv_entry]
        mock_parse.return_value = mock_feed
        
        papers = scraper.get_recent_papers(['AI'], days=1)
        
        # Should deduplicate by paper_id
        paper_ids = [p['paper_id'] for p in papers]
        assert len(paper_ids) == len(set(paper_ids))
    
    def test_normalize_paper(self, scraper, sample_arxiv_entry):
        """Test paper normalization"""
        normalized = scraper._normalize_paper(sample_arxiv_entry)
        
        assert normalized['title'] == 'Test Paper Title'
        assert normalized['paper_id'] == '2401.12345v1'
        assert normalized['source'] == 'arxiv'
        assert normalized['authors'] == 'John Doe, Jane Smith'
        assert normalized['abstract'] == 'Test abstract content'
        assert normalized['year'] == 2024
        assert normalized['venue'] == 'cs.AI, cs.LG'
        assert 'arxiv.org/pdf' in normalized['pdf_url']
    
    def test_normalize_paper_extracts_arxiv_id(self, scraper, sample_arxiv_entry):
        """Test arXiv ID extraction"""
        normalized = scraper._normalize_paper(sample_arxiv_entry)
        
        # Should extract just the ID from the URL
        assert '2401.12345' in normalized['paper_id']
        assert 'http://' not in normalized['paper_id']
    
    def test_normalize_paper_parses_date(self, scraper, sample_arxiv_entry):
        """Test publication date parsing"""
        normalized = scraper._normalize_paper(sample_arxiv_entry)
        
        assert normalized['publication_date'] is not None
        assert isinstance(normalized['publication_date'], datetime)
        assert normalized['publication_date'].year == 2024
    
    def test_normalize_paper_handles_missing_fields(self, scraper):
        """Test normalization with missing fields"""
        entry = Mock()
        entry.id = 'http://arxiv.org/abs/test'
        entry.title = 'Title Only'
        entry.summary = None
        entry.published = None
        entry.authors = []
        entry.links = []
        entry.tags = []
        
        normalized = scraper._normalize_paper(entry)
        
        assert normalized['title'] == 'Title Only'
        assert normalized['authors'] == ''
        assert normalized['abstract'] is None
    
    def test_build_search_url(self, scraper):
        """Test search URL construction"""
        url = scraper.BASE_URL
        assert 'arxiv.org' in url
        assert 'api/query' in url
