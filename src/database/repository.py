"""Database repository for paper operations"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from .models import Paper, get_session


class PaperRepository:
    """Repository for paper database operations"""
    
    def __init__(self, session: Session = None):
        self.session = session or get_session()
    
    def add_paper(self, paper_data: Dict[str, Any]) -> Paper:
        """Add a new paper to database"""
        # Convert dict to Paper object if needed
        if isinstance(paper_data, dict):
            paper = Paper(
                title=paper_data.get('title'),
                paper_id=paper_data.get('paper_id'),
                source=paper_data.get('source'),
                authors=paper_data.get('authors'),
                first_author=paper_data.get('first_author'),
                year=paper_data.get('year'),
                publication_date=paper_data.get('publication_date'),
                venue=paper_data.get('venue'),
                publisher=paper_data.get('publisher'),
                abstract=paper_data.get('abstract'),
                url=paper_data.get('url'),
                pdf_url=paper_data.get('pdf_url'),
                citation_count=paper_data.get('citation_count', 0),
                doi=paper_data.get('doi'),
                keywords=paper_data.get('keywords'),
                fetched_at=paper_data.get('fetched_at', datetime.utcnow()),
                processed=paper_data.get('processed', False),
                published=paper_data.get('published', False)
            )
        else:
            paper = paper_data
        
        self.session.add(paper)
        self.session.commit()
        self.session.refresh(paper)
        return paper
    
    def get_by_paper_id(self, paper_id: str, source: str = None) -> Optional[Paper]:
        """Get paper by its unique ID and optionally source"""
        query = self.session.query(Paper).filter(Paper.paper_id == paper_id)
        if source:
            query = query.filter(Paper.source == source)
        return query.first()
    
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
    
    def get_unprocessed(self, limit: int = None) -> List[Paper]:
        """Alias for get_unprocessed_papers with optional limit"""
        query = self.session.query(Paper).filter(Paper.processed == False).order_by(Paper.fetched_at.desc())
        if limit:
            query = query.limit(limit)
        return query.all()
    
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
    
    def update_citation_count(self, paper_id: int, citation_count: int):
        """Update paper citation count"""
        paper = self.session.query(Paper).filter(Paper.id == paper_id).first()
        if paper:
            paper.citation_count = citation_count
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
    
    def count_all(self) -> int:
        """Count total papers in database"""
        return self.session.query(Paper).count()
    
    def count_unprocessed(self) -> int:
        """Count papers waiting for AI summarization"""
        return self.session.query(Paper).filter(Paper.processed == False).count()
    
    def get_all_papers(self, limit: int = None, offset: int = 0) -> List[Paper]:
        """Get all papers with optional pagination"""
        query = self.session.query(Paper).order_by(Paper.fetched_at.desc())
        if offset:
            query = query.offset(offset)
        if limit:
            query = query.limit(limit)
        return query.all()
