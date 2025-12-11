"""Tests for database repository"""
import pytest
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.database.models import Base, Paper
from src.database.repository import PaperRepository


class TestPaperRepository:
    """Test PaperRepository class"""
    
    @pytest.fixture
    def db_session(self):
        """Create in-memory database for testing"""
        engine = create_engine('sqlite:///:memory:')
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        yield session
        session.close()
    
    @pytest.fixture
    def repo(self, db_session):
        """Create repository instance"""
        return PaperRepository(db_session)
    
    @pytest.fixture
    def sample_paper_data(self):
        """Sample paper data"""
        return {
            'title': 'Test Paper',
            'paper_id': 'test123',
            'source': 'arxiv',
            'authors': 'John Doe',
            'year': 2024,
            'abstract': 'Test abstract',
            'citation_count': 10,
            'url': 'https://example.com'
        }
    
    def test_add_paper(self, repo, sample_paper_data):
        """Test adding a paper"""
        paper = repo.add_paper(sample_paper_data)
        
        assert paper.id is not None
        assert paper.title == 'Test Paper'
        assert paper.paper_id == 'test123'
    
    def test_get_by_paper_id(self, repo, sample_paper_data):
        """Test getting paper by ID"""
        repo.add_paper(sample_paper_data)
        
        paper = repo.get_by_paper_id('test123')
        
        assert paper is not None
        assert paper.title == 'Test Paper'
    
    def test_get_by_paper_id_with_source(self, repo, sample_paper_data):
        """Test getting paper by ID and source"""
        repo.add_paper(sample_paper_data)
        
        paper = repo.get_by_paper_id('test123', 'arxiv')
        assert paper is not None
        
        paper_wrong_source = repo.get_by_paper_id('test123', 'scholar')
        assert paper_wrong_source is None
    
    def test_get_by_paper_id_not_found(self, repo):
        """Test getting non-existent paper"""
        paper = repo.get_by_paper_id('nonexistent')
        assert paper is None
    
    def test_exists(self, repo, sample_paper_data):
        """Test checking if paper exists"""
        assert not repo.exists('test123')
        
        repo.add_paper(sample_paper_data)
        assert repo.exists('test123')
    
    def test_get_recent_papers(self, repo):
        """Test getting recent papers"""
        # Add papers from different dates
        for i in range(5):
            data = {
                'title': f'Paper {i}',
                'paper_id': f'test{i}',
                'source': 'arxiv',
                'year': 2024,
                'fetched_at': datetime.utcnow() - timedelta(days=i)
            }
            repo.add_paper(data)
        
        recent = repo.get_recent_papers(days=3)
        assert len(recent) == 3
    
    def test_get_unprocessed_papers(self, repo):
        """Test getting unprocessed papers"""
        # Add processed paper
        repo.add_paper({
            'title': 'Processed',
            'paper_id': 'proc1',
            'processed': True
        })
        
        # Add unprocessed papers
        for i in range(3):
            repo.add_paper({
                'title': f'Unprocessed {i}',
                'paper_id': f'unproc{i}',
                'processed': False
            })
        
        unprocessed = repo.get_unprocessed_papers()
        assert len(unprocessed) == 3
    
    def test_get_unprocessed_with_limit(self, repo):
        """Test getting unprocessed papers with limit"""
        for i in range(5):
            repo.add_paper({
                'title': f'Paper {i}',
                'paper_id': f'test{i}',
                'processed': False
            })
        
        unprocessed = repo.get_unprocessed(limit=2)
        assert len(unprocessed) == 2
    
    def test_get_unpublished_papers(self, repo):
        """Test getting unpublished papers"""
        # Processed but not published
        repo.add_paper({
            'title': 'Ready to publish',
            'paper_id': 'ready1',
            'processed': True,
            'published': False
        })
        
        # Processed and published
        repo.add_paper({
            'title': 'Already published',
            'paper_id': 'pub1',
            'processed': True,
            'published': True
        })
        
        unpublished = repo.get_unpublished_papers()
        assert len(unpublished) == 1
        assert unpublished[0].paper_id == 'ready1'
    
    def test_mark_as_processed(self, repo, sample_paper_data):
        """Test marking paper as processed"""
        repo.add_paper(sample_paper_data)
        
        repo.mark_as_processed('test123')
        
        paper = repo.get_by_paper_id('test123')
        assert paper.processed is True
    
    def test_mark_as_published(self, repo, sample_paper_data):
        """Test marking paper as published"""
        repo.add_paper(sample_paper_data)
        
        repo.mark_as_published('test123')
        
        paper = repo.get_by_paper_id('test123')
        assert paper.published is True
    
    def test_update_citation_count(self, repo, sample_paper_data):
        """Test updating citation count"""
        paper = repo.add_paper(sample_paper_data)
        
        repo.update_citation_count(paper.id, 50)
        
        updated_paper = repo.get_by_paper_id('test123')
        assert updated_paper.citation_count == 50
    
    def test_update_summary(self, repo, sample_paper_data):
        """Test updating summary"""
        repo.add_paper(sample_paper_data)
        
        repo.update_summary(
            'test123',
            summary_zh='中文摘要',
            keywords='AI, ML',
            insights='投资洞察'
        )
        
        paper = repo.get_by_paper_id('test123')
        assert paper.summary_zh == '中文摘要'
        assert paper.keywords == 'AI, ML'
        assert paper.investment_insights == '投资洞察'
        assert paper.processed is True
    
    def test_get_papers_by_keyword(self, repo):
        """Test searching papers by keyword"""
        repo.add_paper({
            'title': 'Machine Learning Paper',
            'paper_id': 'ml1',
            'abstract': 'About neural networks'
        })
        
        repo.add_paper({
            'title': 'Quantum Computing',
            'paper_id': 'qc1',
            'abstract': 'About qubits'
        })
        
        ml_papers = repo.get_papers_by_keyword('Learning')
        assert len(ml_papers) == 1
        assert ml_papers[0].paper_id == 'ml1'
    
    def test_get_top_cited_papers(self, repo):
        """Test getting top cited papers"""
        for i in range(5):
            repo.add_paper({
                'title': f'Paper {i}',
                'paper_id': f'cite{i}',
                'citation_count': i * 10,
                'fetched_at': datetime.utcnow()
            })
        
        top_papers = repo.get_top_cited_papers(limit=3)
        assert len(top_papers) == 3
        assert top_papers[0].citation_count == 40
        assert top_papers[1].citation_count == 30
    
    def test_count_unprocessed(self, repo):
        """Test counting unprocessed papers"""
        for i in range(3):
            repo.add_paper({
                'title': f'Paper {i}',
                'paper_id': f'test{i}',
                'processed': False
            })
        
        count = repo.count_unprocessed()
        assert count == 3
    
    def test_get_all_papers(self, repo):
        """Test getting all papers"""
        for i in range(10):
            repo.add_paper({
                'title': f'Paper {i}',
                'paper_id': f'all{i}'
            })
        
        all_papers = repo.get_all_papers()
        assert len(all_papers) == 10
        
        limited = repo.get_all_papers(limit=5)
        assert len(limited) == 5
