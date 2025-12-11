"""Semantic Scholar scraper for citation data enrichment"""

import time
import requests
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from .base_scraper import BaseScraper


class SemanticScholarScraper(BaseScraper):
    """Scraper for Semantic Scholar API to get citation data"""
    
    BASE_URL = "https://api.semanticscholar.org/graph/v1"
    
    def __init__(self, logger, rate_limit_delay: int = 1, api_key: Optional[str] = None):
        """
        Initialize Semantic Scholar scraper
        
        Args:
            logger: Logger instance
            rate_limit_delay: Delay between requests (free tier: 100 req/5min)
            api_key: Optional API key for higher rate limits
        """
        super().__init__(logger)
        self.rate_limit_delay = rate_limit_delay
        self.api_key = api_key
        self.headers = {
            'User-Agent': 'ResearchTracker/1.0 (mailto:research@example.com)'
        }
        if api_key:
            self.headers['x-api-key'] = api_key
    
    def search(self, query: str, max_results: int = 100, 
               year_filter: Optional[str] = None,
               fields_of_study: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Search Semantic Scholar for papers
        
        Args:
            query: Search query
            max_results: Maximum number of results (max 100 per request)
            year_filter: Year filter like "2024-" or "2023-2024"
            fields_of_study: List of fields like ["Computer Science", "Engineering"]
            
        Returns:
            List of normalized papers
        """
        papers = []
        
        try:
            self.logger.info(f"Searching Semantic Scholar for: '{query}'")
            
            # Build query parameters
            params = {
                'query': query,
                'limit': min(max_results, 100),
                'fields': 'paperId,externalIds,title,abstract,venue,year,authors,citationCount,publicationDate,url,openAccessPdf'
            }
            
            if year_filter:
                params['year'] = year_filter
            
            if fields_of_study:
                params['fieldsOfStudy'] = ','.join(fields_of_study)
            
            url = f"{self.BASE_URL}/paper/search"
            response = requests.get(url, params=params, headers=self.headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                for item in data.get('data', []):
                    try:
                        paper = self._normalize_paper(item)
                        papers.append(paper)
                    except Exception as e:
                        self.logger.warning(f"Error processing Semantic Scholar paper: {e}")
                        continue
                
                self.logger.info(f"Found {len(papers)} papers from Semantic Scholar")
            else:
                self.logger.error(f"Semantic Scholar API error: {response.status_code} - {response.text}")
            
            time.sleep(self.rate_limit_delay)
            
        except Exception as e:
            self.logger.error(f"Error searching Semantic Scholar: {e}")
        
        return papers
    
    def get_paper_by_arxiv_id(self, arxiv_id: str) -> Optional[Dict[str, Any]]:
        """
        Get paper details by arXiv ID to enrich with citation data
        
        Args:
            arxiv_id: arXiv ID (e.g., "2512.05117v1" or "2512.05117")
            
        Returns:
            Paper dict with citation data or None
        """
        try:
            # Clean arXiv ID (remove version if present)
            clean_id = arxiv_id.split('v')[0] if 'v' in arxiv_id else arxiv_id
            
            url = f"{self.BASE_URL}/paper/arXiv:{clean_id}"
            params = {
                'fields': 'paperId,externalIds,title,abstract,venue,year,authors,citationCount,publicationDate,url,openAccessPdf,influentialCitationCount'
            }
            
            response = requests.get(url, params=params, headers=self.headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                return self._normalize_paper(data)
            elif response.status_code == 404:
                self.logger.debug(f"Paper not found in Semantic Scholar: arXiv:{clean_id}")
                return None
            else:
                self.logger.warning(f"Semantic Scholar API error for {arxiv_id}: {response.status_code}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error fetching paper {arxiv_id} from Semantic Scholar: {e}")
            return None
    
    def enrich_papers_with_citations(self, papers: List[Dict[str, Any]], 
                                     max_papers: int = 50) -> List[Dict[str, Any]]:
        """
        Enrich papers with citation data from Semantic Scholar
        Uses rate limiting (3 seconds) to stay within free tier limits (100 req/5min)
        
        Args:
            papers: List of papers (must have 'paper_id' field with arXiv ID)
            max_papers: Maximum papers to enrich (to avoid hitting rate limits)
            
        Returns:
            List of papers enriched with citation counts
        """
        enriched_papers = []
        request_count = 0
        
        # Limit papers to enrich
        papers_to_enrich = papers[:max_papers]
        
        for i, paper in enumerate(papers_to_enrich, 1):
            try:
                arxiv_id = paper.get('paper_id')
                if not arxiv_id:
                    enriched_papers.append(paper)
                    continue
                
                # Get citation data from Semantic Scholar with retry
                ss_data = self._get_with_retry(arxiv_id)
                
                if ss_data:
                    # Update citation count
                    paper['citation_count'] = ss_data.get('citation_count', 0)
                    paper['influential_citation_count'] = ss_data.get('influential_citation_count', 0)
                    paper['semantic_scholar_id'] = ss_data.get('semantic_scholar_id')
                    self.logger.info(f"[{i}/{len(papers_to_enrich)}] Enriched '{paper['title'][:50]}...' with {paper['citation_count']} citations")
                else:
                    self.logger.debug(f"[{i}/{len(papers_to_enrich)}] Paper not found in Semantic Scholar: {paper['title'][:50]}...")
                
                enriched_papers.append(paper)
                request_count += 1
                
                # Rate limiting: 3 seconds between requests (max 20 req/min)
                # This ensures we stay well under the 100 req/5min limit
                time.sleep(3)
                
            except Exception as e:
                self.logger.warning(f"Error enriching paper: {e}")
                enriched_papers.append(paper)
                continue
        
        # Add remaining papers without enrichment
        if len(papers) > max_papers:
            enriched_papers.extend(papers[max_papers:])
            self.logger.info(f"Skipped enrichment for {len(papers) - max_papers} papers to avoid rate limits")
        
        self.logger.info(f"Enriched {request_count} papers with citation data")
        return enriched_papers
    
    def _get_with_retry(self, arxiv_id: str, max_retries: int = 3) -> Optional[Dict[str, Any]]:
        """
        Get paper with exponential backoff retry on rate limit
        
        Args:
            arxiv_id: arXiv ID
            max_retries: Maximum retry attempts
            
        Returns:
            Paper dict or None
        """
        for attempt in range(max_retries):
            try:
                paper = self.get_paper_by_arxiv_id(arxiv_id)
                return paper
            except Exception as e:
                if attempt < max_retries - 1:
                    wait_time = (2 ** attempt) * 5  # 5, 10, 20 seconds
                    self.logger.debug(f"Retry {attempt + 1}/{max_retries} for {arxiv_id} after {wait_time}s")
                    time.sleep(wait_time)
                else:
                    self.logger.warning(f"Failed to get {arxiv_id} after {max_retries} attempts")
                    return None
        return None
    
    def get_recent_papers(self, keywords: List[str], days: int = 30) -> List[Dict[str, Any]]:
        """
        Get recent papers from Semantic Scholar
        
        Args:
            keywords: List of keywords to search
            days: Look back this many days (parameter kept for compatibility but year range used instead)
            
        Returns:
            List of papers sorted by citation count
        """
        all_papers = []
        current_year = datetime.now().year
        
        # Fields of study for AI/Robotics
        fields = ["Computer Science", "Engineering"]
        
        # Use 1-year window to get papers with citations
        year_filter = f"{current_year - 1}-"
        
        self.logger.info(f"Fetching papers from {current_year - 1} onwards (to ensure citation data)")
        
        # OPTIMIZATION: Use only the FIRST keyword to reduce API calls and avoid rate limiting (429 errors)
        # Semantic Scholar search is broad enough that one keyword returns diverse results
        primary_keyword = keywords[0] if keywords else "artificial intelligence"
        
        try:
            self.logger.info(f"Fetching Semantic Scholar papers for: '{primary_keyword}' (optimized for rate limits)")
            
            # Single search to avoid rate limiting
            papers = self.search(
                query=primary_keyword,
                max_results=100,
                year_filter=year_filter,
                fields_of_study=fields
            )
            
            all_papers.extend(papers)
            
        except Exception as e:
            self.logger.error(f"Error fetching Semantic Scholar papers for '{primary_keyword}': {e}")
            # Don't try other keywords to avoid more rate limiting
            return []
        
        # Remove duplicates by paper_id
        unique_papers = []
        seen_ids = set()
        
        for paper in all_papers:
            paper_id = paper.get('paper_id') or paper.get('semantic_scholar_id')
            if paper_id and paper_id not in seen_ids:
                seen_ids.add(paper_id)
                unique_papers.append(paper)
        
        # Sort by citation count (descending)
        unique_papers.sort(key=lambda x: x.get('citation_count', 0), reverse=True)
        
        self.logger.info(f"Total unique Semantic Scholar papers found: {len(unique_papers)}")
        return unique_papers
    
    def _normalize_paper(self, raw_paper: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize Semantic Scholar paper to standard format
        
        Args:
            raw_paper: Semantic Scholar API response
            
        Returns:
            Normalized paper dictionary
        """
        # Extract authors
        authors_list = raw_paper.get('authors', [])
        authors = ', '.join([a.get('name', '') for a in authors_list if a.get('name')])
        first_author = authors_list[0].get('name', '') if authors_list else ''
        
        # Get arXiv ID from external IDs
        external_ids = raw_paper.get('externalIds', {})
        arxiv_id = external_ids.get('ArXiv', '')
        doi = external_ids.get('DOI', '')
        
        # Get paper ID (prefer arXiv, fallback to Semantic Scholar ID)
        paper_id = arxiv_id or raw_paper.get('paperId', '')
        
        # Get URL (prefer arXiv)
        url = f"https://arxiv.org/abs/{arxiv_id}" if arxiv_id else raw_paper.get('url', '')
        
        # Get PDF URL
        pdf_url = ''
        if arxiv_id:
            pdf_url = f"https://arxiv.org/pdf/{arxiv_id}"
        elif raw_paper.get('openAccessPdf'):
            pdf_url = raw_paper['openAccessPdf'].get('url', '')
        
        # Parse publication date
        pub_date = raw_paper.get('publicationDate')
        if pub_date:
            try:
                pub_date = datetime.fromisoformat(pub_date.replace('Z', '+00:00'))
            except:
                pub_date = None
        
        return {
            "title": raw_paper.get('title', ''),
            "paper_id": paper_id,
            "semantic_scholar_id": raw_paper.get('paperId', ''),
            "source": "arxiv" if arxiv_id else "semantic_scholar",
            "authors": authors,
            "first_author": first_author,
            "year": raw_paper.get('year'),
            "publication_date": pub_date,
            "venue": raw_paper.get('venue', ''),
            "publisher": "arXiv" if arxiv_id else raw_paper.get('venue', ''),
            "abstract": raw_paper.get('abstract', ''),
            "url": url,
            "pdf_url": pdf_url,
            "citation_count": raw_paper.get('citationCount', 0),
            "influential_citation_count": raw_paper.get('influentialCitationCount', 0),
            "doi": doi,
            "fetched_at": datetime.utcnow()
        }
