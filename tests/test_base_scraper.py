"""Tests for base scraper"""
import pytest
from src.scrapers.base_scraper import BaseScraper
from src.utils.logger import setup_logger


class ConcreteScraper(BaseScraper):
    """Concrete implementation for testing"""
    
    def search(self, query: str, max_results: int = 50):
        return [{'title': f'Result for {query}', 'id': '123'}]
    
    def get_recent_papers(self, keywords, days=1):
        return [{'title': f'Recent paper for {keywords[0]}', 'id': '456'}]


class TestBaseScraper:
    """Test BaseScraper abstract class"""
    
    @pytest.fixture
    def logger(self):
        """Create test logger"""
        return setup_logger("test_scraper")
    
    @pytest.fixture
    def scraper(self, logger):
        """Create concrete scraper instance"""
        return ConcreteScraper(logger)
    
    def test_scraper_initialization(self, scraper, logger):
        """Test scraper initialization"""
        assert scraper.logger == logger
    
    def test_search_method(self, scraper):
        """Test search method"""
        results = scraper.search("test query")
        assert len(results) > 0
        assert results[0]['title'] == 'Result for test query'
    
    def test_get_recent_papers_method(self, scraper):
        """Test get_recent_papers method"""
        results = scraper.get_recent_papers(['AI', 'ML'], days=7)
        assert len(results) > 0
        assert 'Recent paper' in results[0]['title']
    
    def test_normalize_paper_returns_dict(self, scraper):
        """Test _normalize_paper returns dict"""
        raw_paper = {'title': 'Test', 'authors': 'John Doe'}
        normalized = scraper._normalize_paper(raw_paper)
        assert isinstance(normalized, dict)
    
    def test_cannot_instantiate_abstract_class(self, logger):
        """Test that BaseScraper cannot be instantiated directly"""
        with pytest.raises(TypeError):
            BaseScraper(logger)
