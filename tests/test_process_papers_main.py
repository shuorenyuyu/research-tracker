"""Comprehensive tests for process_papers main() function"""
import pytest
from unittest.mock import Mock, patch
import sys

# Mock dependencies
sys.modules['openai'] = Mock()

from src.scheduler.process_papers import PaperProcessor, main


class TestProcessPapersMain:
    """Test main() function and argparse handling"""
    
    @patch('src.scheduler.process_papers.PaperProcessor')
    def test_main_default(self, mock_processor_class):
        """Test main() with default arguments"""
        mock_processor = Mock()
        mock_processor_class.return_value = mock_processor
        
        with patch('sys.argv', ['process_papers.py']):
            try:
                main()
            except SystemExit:
                pass
        
        # Verify processor was called with default limit
        mock_processor.process_unprocessed_papers.assert_called_once_with(limit=1)
    
    @patch('src.scheduler.process_papers.PaperProcessor')
    def test_main_with_limit(self, mock_processor_class):
        """Test main() with --limit argument"""
        mock_processor = Mock()
        mock_processor_class.return_value = mock_processor
        
        with patch('sys.argv', ['process_papers.py', '--limit', '5']):
            try:
                main()
            except SystemExit:
                pass
        
        # Verify processor was called with specified limit
        mock_processor.process_unprocessed_papers.assert_called_once_with(limit=5)
    
    @patch('src.scheduler.process_papers.PaperProcessor')
    def test_main_with_all_flag(self, mock_processor_class):
        """Test main() with --all flag"""
        mock_processor = Mock()
        mock_processor_class.return_value = mock_processor
        
        with patch('sys.argv', ['process_papers.py', '--all']):
            try:
                main()
            except SystemExit:
                pass
        
        # Verify processor was called with None (process all)
        mock_processor.process_unprocessed_papers.assert_called_once_with(limit=None)
    
    @patch('src.scheduler.process_papers.PaperProcessor')
    def test_main_with_exception(self, mock_processor_class):
        """Test main() handling exception"""
        mock_processor = Mock()
        mock_processor.process_unprocessed_papers.side_effect = Exception("Processing error")
        mock_processor_class.return_value = mock_processor
        
        with patch('sys.argv', ['process_papers.py']):
            with pytest.raises(Exception):
                main()
