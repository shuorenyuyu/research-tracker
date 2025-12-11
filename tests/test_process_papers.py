"""Tests for paper processor"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import sys

# Mock openai module
sys.modules['openai'] = Mock()

from src.database.models import Paper
from src.database.repository import PaperRepository


class TestProcessPapers:
    """Test paper processing logic"""
    
    @patch('src.database.repository.PaperRepository')
    @patch('src.processors.azure_summarizer.AzureSummarizer')
    def test_process_unprocessed_papers(self, mock_summarizer, mock_repo):
        """Test processing unprocessed papers"""
        # Create mock unprocessed paper
        mock_paper = Mock(spec=Paper)
        mock_paper.title = 'Test Paper'
        mock_paper.abstract = 'Test abstract'
        mock_paper.authors = 'John Doe'
        mock_paper.year = 2024
        mock_paper.citation_count = 10
        mock_paper.paper_id = 'test123'
        mock_paper.processed = False
        
        mock_repo_instance = Mock()
        mock_repo_instance.get_unprocessed.return_value = [mock_paper]
        mock_repo_instance.update_summary = Mock()
        
        mock_summarizer_instance = Mock()
        mock_summarizer_instance.generate_summary.return_value = '测试摘要'
        mock_summarizer_instance.generate_investment_insights.return_value = '投资洞察'
        
        # Simulate processing
        papers = mock_repo_instance.get_unprocessed(limit=1)
        assert len(papers) == 1
        
        summary = mock_summarizer_instance.generate_summary({})
        assert summary == '测试摘要'
        
        insights = mock_summarizer_instance.generate_investment_insights({}, summary)
        assert insights == '投资洞察'
    
    @patch('src.database.repository.PaperRepository')
    def test_no_unprocessed_papers(self, mock_repo):
        """Test when no unprocessed papers exist"""
        mock_repo_instance = Mock()
        mock_repo_instance.get_unprocessed.return_value = []
        
        papers = mock_repo_instance.get_unprocessed()
        assert len(papers) == 0
    
    @patch('src.database.repository.PaperRepository')
    def test_update_summary(self, mock_repo):
        """Test updating paper with summary"""
        mock_repo_instance = Mock()
        mock_repo_instance.update_summary = Mock()
        
        mock_repo_instance.update_summary(
            'test123',
            summary_zh='中文摘要',
            keywords='AI, ML',
            insights='投资洞察'
        )
        
        mock_repo_instance.update_summary.assert_called_once()
        call_args = mock_repo_instance.update_summary.call_args
        assert call_args[0][0] == 'test123'
        assert call_args[1]['summary_zh'] == '中文摘要'
