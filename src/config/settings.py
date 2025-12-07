"""Configuration settings for Research Tracker"""

import os
from pathlib import Path
from typing import List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings:
    """Application settings"""
    
    # Project paths
    BASE_DIR = Path(__file__).resolve().parent.parent.parent
    DATA_DIR = BASE_DIR / "data"
    LOG_DIR = DATA_DIR / "logs"
    
    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DATA_DIR}/papers.db")
    
    # Azure OpenAI API
    AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "")
    AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY", "")
    AZURE_OPENAI_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4")
    AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
    
    # Lark Bot (飞书)
    LARK_WEBHOOK_URL = os.getenv("LARK_WEBHOOK_URL", "")
    
    # Scraping settings
    FETCH_LIMIT = int(os.getenv("FETCH_LIMIT", "50"))
    RATE_LIMIT_DELAY = int(os.getenv("RATE_LIMIT_DELAY", "3"))
    
    # Keywords for paper search
    KEYWORDS: List[str] = [
        keyword.strip() 
        for keyword in os.getenv(
            "KEYWORDS", 
            "artificial intelligence,machine learning,deep learning,robotics"
        ).split(",")
    ]
    
    # Optional features
    ARXIV_ENABLED = os.getenv("ARXIV_ENABLED", "true").lower() == "true"
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    @classmethod
    def ensure_directories(cls):
        """Create necessary directories if they don't exist"""
        cls.DATA_DIR.mkdir(exist_ok=True)
        cls.LOG_DIR.mkdir(exist_ok=True)
    
    @property
    def database_url(self):
        """Get database URL with proper path resolution"""
        return str(self.DATABASE_URL)
    
    @property
    def keywords(self):
        """Get search keywords as list"""
        return self.KEYWORDS


# Initialize directories
Settings.ensure_directories()
