"""Tests for logger utility"""
import pytest
import logging
from pathlib import Path
from src.utils.logger import setup_logger


class TestLogger:
    """Test logger setup"""
    
    def test_setup_logger_creates_logger(self, tmp_path, monkeypatch):
        """Test that setup_logger creates a logger"""
        # Use temp directory for logs
        from src.config.settings import Settings
        test_log_dir = tmp_path / "logs"
        test_log_dir.mkdir()
        monkeypatch.setattr(Settings, 'LOG_DIR', test_log_dir)
        
        logger = setup_logger("test_logger")
        
        assert logger is not None
        assert isinstance(logger, logging.Logger)
        assert logger.name == "test_logger"
    
    def test_setup_logger_log_level(self, tmp_path, monkeypatch):
        """Test logger log level configuration"""
        from src.config.settings import Settings
        test_log_dir = tmp_path / "logs"
        test_log_dir.mkdir()
        monkeypatch.setattr(Settings, 'LOG_DIR', test_log_dir)
        monkeypatch.setattr(Settings, 'LOG_LEVEL', 'DEBUG')
        
        logger = setup_logger("debug_logger")
        
        assert logger.level == logging.DEBUG
    
    def test_setup_logger_creates_log_file(self, tmp_path, monkeypatch):
        """Test that logger creates log file"""
        from src.config.settings import Settings
        test_log_dir = tmp_path / "logs"
        test_log_dir.mkdir()
        monkeypatch.setattr(Settings, 'LOG_DIR', test_log_dir)
        
        logger = setup_logger("file_test")
        logger.info("Test message")
        
        log_file = test_log_dir / "file_test.log"
        assert log_file.exists()
    
    def test_setup_logger_writes_to_file(self, tmp_path, monkeypatch):
        """Test that logger writes messages to file"""
        from src.config.settings import Settings
        test_log_dir = tmp_path / "logs"
        test_log_dir.mkdir()
        monkeypatch.setattr(Settings, 'LOG_DIR', test_log_dir)
        
        logger = setup_logger("write_test")
        test_message = "Test log message"
        logger.info(test_message)
        
        log_file = test_log_dir / "write_test.log"
        content = log_file.read_text()
        
        assert test_message in content
    
    def test_setup_logger_different_levels(self, tmp_path, monkeypatch):
        """Test logger with different log levels"""
        from src.config.settings import Settings
        test_log_dir = tmp_path / "logs"
        test_log_dir.mkdir()
        monkeypatch.setattr(Settings, 'LOG_DIR', test_log_dir)
        
        for level in ['DEBUG', 'INFO', 'WARNING', 'ERROR']:
            monkeypatch.setattr(Settings, 'LOG_LEVEL', level)
            logger = setup_logger(f"{level.lower()}_logger")
            
            expected_level = getattr(logging, level)
            assert logger.level == expected_level
