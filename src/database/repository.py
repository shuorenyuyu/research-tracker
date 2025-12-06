"""Database repository for paper operations"""

from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from .models import Paper


class PaperRepository:
    """Repository for paper database operations"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def add_paper(self, paper: Paper) -> Paper:
        """Add a new paper to database"""
        self.session.add(paper)
        self.session.commit()
        self.session.refresh(paper)
        return paper
    
    def get_by_paper_id(self, paper_id: str) -> Optional[Paper]:
        """Get paper by its unique ID"""
        return self.session.query(Paper).filter(Paper.paper_id == paper_id).first()
    
    def exists(self, paper_id: str) -> bool:
        """Check if paper exists in database"""
        return self.session.query(Paper).filter(Paper.paper_id == paper_id).count() > 0
    
    def get_recent_papers(self, days: int = 7, limit: int = 100) -> List[Paper]:
        """Get papers fetched in the last N days"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        return (
            self.session.query(Paper)
            .filter(Paper.fetched_at >= cutoff_date)
            .order_by(Paper.fetched_at.desc())
            .limit(limit)
            .all()
        )
    
    def get_unprocessed_papers(self, limit: int = 50) -> List[Paper]:
        """Get papers that haven't been processed by AI yet"""
        return (
            self.session.query(Paper)
            .filter(Paper.processed == False)
            .order_by(Paper.fetched_at.desc())
            .limit(limit)
            .all()
        )
    
    def get_unpublished_papers(self, limit: int = 20) -> List[Paper]:
        """Get processed papers that haven't been published yet"""
        return (
            self.session.query(Paper)
            .filter(Paper.processed == True, Paper.published == False)
            .order_by(Paper.fetched_at.desc())
            .limit(limit)
            .all()
        )
    
    def mark_as_processed(self, paper_id: str):
        """Mark a paper as processed"""
        paper = self.get_by_paper_id(paper_id)
        if paper:
            paper.processed = True
            self.session.commit()
    
    def mark_as_published(self, paper_id: str):
        """Mark a paper as published"""
        paper = self.get_by_paper_id(paper_id)
        if paper:
            paper.published = True
            self.session.commit()
    
    def update_summary(self, paper_id: str, summary_zh: str, keywords: str, insights: str):
        """Update paper with AI-generated content"""
        paper = self.get_by_paper_id(paper_id)
        if paper:
            paper.summary_zh = summary_zh
            paper.keywords = keywords
            paper.investment_insights = insights
            paper.processed = True
            self.session.commit()
    
    def get_papers_by_keyword(self, keyword: str, limit: int = 50) -> List[Paper]:
        """Search papers by keyword in title or abstract"""
        return (
            self.session.query(Paper)
            .filter(
                (Paper.title.ilike(f"%{keyword}%")) | 
                (Paper.abstract.ilike(f"%{keyword}%"))
            )
            .order_by(Paper.citation_count.desc())
            .limit(limit)
            .all()
        )
    
    def get_top_cited_papers(self, days: int = 30, limit: int = 20) -> List[Paper]:
        """Get most cited papers from recent period"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        return (
            self.session.query(Paper)
            .filter(Paper.fetched_at >= cutoff_date)
            .order_by(Paper.citation_count.desc())
            .limit(limit)
            .all()
        )
