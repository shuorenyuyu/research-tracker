"""Test script for the scrapers"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.logger import setup_logger
from src.scrapers.scholar_scraper import ScholarScraper
from src.scrapers.arxiv_scraper import ArxivScraper


def test_scholar():
    """Test Google Scholar scraper"""
    logger = setup_logger("test_scholar")
    logger.info("Testing Google Scholar scraper...")
    
    scraper = ScholarScraper(logger, rate_limit_delay=2)
    
    # Test search
    papers = scraper.search("large language models", max_results=5)
    
    logger.info(f"\nFound {len(papers)} papers:")
    for i, paper in enumerate(papers, 1):
        logger.info(f"\n{i}. {paper['title']}")
        logger.info(f"   Authors: {paper['authors'][:100]}...")
        logger.info(f"   Year: {paper['year']}")
        logger.info(f"   Citations: {paper['citation_count']}")
        logger.info(f"   URL: {paper['url']}")


def test_arxiv():
    """Test arXiv scraper"""
    logger = setup_logger("test_arxiv")
    logger.info("Testing arXiv scraper...")
    
    scraper = ArxivScraper(logger, rate_limit_delay=1)
    
    # Test search
    papers = scraper.search("large language models", max_results=5)
    
    logger.info(f"\nFound {len(papers)} papers:")
    for i, paper in enumerate(papers, 1):
        logger.info(f"\n{i}. {paper['title']}")
        logger.info(f"   Authors: {paper['authors'][:100]}...")
        logger.info(f"   Date: {paper['publication_date']}")
        logger.info(f"   Category: {paper['venue']}")
        logger.info(f"   URL: {paper['url']}")


def test_recent_papers():
    """Test fetching recent papers"""
    logger = setup_logger("test_recent")
    logger.info("Testing recent papers fetch...")
    
    keywords = ["artificial intelligence", "robotics"]
    
    # Test Scholar
    logger.info("\n--- Google Scholar ---")
    scholar = ScholarScraper(logger, rate_limit_delay=2)
    scholar_papers = scholar.get_recent_papers(keywords, days=7)
    logger.info(f"Found {len(scholar_papers)} recent papers from Scholar")
    
    # Test arXiv
    logger.info("\n--- arXiv ---")
    arxiv = ArxivScraper(logger, rate_limit_delay=1)
    arxiv_papers = arxiv.get_recent_papers(keywords, days=7)
    logger.info(f"Found {len(arxiv_papers)} recent papers from arXiv")
    
    # Show some examples
    all_papers = scholar_papers[:3] + arxiv_papers[:3]
    logger.info(f"\nSample papers:")
    for i, paper in enumerate(all_papers, 1):
        logger.info(f"\n{i}. [{paper['source'].upper()}] {paper['title'][:80]}...")
        logger.info(f"   Year: {paper['year']}, Citations: {paper['citation_count']}")


if __name__ == "__main__":
    print("Choose test:")
    print("1. Test Google Scholar")
    print("2. Test arXiv")
    print("3. Test recent papers (both sources)")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == "1":
        test_scholar()
    elif choice == "2":
        test_arxiv()
    elif choice == "3":
        test_recent_papers()
    else:
        print("Invalid choice")
