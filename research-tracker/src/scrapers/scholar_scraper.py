"""Google Scholar scraper using scholarly library"""

import time
from typing import List, Dict, Any
from datetime import datetime, timedelta
from scholarly import scholarly, ProxyGenerator
from .base_scraper import BaseScraper


class ScholarScraper(BaseScraper):
    """Scraper for Google Scholar papers"""
    
    def __init__(self, logger, rate_limit_delay: int = 3, use_proxy: bool = False):
        """
        Initialize Scholar scraper
        
        Args:
            logger: Logger instance
            rate_limit_delay: Delay between requests in seconds
            use_proxy: Whether to use proxy (optional)
        """
        super().__init__(logger)
        self.rate_limit_delay = rate_limit_delay
        
        # Set up proxy if requested (optional, helps avoid rate limiting)
        if use_proxy:
            try:
                pg = ProxyGenerator()
                pg.FreeProxies()
                scholarly.use_proxy(pg)
                self.logger.info("Proxy enabled for Google Scholar")
            except Exception as e:
                self.logger.warning(f"Failed to set up proxy: {e}. Continuing without proxy.")
    
    def search(self, query: str, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Search Google Scholar for papers
        
        Args:
            query: Search query
            max_results: Maximum number of results
            
        Returns:
            List of normalized papers
        """
        papers = []
        
        try:
            self.logger.info(f"Searching Google Scholar for: '{query}'")
            search_query = scholarly.search_pubs(query)
            
            for i, result in enumerate(search_query):
                if i >= max_results:
                    break
                
                try:
                    paper = self._normalize_paper(result)
                    papers.append(paper)
                    
                    # Rate limiting
                    if i < max_results - 1:
                        time.sleep(self.rate_limit_delay)
                        
                except Exception as e:
                    self.logger.warning(f"Error processing paper {i+1}: {e}")
                    continue
            
            self.logger.info(f"Found {len(papers)} papers for query: '{query}'")
            
        except Exception as e:
            self.logger.error(f"Error searching Google Scholar: {e}")
        
        return papers
    
    def get_recent_papers(self, keywords: List[str], days: int = 1) -> List[Dict[str, Any]]:
        """
        Get recent papers from Google Scholar
        
        Args:
            keywords: List of keywords to search
            days: Look back this many days
            
        Returns:
            List of papers
        """
        all_papers = []
        current_year = datetime.now().year
        
        for keyword in keywords:
            try:
                # Build query with year filter for recent papers
                query = f"{keyword} after:{current_year-1}"
                self.logger.info(f"Fetching recent papers for: '{keyword}'")
                
                papers = self.search(query, max_results=20)
                
                # Filter by date if publication date is available
                cutoff_date = datetime.now() - timedelta(days=days)
                filtered_papers = []
                
                for paper in papers:
                    # If we have publication date, filter by it
                    if paper.get("publication_date"):
                        if paper["publication_date"] >= cutoff_date:
                            filtered_papers.append(paper)
                    else:
                        # If no date, include if year matches
                        if paper.get("year") and paper["year"] >= current_year:
                            filtered_papers.append(paper)
                
                all_papers.extend(filtered_papers if filtered_papers else papers[:10])
                
                # Rate limiting between keywords
                time.sleep(self.rate_limit_delay)
                
            except Exception as e:
                self.logger.error(f"Error fetching papers for keyword '{keyword}': {e}")
                continue
        
        # Remove duplicates based on title
        unique_papers = []
        seen_titles = set()
        
        for paper in all_papers:
            title_lower = paper["title"].lower()
            if title_lower not in seen_titles:
                seen_titles.add(title_lower)
                unique_papers.append(paper)
        
        self.logger.info(f"Total unique recent papers found: {len(unique_papers)}")
        return unique_papers
    
    def _normalize_paper(self, raw_paper: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize Google Scholar paper to standard format
        
        Args:
            raw_paper: Raw paper dict from scholarly
            
        Returns:
            Normalized paper dictionary
        """
        # Extract basic info
        title = raw_paper.get('bib', {}).get('title', 'Unknown Title')
        
        # Get authors
        authors_list = raw_paper.get('bib', {}).get('author', [])
        if isinstance(authors_list, list):
            authors = ', '.join(authors_list)
            first_author = authors_list[0] if authors_list else ''
        else:
            authors = str(authors_list)
            first_author = authors.split(',')[0] if authors else ''
        
        # Get year
        year = raw_paper.get('bib', {}).get('pub_year')
        if year:
            try:
                year = int(year)
            except (ValueError, TypeError):
                year = None
        
        # Get venue/publication
        venue = raw_paper.get('bib', {}).get('venue', '')
        publisher = raw_paper.get('bib', {}).get('publisher', '')
        
        # Get abstract
        abstract = raw_paper.get('bib', {}).get('abstract', '')
        
        # Get URLs
        url = raw_paper.get('pub_url', '') or raw_paper.get('eprint_url', '')
        pdf_url = raw_paper.get('eprint_url', '')
        
        # Get citation count
        citation_count = raw_paper.get('num_citations', 0)
        
        # Generate paper ID (use scholar ID or hash of title)
        paper_id = raw_paper.get('author_id', '') or f"scholar_{hash(title)}"
        
        # Try to construct publication date
        publication_date = None
        if year:
            try:
                publication_date = datetime(year, 1, 1)
            except:
                pass
        
        return {
            "title": title,
            "paper_id": paper_id,
            "source": "scholar",
            "authors": authors,
            "first_author": first_author,
            "year": year,
            "publication_date": publication_date,
            "venue": venue,
            "publisher": publisher,
            "abstract": abstract,
            "url": url,
            "pdf_url": pdf_url,
            "citation_count": citation_count,
            "fetched_at": datetime.utcnow()
        }
