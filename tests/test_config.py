"""Tests for configuration module"""
import os
import pytest
from pathlib import Path
from src.config.settings import Settings


class TestSettings:
    """Test Settings class"""
    
    def test_base_dir_exists(self):
        """Test BASE_DIR is properly set"""
        assert Settings.BASE_DIR.exists()
        assert Settings.BASE_DIR.is_dir()
    
    def test_data_dir_path(self):
        """Test DATA_DIR path"""
        assert Settings.DATA_DIR == Settings.BASE_DIR / "data"
    
    def test_log_dir_path(self):
        """Test LOG_DIR path"""
        assert Settings.LOG_DIR == Settings.DATA_DIR / "logs"
    
    def test_database_url_default(self):
        """Test DATABASE_URL default value"""
        assert "sqlite:///" in Settings.DATABASE_URL
        assert "papers.db" in Settings.DATABASE_URL
    
    def test_azure_openai_settings(self):
        """Test Azure OpenAI settings exist"""
        assert hasattr(Settings, 'AZURE_OPENAI_ENDPOINT')
        assert hasattr(Settings, 'AZURE_OPENAI_API_KEY')
        assert hasattr(Settings, 'AZURE_OPENAI_DEPLOYMENT_NAME')
        assert hasattr(Settings, 'AZURE_OPENAI_API_VERSION')
    
    def test_semantic_scholar_api_key(self):
        """Test Semantic Scholar API key setting"""
        assert hasattr(Settings, 'SEMANTIC_SCHOLAR_API_KEY')
    
    def test_fetch_limit_type(self):
        """Test FETCH_LIMIT is integer"""
        assert isinstance(Settings.FETCH_LIMIT, int)
        assert Settings.FETCH_LIMIT > 0
    
    def test_rate_limit_delay_type(self):
        """Test RATE_LIMIT_DELAY is integer"""
        assert isinstance(Settings.RATE_LIMIT_DELAY, int)
        assert Settings.RATE_LIMIT_DELAY >= 0
    
    def test_keywords_is_list(self):
        """Test KEYWORDS is a list"""
        assert isinstance(Settings.KEYWORDS, list)
        assert len(Settings.KEYWORDS) > 0
    
    def test_keywords_not_empty(self):
        """Test KEYWORDS contains non-empty strings"""
        for keyword in Settings.KEYWORDS:
            assert isinstance(keyword, str)
            assert len(keyword.strip()) > 0
    
    def test_arxiv_enabled_type(self):
        """Test ARXIV_ENABLED is boolean"""
        assert isinstance(Settings.ARXIV_ENABLED, bool)
    
    def test_log_level_valid(self):
        """Test LOG_LEVEL is valid"""
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        assert Settings.LOG_LEVEL in valid_levels
    
    def test_ensure_directories_creates_data_dir(self, tmp_path, monkeypatch):
        """Test ensure_directories creates DATA_DIR"""
        test_data_dir = tmp_path / "test_data"
        test_log_dir = test_data_dir / "logs"
        
        monkeypatch.setattr(Settings, 'DATA_DIR', test_data_dir)
        monkeypatch.setattr(Settings, 'LOG_DIR', test_log_dir)
        
        Settings.ensure_directories()
        
        assert test_data_dir.exists()
        assert test_log_dir.exists()
    
    def test_database_url_property(self):
        """Test database_url property"""
        settings = Settings()
        db_url = settings.database_url
        assert isinstance(db_url, str)
        assert len(db_url) > 0
    
    def test_keywords_property(self):
        """Test keywords property"""
        settings = Settings()
        keywords = settings.keywords
        assert isinstance(keywords, list)
        assert keywords == Settings.KEYWORDS
    
    def test_lark_webhook_url_exists(self):
        """Test LARK_WEBHOOK_URL setting exists"""
        assert hasattr(Settings, 'LARK_WEBHOOK_URL')
