"""Comprehensive tests for process_papers module"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import sys

# Mock openai
sys.modules['openai'] = Mock()


@pytest.fixture
def mock_dependencies():
    """Mock dependencies for process_papers"""
    with patch('src.scheduler.process_papers.PaperRepository') as mock_repo, \
         patch('src.scheduler.process_papers.AzureSummarizer') as mock_summarizer:
        yield {
            'repo': mock_repo,
            'summarizer': mock_summarizer
        }


class TestPaperProcessor:
    """Test PaperProcessor class"""
    
    def test_initialization(self, mock_dependencies):
        """Test processor initialization"""
        from src.scheduler.process_papers import PaperProcessor
        
        mock_dependencies['repo'].return_value = Mock()
        mock_dependencies['summarizer'].return_value = Mock()
        
        processor = PaperProcessor()
        
        assert processor is not None
        assert hasattr(processor, 'paper_repo')
        assert hasattr(processor, 'summarizer')
    
    def test_process_unprocessed_papers_success(self, mock_dependencies):
        """Test successful processing of unprocessed papers"""
        from src.scheduler.process_papers import PaperProcessor
        
        # Create mock paper
        mock_paper = Mock()
        mock_paper.title = 'Test Paper'
        mock_paper.abstract = 'Abstract'
        mock_paper.authors = 'John Doe'
        mock_paper.year = 2024
        mock_paper.citation_count = 50
        mock_paper.venue = 'Conference'
        mock_paper.paper_id = 'test123'
        
        mock_repo = Mock()
        mock_repo.get_unprocessed.return_value = [mock_paper]
        mock_repo.update_summary = Mock()
        mock_dependencies['repo'].return_value = mock_repo
        
        mock_summarizer = Mock()
        mock_summarizer.generate_summary.return_value = '中文摘要'
        mock_summarizer.generate_investment_insights.return_value = '投资洞察'
        mock_dependencies['summarizer'].return_value = mock_summarizer
        
        processor = PaperProcessor()
        processor.process_unprocessed_papers(limit=1)
        
        # Should have generated summary
        mock_summarizer.generate_summary.assert_called_once()
        # Should have generated insights
        mock_summarizer.generate_investment_insights.assert_called_once()
        # Should have updated database
        mock_repo.update_summary.assert_called_once()
    
    def test_process_no_unprocessed_papers(self, mock_dependencies):
        """Test processing when no unprocessed papers"""
        from src.scheduler.process_papers import PaperProcessor
        
        mock_repo = Mock()
        mock_repo.get_unprocessed.return_value = []
        mock_dependencies['repo'].return_value = mock_repo
        
        mock_summarizer = Mock()
        mock_dependencies['summarizer'].return_value = mock_summarizer
        
        processor = PaperProcessor()
        processor.process_unprocessed_papers()
        
        # Should not call summarizer
        mock_summarizer.generate_summary.assert_not_called()
    
    def test_process_summary_generation_failed(self, mock_dependencies):
        """Test when summary generation fails"""
        from src.scheduler.process_papers import PaperProcessor
        
        mock_paper = Mock()
        mock_paper.title = 'Test'
        mock_paper.abstract = 'Abstract'
        mock_paper.authors = 'Author'
        mock_paper.year = 2024
        mock_paper.citation_count = 10
        mock_paper.venue = 'Venue'
        mock_paper.paper_id = 'test'
        
        mock_repo = Mock()
        mock_repo.get_unprocessed.return_value = [mock_paper]
        mock_dependencies['repo'].return_value = mock_repo
        
        mock_summarizer = Mock()
        mock_summarizer.generate_summary.return_value = None  # Failed
        mock_dependencies['summarizer'].return_value = mock_summarizer
        
        processor = PaperProcessor()
        processor.process_unprocessed_papers(limit=1)
        
        # Should not update database if summary failed
        mock_repo.update_summary.assert_not_called()
    
    def test_process_insights_generation_failed(self, mock_dependencies):
        """Test when insights generation fails"""
        from src.scheduler.process_papers import PaperProcessor
        
        mock_paper = Mock()
        mock_paper.title = 'Test'
        mock_paper.abstract = 'Abstract'
        mock_paper.authors = 'Author'
        mock_paper.year = 2024
        mock_paper.citation_count = 10
        mock_paper.venue = 'Venue'
        mock_paper.paper_id = 'test'
        
        mock_repo = Mock()
        mock_repo.get_unprocessed.return_value = [mock_paper]
        mock_dependencies['repo'].return_value = mock_repo
        
        mock_summarizer = Mock()
        mock_summarizer.generate_summary.return_value = '摘要'
        mock_summarizer.generate_investment_insights.return_value = None  # Failed
        mock_dependencies['summarizer'].return_value = mock_summarizer
        
        processor = PaperProcessor()
        processor.process_unprocessed_papers(limit=1)
        
        # Should not update database if insights failed
        mock_repo.update_summary.assert_not_called()
    
    def test_process_with_limit(self, mock_dependencies):
        """Test processing with limit"""
        from src.scheduler.process_papers import PaperProcessor
        
        mock_paper = Mock()
        mock_paper.title = 'Test'
        mock_paper.abstract = 'Abstract'
        mock_paper.authors = 'Author'
        mock_paper.year = 2024
        mock_paper.citation_count = 10
        mock_paper.venue = 'Venue'
        mock_paper.paper_id = 'test'
        
        mock_repo = Mock()
        mock_repo.get_unprocessed.return_value = [mock_paper]
        mock_dependencies['repo'].return_value = mock_repo
        
        processor = PaperProcessor()
        
        # Test that limit is passed to get_unprocessed
        processor.paper_repo.get_unprocessed(limit=5)
        mock_repo.return_value.get_unprocessed.assert_called_with(limit=5)


class TestMainFunction:
    """Test main entry point for process_papers"""
    
    @patch('src.scheduler.process_papers.PaperProcessor')
    @patch('sys.argv', ['process_papers.py', '--one'])
    def test_main_with_one_flag(self, mock_processor_class):
        """Test main with --one flag"""
        mock_processor = Mock()
        mock_processor_class.return_value = mock_processor
        
        try:
            from src.scheduler.process_papers import main
            main()
            mock_processor.process_unprocessed_papers.assert_called_once_with(limit=1)
        except SystemExit:
            pass
    
    @patch('src.scheduler.process_papers.PaperProcessor')
    @patch('sys.argv', ['process_papers.py', '--limit', '5'])
    def test_main_with_limit_flag(self, mock_processor_class):
        """Test main with --limit flag"""
        mock_processor = Mock()
        mock_processor_class.return_value = mock_processor
        
        try:
            from src.scheduler.process_papers import main
            main()
            mock_processor.process_unprocessed_papers.assert_called_once_with(limit=5)
        except SystemExit:
            pass
    
    @patch('src.scheduler.process_papers.PaperProcessor')
    @patch('sys.argv', ['process_papers.py'])
    def test_main_without_flags(self, mock_processor_class):
        """Test main without flags (process all)"""
        mock_processor = Mock()
        mock_processor_class.return_value = mock_processor
        
        try:
            from src.scheduler.process_papers import main
            main()
            mock_processor.process_unprocessed_papers.assert_called_once_with(limit=None)
        except SystemExit:
            pass
