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
    
    # Volcano Engine API (火山方舟)
    VOLCANO_API_KEY = os.getenv("VOLCANO_API_KEY", "")
    VOLCANO_API_ENDPOINT = os.getenv("VOLCANO_API_ENDPOINT", "")
    
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


# Initialize directories
Settings.ensure_directories()
