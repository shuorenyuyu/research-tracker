"""Tests for Azure OpenAI summarizer"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import sys

# Mock the openai module before importing
sys.modules['openai'] = Mock()

from src.processors.azure_summarizer import AzureSummarizer


class TestAzureSummarizer:
    """Test AzureSummarizer class"""
    
    @pytest.fixture
    def mock_env(self, monkeypatch):
        """Mock environment variables"""
        monkeypatch.setenv('AZURE_OPENAI_ENDPOINT', 'https://test.openai.azure.com/')
        monkeypatch.setenv('AZURE_OPENAI_API_KEY', 'test_key_12345')
        monkeypatch.setenv('AZURE_OPENAI_DEPLOYMENT_NAME', 'gpt-4')
        monkeypatch.setenv('AZURE_OPENAI_API_VERSION', '2024-02-15-preview')
    
    @pytest.fixture
    def sample_paper(self):
        """Sample paper data"""
        return {
            'title': 'Test Paper on Machine Learning',
            'abstract': 'This paper presents a novel approach to ML',
            'authors': 'John Doe, Jane Smith',
            'year': 2024,
            'venue': 'NeurIPS',
            'citation_count': 42
        }
    
    def test_initialization_without_credentials(self, monkeypatch):
        """Test initialization fails without credentials"""
        monkeypatch.delenv('AZURE_OPENAI_ENDPOINT', raising=False)
        monkeypatch.delenv('AZURE_OPENAI_API_KEY', raising=False)
        
        with pytest.raises(ValueError, match="Azure OpenAI credentials"):
            AzureSummarizer()
    
    @patch('src.processors.azure_summarizer.AzureOpenAI')
    def test_initialization_success(self, mock_client, mock_env):
        """Test successful initialization"""
        summarizer = AzureSummarizer()
        
        assert summarizer.endpoint == 'https://test.openai.azure.com/'
        assert summarizer.api_key == 'test_key_12345'
        assert summarizer.deployment == 'gpt-4'
        mock_client.assert_called_once()
    
    @patch('src.processors.azure_summarizer.AzureOpenAI')
    def test_generate_summary_success(self, mock_client, mock_env, sample_paper):
        """Test successful summary generation"""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '测试摘要内容'
        
        mock_instance = Mock()
        mock_instance.chat.completions.create.return_value = mock_response
        mock_client.return_value = mock_instance
        
        summarizer = AzureSummarizer()
        summary = summarizer.generate_summary(sample_paper)
        
        assert summary == '测试摘要内容'
        mock_instance.chat.completions.create.assert_called_once()
    
    @patch('src.processors.azure_summarizer.AzureOpenAI')
    def test_generate_summary_with_all_fields(self, mock_client, mock_env):
        """Test summary generation uses all paper fields"""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '完整摘要'
        
        mock_instance = Mock()
        mock_instance.chat.completions.create.return_value = mock_response
        mock_client.return_value = mock_instance
        
        paper = {
            'title': 'Complete Paper',
            'abstract': 'Full abstract',
            'authors': 'Multiple Authors',
            'year': 2024,
            'venue': 'Top Conference',
            'citation_count': 100
        }
        
        summarizer = AzureSummarizer()
        summary = summarizer.generate_summary(paper)
        
        # Check that prompt includes all fields
        call_args = mock_instance.chat.completions.create.call_args
        messages = call_args[1]['messages']
        user_message = messages[1]['content']
        
        assert 'Complete Paper' in user_message
        assert 'Full abstract' in user_message
        assert '2024' in user_message
        assert '100' in user_message
    
    @patch('src.processors.azure_summarizer.AzureOpenAI')
    def test_generate_summary_error_handling(self, mock_client, mock_env, sample_paper):
        """Test summary generation error handling"""
        mock_instance = Mock()
        mock_instance.chat.completions.create.side_effect = Exception("API Error")
        mock_client.return_value = mock_instance
        
        summarizer = AzureSummarizer()
        summary = summarizer.generate_summary(sample_paper)
        
        assert summary is None
    
    @patch('src.processors.azure_summarizer.AzureOpenAI')
    def test_generate_investment_insights_success(self, mock_client, mock_env, sample_paper):
        """Test successful investment insights generation"""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '投资洞察内容'
        
        mock_instance = Mock()
        mock_instance.chat.completions.create.return_value = mock_response
        mock_client.return_value = mock_instance
        
        summarizer = AzureSummarizer()
        insights = summarizer.generate_investment_insights(sample_paper, '测试摘要')
        
        assert insights == '投资洞察内容'
    
    @patch('src.processors.azure_summarizer.AzureOpenAI')
    def test_generate_investment_insights_includes_summary(self, mock_client, mock_env, sample_paper):
        """Test insights generation includes summary"""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '洞察'
        
        mock_instance = Mock()
        mock_instance.chat.completions.create.return_value = mock_response
        mock_client.return_value = mock_instance
        
        summarizer = AzureSummarizer()
        test_summary = '这是测试摘要'
        summarizer.generate_investment_insights(sample_paper, test_summary)
        
        call_args = mock_instance.chat.completions.create.call_args
        messages = call_args[1]['messages']
        user_message = messages[1]['content']
        
        assert test_summary in user_message
    
    @patch('src.processors.azure_summarizer.AzureOpenAI')
    def test_generate_investment_insights_error_handling(self, mock_client, mock_env, sample_paper):
        """Test insights generation error handling"""
        mock_instance = Mock()
        mock_instance.chat.completions.create.side_effect = Exception("API Error")
        mock_client.return_value = mock_instance
        
        summarizer = AzureSummarizer()
        insights = summarizer.generate_investment_insights(sample_paper, '摘要')
        
        assert insights is None
    
    @patch('src.processors.azure_summarizer.AzureOpenAI')
    def test_build_summary_prompt(self, mock_client, mock_env, sample_paper):
        """Test summary prompt building"""
        summarizer = AzureSummarizer()
        prompt = summarizer._build_summary_prompt(sample_paper)
        
        assert isinstance(prompt, str)
        assert 'Test Paper on Machine Learning' in prompt
        assert '术语速查' in prompt
        assert '商业价值' in prompt
    
    @patch('src.processors.azure_summarizer.AzureOpenAI')
    def test_build_insights_prompt(self, mock_client, mock_env, sample_paper):
        """Test insights prompt building"""
        summarizer = AzureSummarizer()
        prompt = summarizer._build_insights_prompt(sample_paper, '测试摘要')
        
        assert isinstance(prompt, str)
        assert 'Test Paper on Machine Learning' in prompt
        assert '测试摘要' in prompt
        assert '投资' in prompt
    
    @patch('src.processors.azure_summarizer.AzureOpenAI')
    def test_api_parameters(self, mock_client, mock_env, sample_paper):
        """Test API call parameters"""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = 'test'
        
        mock_instance = Mock()
        mock_instance.chat.completions.create.return_value = mock_response
        mock_client.return_value = mock_instance
        
        summarizer = AzureSummarizer()
        summarizer.generate_summary(sample_paper)
        
        call_args = mock_instance.chat.completions.create.call_args
        assert call_args[1]['model'] == 'gpt-4'
        assert call_args[1]['temperature'] == 0.7
        assert call_args[1]['max_tokens'] == 3000
