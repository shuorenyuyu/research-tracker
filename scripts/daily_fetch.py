"""Main script for daily paper fetching"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config.settings import Settings
from src.utils.logger import setup_logger
from src.scrapers.scholar_scraper import ScholarScraper
from src.scrapers.arxiv_scraper import ArxivScraper
from src.database.models import init_database, get_session, Paper
from src.database.repository import PaperRepository


def main():
    """Main function to fetch papers daily"""
    
    # Set up logger
    logger = setup_logger("daily_fetch")
    logger.info("=" * 60)
    logger.info("Starting daily paper fetch")
    logger.info("=" * 60)
    
    # Initialize database
    logger.info(f"Initializing database: {Settings.DATABASE_URL}")
    engine = init_database(Settings.DATABASE_URL)
    session = get_session(engine)
    repo = PaperRepository(session)
    
    # Initialize scrapers
    logger.info("Initializing scrapers...")
    scholar_scraper = ScholarScraper(logger, rate_limit_delay=Settings.RATE_LIMIT_DELAY)
    arxiv_scraper = ArxivScraper(logger, rate_limit_delay=Settings.RATE_LIMIT_DELAY)
    
    # Fetch papers from Google Scholar
    logger.info(f"Fetching papers from Google Scholar for keywords: {Settings.KEYWORDS}")
    scholar_papers = scholar_scraper.get_recent_papers(Settings.KEYWORDS, days=1)
    
    # Fetch papers from arXiv (if enabled)
    arxiv_papers = []
    if Settings.ARXIV_ENABLED:
        logger.info(f"Fetching papers from arXiv for keywords: {Settings.KEYWORDS}")
        arxiv_papers = arxiv_scraper.get_recent_papers(Settings.KEYWORDS, days=1)
    
    # Combine all papers
    all_papers = scholar_papers + arxiv_papers
    logger.info(f"Total papers fetched: {len(all_papers)}")
    
    # Save to database
    new_papers_count = 0
    duplicate_count = 0
    
    for paper_data in all_papers:
        try:
            # Check if paper already exists
            if repo.exists(paper_data['paper_id']):
                duplicate_count += 1
                logger.debug(f"Duplicate paper skipped: {paper_data['title'][:50]}...")
                continue
            
            # Create Paper object
            paper = Paper(**paper_data)
            repo.add_paper(paper)
            new_papers_count += 1
            logger.info(f"Added new paper: {paper.title[:60]}...")
            
        except Exception as e:
            logger.error(f"Error saving paper: {e}")
            continue
    
    # Summary
    logger.info("=" * 60)
    logger.info("Daily fetch completed")
    logger.info(f"Total papers fetched: {len(all_papers)}")
    logger.info(f"New papers added: {new_papers_count}")
    logger.info(f"Duplicates skipped: {duplicate_count}")
    logger.info("=" * 60)
    
    session.close()


if __name__ == "__main__":
    main()
