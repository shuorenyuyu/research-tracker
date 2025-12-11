"""OpenAlex API scraper for research papers - free alternative to Semantic Scholar"""

import time
import requests
from typing import List, Dict, Any, Optional
from .base_scraper import BaseScraper


class OpenAlexScraper(BaseScraper):
    """
    Scraper for OpenAlex API (free, no API key required)
    
    Features:
    - 200M+ papers with citation data
    - 10 requests/second rate limit (no registration!)
    - Replacement for Microsoft Academic Graph
    - Full metadata: abstracts, citations, authors, venues
    
    API Docs: https://docs.openalex.org/
    """
    
    BASE_URL = "https://api.openalex.org"
    
    def __init__(self, logger, rate_limit_delay: int = 1):
        """
        Initialize OpenAlex scraper
        
        Args:
            logger: Logger instance
            rate_limit_delay: Seconds to wait between requests (default 1s for 10 req/sec limit)
        """
        super().__init__(logger)
        self.rate_limit_delay = rate_limit_delay
        self.headers = {
            'User-Agent': 'ResearchTracker/1.0 (mailto:research@example.com)',  # Polite API usage
            'Accept': 'application/json'
        }
    
    def _normalize_paper(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize OpenAlex paper to standard format
        
        Args:
            item: Raw OpenAlex work object
            
        Returns:
            Normalized paper dictionary
        """
        # Extract authors
        authors_list = []
        for authorship in item.get('authorships', []):
            author = authorship.get('author', {})
            if author.get('display_name'):
                authors_list.append(author['display_name'])
        
        authors_str = ', '.join(authors_list) if authors_list else 'Unknown'
        
        # Extract abstract (inverted index format)
        abstract = self._extract_abstract(item.get('abstract_inverted_index'))
        
        # Extract venue
        venue = None
        if item.get('primary_location'):
            source = item['primary_location'].get('source', {})
            venue = source.get('display_name')
        
        # Extract publication year
        year = item.get('publication_year')
        
        # Extract DOI
        doi = item.get('doi')
        if doi and doi.startswith('https://doi.org/'):
            doi = doi.replace('https://doi.org/', '')
        
        # Extract PDF URL
        pdf_url = None
        if item.get('primary_location', {}).get('pdf_url'):
            pdf_url = item['primary_location']['pdf_url']
        elif item.get('open_access', {}).get('oa_url'):
            pdf_url = item['open_access']['oa_url']
        
        return {
            'paper_id': item.get('id', '').replace('https://openalex.org/', ''),  # Clean ID
            'source': 'openalex',
            'title': item.get('title', '').strip(),
            'authors': authors_str,
            'year': year,
            'venue': venue,
            'abstract': abstract or 'No abstract available',
            'url': item.get('id', ''),  # OpenAlex URL
            'pdf_url': pdf_url,
            'doi': doi,
            'citation_count': item.get('cited_by_count', 0),
            'keywords': ', '.join(self._extract_concepts(item.get('concepts', [])))
        }
    
    def _extract_abstract(self, inverted_index: Optional[Dict[str, List[int]]]) -> Optional[str]:
        """
        Convert OpenAlex inverted index to abstract text
        
        Args:
            inverted_index: Dictionary mapping words to position indices
            
        Returns:
            Reconstructed abstract text or None
        """
        if not inverted_index:
            return None
        
        try:
            # Create list to hold words in correct positions
            max_pos = max(max(positions) for positions in inverted_index.values())
            words = [''] * (max_pos + 1)
            
            # Place each word at its positions
            for word, positions in inverted_index.items():
                for pos in positions:
                    words[pos] = word
            
            # Join words and clean up
            abstract = ' '.join(words).strip()
            return abstract if abstract else None
        except Exception as e:
            self.logger.warning(f"Error extracting abstract: {e}")
            return None
    
    def _extract_concepts(self, concepts: List[Dict[str, Any]]) -> List[str]:
        """
        Extract top concepts/keywords from OpenAlex concepts
        
        Args:
            concepts: List of concept objects with scores
            
        Returns:
            List of top 5 concept names
        """
        # Sort by score and take top 5
        sorted_concepts = sorted(concepts, key=lambda c: c.get('score', 0), reverse=True)
        return [c.get('display_name', '') for c in sorted_concepts[:5] if c.get('display_name')]
    
    def search(self, query: str, max_results: int = 100, 
               year_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Search OpenAlex for papers
        
        Args:
            query: Search query (will search title and abstract)
            max_results: Maximum results to return (max 200 per page)
            year_filter: Year filter like "2024" or ">2023"
            
        Returns:
            List of normalized papers sorted by citations
        """
        papers = []
        
        try:
            self.logger.info(f"Searching OpenAlex for: '{query}'")
            
            # Build filter string
            filters = [f"default.search:{query}"]
            
            if year_filter:
                # Convert "2024-" format to ">2023"
                if year_filter.endswith('-'):
                    year = int(year_filter[:-1])
                    filters.append(f"publication_year:>{year-1}")
                else:
                    filters.append(f"publication_year:{year_filter}")
            
            # Build request parameters
            params = {
                'filter': ','.join(filters),
                'sort': 'cited_by_count:desc',  # Sort by citations
                'per-page': min(max_results, 200),  # Max 200 per page
                'page': 1
            }
            
            url = f"{self.BASE_URL}/works"
            response = requests.get(url, params=params, headers=self.headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                results = data.get('results', [])
                
                for item in results:
                    try:
                        paper = self._normalize_paper(item)
                        if paper.get('title'):  # Only add if has title
                            papers.append(paper)
                    except Exception as e:
                        self.logger.warning(f"Error processing OpenAlex paper: {e}")
                        continue
                
                self.logger.info(f"Found {len(papers)} papers from OpenAlex")
            else:
                self.logger.error(f"OpenAlex API error: {response.status_code} - {response.text}")
            
            time.sleep(self.rate_limit_delay)
            
        except Exception as e:
            self.logger.error(f"Error searching OpenAlex: {e}")
        
        return papers
    
    def get_recent_papers(self, keywords: List[str], days: int = 7) -> List[Dict[str, Any]]:
        """
        Get recent high-impact papers from OpenAlex
        
        Args:
            keywords: List of search keywords (will use first one for simplicity)
            days: Days parameter (converted to year filter for better results)
            
        Returns:
            List of papers sorted by citations
        """
        # For OpenAlex, use year filter instead of days (more papers)
        # If days=180, search from current year
        import datetime
        current_year = datetime.datetime.now().year
        
        if days >= 180:
            year_filter = f"{current_year}"
        else:
            year_filter = f">{current_year - 1}"  # Recent papers
        
        # Use first keyword for search (to avoid rate limits)
        search_query = keywords[0] if keywords else "artificial intelligence"
        
        self.logger.info(f"Fetching OpenAlex papers from {year_filter} onwards")
        self.logger.info(f"Using keyword: '{search_query}' (optimized for rate limits)")
        
        papers = self.search(
            query=search_query,
            max_results=100,
            year_filter=year_filter
        )
        
        # Filter to ensure we have minimum data quality
        quality_papers = [
            p for p in papers 
            if p.get('abstract') and p['abstract'] != 'No abstract available'
            and p.get('citation_count', 0) > 0  # At least 1 citation
        ]
        
        self.logger.info(f"Total quality papers from OpenAlex: {len(quality_papers)}")
        
        return quality_papers
