"""arXiv scraper using arxiv library"""

import time
import arxiv
from typing import List, Dict, Any
from datetime import datetime, timedelta
from .base_scraper import BaseScraper


class ArxivScraper(BaseScraper):
    """Scraper for arXiv papers"""
    
    def __init__(self, logger, rate_limit_delay: int = 3):
        """
        Initialize arXiv scraper
        
        Args:
            logger: Logger instance
            rate_limit_delay: Delay between requests (arXiv is more lenient)
        """
        super().__init__(logger)
        self.rate_limit_delay = rate_limit_delay
        self.client = arxiv.Client()
    
    def search(self, query: str, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Search arXiv for papers
        
        Args:
            query: Search query
            max_results: Maximum number of results
            
        Returns:
            List of normalized papers
        """
        papers = []
        
        try:
            self.logger.info(f"Searching arXiv for: '{query}'")
            
            search = arxiv.Search(
                query=query,
                max_results=max_results,
                sort_by=arxiv.SortCriterion.SubmittedDate,
                sort_order=arxiv.SortOrder.Descending
            )
            
            for result in self.client.results(search):
                try:
                    paper = self._normalize_paper(result)
                    papers.append(paper)
                except Exception as e:
                    self.logger.warning(f"Error processing arXiv paper: {e}")
                    continue
            
            self.logger.info(f"Found {len(papers)} papers from arXiv for: '{query}'")
            
        except Exception as e:
            self.logger.error(f"Error searching arXiv: {e}")
        
        return papers
    
    def get_recent_papers(self, keywords: List[str], days: int = 60, 
                          min_age_days: int = 0) -> List[Dict[str, Any]]:
        """
        Get recent papers from arXiv with optional minimum age for citation accumulation
        
        Args:
            keywords: List of keywords to search
            days: Look back this many days from min_age_days (default 60)
            min_age_days: Minimum age in days (0 = include all recent papers)
            
        Returns:
            List of papers
        """
        all_papers = []
        from datetime import timezone
        
        # Calculate date range
        cutoff_date_end = datetime.now(timezone.utc) - timedelta(days=min_age_days)
        cutoff_date_start = cutoff_date_end - timedelta(days=days)
        
        self.logger.info(f"Fetching papers from {cutoff_date_start.date()} to {cutoff_date_end.date()}")
        
        # arXiv categories for AI/Robotics
        categories = [
            'cs.AI',  # Artificial Intelligence
            'cs.LG',  # Machine Learning
            'cs.CV',  # Computer Vision
            'cs.CL',  # Computation and Language (NLP)
            'cs.RO',  # Robotics
            'cs.NE',  # Neural and Evolutionary Computing
        ]
        
        for keyword in keywords:
            try:
                # Build query combining keyword with categories
                category_query = ' OR '.join([f'cat:{cat}' for cat in categories])
                query = f'({category_query}) AND (all:{keyword})'
                
                self.logger.info(f"Fetching arXiv papers for: '{keyword}'")
                
                # Fetch many more papers to reach older dates
                # arXiv returns newest first, so we need to fetch enough to reach our target window
                max_results = 500 if min_age_days > 30 else 100
                papers = self.search(query, max_results=max_results)
                
                # Filter by submission date window
                if min_age_days > 0:
                    # Filter to specific date range
                    recent_papers = [
                        p for p in papers 
                        if p.get('publication_date') and 
                        cutoff_date_start <= p['publication_date'] <= cutoff_date_end
                    ]
                else:
                    # Just use cutoff from today
                    recent_papers = [
                        p for p in papers 
                        if p.get('publication_date') and 
                        p['publication_date'] >= cutoff_date_start
                    ]
                
                all_papers.extend(recent_papers)
                
                # Rate limiting
                time.sleep(self.rate_limit_delay)
                
            except Exception as e:
                self.logger.error(f"Error fetching arXiv papers for '{keyword}': {e}")
                continue
        
        # Remove duplicates
        unique_papers = []
        seen_ids = set()
        
        for paper in all_papers:
            paper_id = paper.get('paper_id')
            if paper_id not in seen_ids:
                seen_ids.add(paper_id)
                unique_papers.append(paper)
        
        self.logger.info(f"Total unique arXiv papers found: {len(unique_papers)}")
        return unique_papers
    
    def _normalize_paper(self, raw_paper: arxiv.Result) -> Dict[str, Any]:
        """
        Normalize arXiv paper to standard format
        
        Args:
            raw_paper: arXiv Result object
            
        Returns:
            Normalized paper dictionary
        """
        # Extract authors
        authors = ', '.join([author.name for author in raw_paper.authors])
        first_author = raw_paper.authors[0].name if raw_paper.authors else ''
        
        # Extract year
        year = raw_paper.published.year if raw_paper.published else None
        
        # Get primary category as venue
        venue = raw_paper.primary_category if raw_paper.primary_category else ''
        
        return {
            "title": raw_paper.title,
            "paper_id": raw_paper.entry_id.split('/')[-1],  # arXiv ID
            "source": "arxiv",
            "authors": authors,
            "first_author": first_author,
            "year": year,
            "publication_date": raw_paper.published,
            "venue": venue,
            "publisher": "arXiv",
            "abstract": raw_paper.summary,
            "url": raw_paper.entry_id,
            "pdf_url": raw_paper.pdf_url,
            "citation_count": 0,  # arXiv doesn't provide citation count
            "fetched_at": datetime.utcnow()
        }
