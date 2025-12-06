"""Base scraper interface"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any
from datetime import datetime


class BaseScraper(ABC):
    """Abstract base class for all scrapers"""
    
    def __init__(self, logger):
        self.logger = logger
    
    @abstractmethod
    def search(self, query: str, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Search for papers matching the query
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            
        Returns:
            List of paper dictionaries
        """
        pass
    
    @abstractmethod
    def get_recent_papers(self, keywords: List[str], days: int = 1) -> List[Dict[str, Any]]:
        """
        Get papers published in the last N days
        
        Args:
            keywords: List of keywords to search for
            days: Number of days to look back
            
        Returns:
            List of paper dictionaries
        """
        pass
    
    def _normalize_paper(self, raw_paper: Any) -> Dict[str, Any]:
        """
        Normalize paper data to standard format
        
        Args:
            raw_paper: Raw paper object from API
            
        Returns:
            Normalized paper dictionary
        """
        return {
            "title": "",
            "paper_id": "",
            "source": "",
            "authors": "",
            "first_author": "",
            "year": None,
            "publication_date": None,
            "venue": "",
            "publisher": "",
            "abstract": "",
            "url": "",
            "pdf_url": "",
            "citation_count": 0,
            "fetched_at": datetime.utcnow()
        }
