"""
Process unprocessed papers with Azure OpenAI
Generates Chinese summaries and investment insights
"""
import sys
import logging
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

from src.database.repository import PaperRepository
from src.processors.azure_summarizer import AzureSummarizer
from src.config.settings import Settings

# Set up logging
Settings.LOG_DIR.mkdir(parents=True, exist_ok=True)
log_file = Settings.LOG_DIR / "processor.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class PaperProcessor:
    """Process papers with AI summarization"""
    
    def __init__(self):
        self.paper_repo = PaperRepository()
        self.summarizer = AzureSummarizer()
    
    def process_unprocessed_papers(self, limit: int = None):
        """
        Process all unprocessed papers (or up to limit)
        
        Args:
            limit: Maximum number of papers to process (None = all)
        """
        # Get unprocessed papers
        unprocessed = self.paper_repo.get_unprocessed(limit=limit)
        
        if not unprocessed:
            logger.info("No unprocessed papers found")
            return
        
        logger.info(f"Found {len(unprocessed)} unprocessed paper(s)")
        
        # Process each paper
        for paper in unprocessed:
            logger.info(f"\n{'='*80}")
            logger.info(f"Processing: {paper.title}")
            logger.info(f"Citations: {paper.citation_count}")
            logger.info(f"{'='*80}\n")
            
            # Convert to dict for summarizer
            paper_dict = {
                'title': paper.title,
                'abstract': paper.abstract,
                'authors': paper.authors,
                'year': paper.year,
                'venue': paper.venue,
                'citation_count': paper.citation_count
            }
            
            # Generate Chinese summary
            logger.info("Generating Chinese summary...")
            summary = self.summarizer.generate_summary(paper_dict)
            
            if not summary:
                logger.warning(f"Failed to generate summary for: {paper.title}")
                continue
            
            # Generate investment insights
            logger.info("Generating investment insights...")
            insights = self.summarizer.generate_investment_insights(paper_dict, summary)
            
            if not insights:
                logger.warning(f"Failed to generate insights for: {paper.title}")
                # Still save the summary even if insights failed
            
            # Update paper in database
            paper.summary_zh = summary
            paper.investment_insights = insights
            paper.processed = True
            
            self.paper_repo.session.commit()
            
            logger.info(f"✅ Successfully processed: {paper.title[:50]}...")
            logger.info(f"\n摘要预览:\n{summary[:200]}...\n")
            
            if insights:
                logger.info(f"投资洞察预览:\n{insights[:200]}...\n")
        
        logger.info(f"\n{'='*80}")
        logger.info(f"Processing complete: {len(unprocessed)} paper(s) processed")
        logger.info(f"{'='*80}\n")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Process papers with Azure OpenAI')
    parser.add_argument(
        '--limit',
        type=int,
        default=None,
        help='Maximum number of papers to process (default: all unprocessed)'
    )
    parser.add_argument(
        '--one',
        action='store_true',
        help='Process only one paper (same as --limit 1)'
    )
    
    args = parser.parse_args()
    
    limit = 1 if args.one else args.limit
    
    try:
        processor = PaperProcessor()
        processor.process_unprocessed_papers(limit=limit)
    except Exception as e:
        logger.error(f"Processing failed: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
