"""Display detailed information about fetched papers"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.logger import setup_logger
from src.scrapers.arxiv_scraper import ArxivScraper


def main():
    logger = setup_logger("paper_details")
    
    logger.info("Fetching papers for detailed review...")
    
    # Initialize arXiv scraper
    scraper = ArxivScraper(logger, rate_limit_delay=1)
    
    # Fetch recent papers (last 3 days)
    keywords = ["artificial intelligence"]
    papers = scraper.get_recent_papers(keywords, days=3)[:10]
    
    print("\n" + "="*100)
    print(f"FETCHED {len(papers)} RECENT AI PAPERS")
    print("="*100 + "\n")
    
    for i, paper in enumerate(papers, 1):
        print(f"\n{'─'*100}")
        print(f"PAPER #{i}")
        print(f"{'─'*100}\n")
        
        print(f"📄 Title: {paper['title']}")
        print(f"\n👥 Authors: {paper['authors']}")
        print(f"\n📅 Publication Date: {paper['publication_date']}")
        print(f"📚 Category: {paper['venue']}")
        print(f"🆔 Paper ID: {paper['paper_id']}")
        print(f"🔗 URL: {paper['url']}")
        print(f"📥 PDF: {paper['pdf_url']}")
        print(f"📊 Citations: {paper['citation_count']}")
        
        print(f"\n📝 Abstract:")
        print("─" * 100)
        # Format abstract for better readability
        abstract = paper['abstract'].replace('\n', ' ').strip()
        # Wrap text at 100 characters
        words = abstract.split()
        line = ""
        for word in words:
            if len(line) + len(word) + 1 <= 95:
                line += word + " "
            else:
                print(line)
                line = word + " "
        if line:
            print(line)
        
        print("\n")
    
    print("="*100)
    print(f"Total: {len(papers)} papers")
    print("="*100)
    
    # Save to JSON for reference
    import json
    output_file = Path(__file__).parent.parent / "data" / "latest_papers.json"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(papers, f, indent=2, default=str, ensure_ascii=False)
    
    print(f"\n✅ Papers saved to: {output_file}")


if __name__ == "__main__":
    main()
