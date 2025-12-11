"""Test script to verify OpenAlex scraper works"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.logger import setup_logger
from src.scrapers.openalex_scraper import OpenAlexScraper


def main():
    """Test OpenAlex scraper"""
    logger = setup_logger("test_openalex")
    
    print("=" * 80)
    print("Testing OpenAlex Scraper (Free, No API Key Required)")
    print("=" * 80)
    
    # Initialize scraper
    scraper = OpenAlexScraper(logger, rate_limit_delay=1)
    
    # Test search
    print("\n[TEST 1] Searching for 'artificial intelligence' papers from 2024+")
    papers = scraper.search(
        query="artificial intelligence",
        max_results=10,
        year_filter="2024-"
    )
    
    print(f"\nFound {len(papers)} papers")
    
    if papers:
        print("\nTop 3 papers:")
        for i, paper in enumerate(papers[:3], 1):
            print(f"\n{i}. {paper['title']}")
            print(f"   Source: {paper['source']}")
            print(f"   Citations: {paper['citation_count']}")
            print(f"   Year: {paper['year']}")
            print(f"   Authors: {paper['authors'][:100]}...")
            print(f"   Abstract: {paper['abstract'][:150]}...")
    
    # Test get_recent_papers
    print("\n" + "=" * 80)
    print("[TEST 2] Getting recent high-impact papers")
    recent = scraper.get_recent_papers(
        keywords=["machine learning", "deep learning"],
        days=180
    )
    
    print(f"\nFound {len(recent)} quality papers (with abstracts and citations)")
    
    if recent:
        top_paper = recent[0]
        print(f"\nHighest cited paper:")
        print(f"Title: {top_paper['title']}")
        print(f"Citations: {top_paper['citation_count']}")
        print(f"URL: {top_paper['url']}")
    
    print("\n" + "=" * 80)
    print("✓ OpenAlex scraper test complete!")
    print("=" * 80)


if __name__ == "__main__":
    main()
