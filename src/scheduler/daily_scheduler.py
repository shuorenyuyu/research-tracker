"""Scheduler for automated daily paper fetching and processing"""

import sys
from pathlib import Path
from datetime import datetime, time
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.utils.logger import setup_logger
from src.scrapers.arxiv_scraper import ArxivScraper
from src.scrapers.semantic_scholar_scraper import SemanticScholarScraper
from src.database.models import init_database
from src.database.repository import PaperRepository
from src.config.settings import Settings


class DailyPaperScheduler:
    """Scheduler for daily paper fetching and processing"""
    
    def __init__(self):
        self.logger = setup_logger("scheduler")
        self.settings = Settings()
        self.scheduler = BlockingScheduler()
        
        # Initialize database
        init_database(self.settings.database_url)
        self.paper_repo = PaperRepository()
        
        # Initialize scrapers with API key if available
        self.arxiv_scraper = ArxivScraper(self.logger, rate_limit_delay=1)
        ss_api_key = self.settings.SEMANTIC_SCHOLAR_API_KEY or None
        self.ss_scraper = SemanticScholarScraper(
            self.logger, 
            rate_limit_delay=3,
            api_key=ss_api_key
        )
        if ss_api_key:
            self.logger.info("Semantic Scholar API key configured - using higher rate limits")
        else:
            self.logger.warning("No Semantic Scholar API key - using free tier (rate limited)")
    
    def fetch_and_store_papers(self):
        """Fetch one high-impact paper per day for summarization"""
        try:
            self.logger.info("="*80)
            self.logger.info(f"STARTING DAILY PAPER FETCH - {datetime.now()}")
            self.logger.info("="*80)
            
            # Strategy: Fetch citation-validated papers from Semantic Scholar
            # Pick ONE paper per day that we haven't processed yet
            self.logger.info("[1/3] Fetching citation-validated papers from Semantic Scholar...")
            papers = self.ss_scraper.get_recent_papers(
                keywords=self.settings.keywords,
                days=180  # Papers from 2025 (current year)
            )
            
            # Filter to top 100 by citations
            papers = papers[:100]
            self.logger.info(f"Retrieved {len(papers)} papers (sorted by citations)")
            
            # Step 2: Check which papers we already have in database (deduplication)
            self.logger.info("[2/3] Checking for duplicates...")
            new_papers_to_add = []
            
            for paper in papers:
                paper_id = paper.get('paper_id') or paper.get('semantic_scholar_id')
                if paper_id:
                    # Check if we already have this paper
                    exists = self.paper_repo.get_by_paper_id(paper_id, paper.get('source'))
                    if not exists:
                        new_papers_to_add.append(paper)
            
            self.logger.info(f"Found {len(new_papers_to_add)} new papers not in database")
            
            # Step 3: Add only ONE new paper per day (highest citations)
            self.logger.info("[3/3] Adding today's paper to database...")
            
            if not new_papers_to_add:
                self.logger.info("No new papers found - all top papers already in database")
                return 0, 0
            
            # Take the first (highest citation) new paper
            today_paper = new_papers_to_add[0]
            
            try:
                self.paper_repo.add_paper(today_paper)
                self.logger.info(f"Added: {today_paper['title']}")
                self.logger.info(f"Citations: {today_paper.get('citation_count', 0)}")
                new_papers = 1
            except Exception as e:
                self.logger.error(f"Error storing paper: {e}")
                new_papers = 0
            
            # Summary
            self.logger.info("="*80)
            self.logger.info("DAILY FETCH COMPLETE")
            self.logger.info(f"Today's paper added: {new_papers}")
            self.logger.info(f"Total papers in database: {self.paper_repo.count_all()}")
            self.logger.info(f"Unprocessed papers (waiting for summary): {self.paper_repo.count_unprocessed()}")
            self.logger.info("="*80)
            
            return new_papers, 0
            
        except Exception as e:
            self.logger.error(f"Error in daily fetch: {e}", exc_info=True)
            raise
    
    def start(self, schedule_time: str = "00:00", timezone: str = "UTC"):
        """
        Start the scheduler
        
        Args:
            schedule_time: Time to run daily fetch (HH:MM format)
            timezone: Timezone for scheduling (default: UTC)
        """
        try:
            # Parse schedule time
            hour, minute = map(int, schedule_time.split(':'))
            
            # Add scheduled job
            self.scheduler.add_job(
                self.fetch_and_store_papers,
                trigger=CronTrigger(hour=hour, minute=minute, timezone=timezone),
                id='daily_paper_fetch',
                name='Daily Paper Fetch and Store',
                misfire_grace_time=3600  # Allow 1 hour grace time
            )
            
            self.logger.info(f"Scheduler started. Daily fetch scheduled at {schedule_time} {timezone}")
            self.logger.info("Press Ctrl+C to exit")
            
            # Run once immediately on startup (optional)
            self.logger.info("Running initial fetch now...")
            self.fetch_and_store_papers()
            
            # Start scheduler (blocks)
            self.scheduler.start()
            
        except (KeyboardInterrupt, SystemExit):
            self.logger.info("Scheduler stopped by user")
            self.scheduler.shutdown()
        except Exception as e:
            self.logger.error(f"Scheduler error: {e}", exc_info=True)
            raise


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Daily paper fetching scheduler')
    parser.add_argument(
        '--time',
        default='00:00',
        help='Daily fetch time in HH:MM format (default: 00:00)'
    )
    parser.add_argument(
        '--timezone',
        default='UTC',
        help='Timezone for scheduling (default: UTC)'
    )
    parser.add_argument(
        '--run-once',
        action='store_true',
        help='Run once and exit (no scheduling)'
    )
    
    args = parser.parse_args()
    
    scheduler = DailyPaperScheduler()
    
    if args.run_once:
        scheduler.logger.info("Running one-time fetch (no scheduling)")
        scheduler.fetch_and_store_papers()
    else:
        scheduler.start(schedule_time=args.time, timezone=args.timezone)


if __name__ == "__main__":
    main()
