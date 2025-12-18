"""Tests for deduplication utilities"""
from datetime import datetime, timedelta
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from scripts.dedupe_papers import run_dedupe
from src.database.models import Base, init_database
from src.database.repository import PaperRepository


@pytest.fixture
def db_session():
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    session_maker = sessionmaker(bind=engine)
    session = session_maker()
    try:
        yield session
    finally:
        session.close()


def test_deduplicate_prefers_newer_record(db_session):
    repo = PaperRepository(db_session)
    base_time = datetime(2024, 1, 1)

    repo.add_paper({
        'title': '自然语言处理的前沿进展',
        'paper_id': 'dup-a',
        'fetched_at': base_time,
    })
    repo.add_paper({
        'title': '自然语言处理的前沿进展',
        'paper_id': 'dup-b',
        'fetched_at': base_time + timedelta(days=1),
    })
    repo.add_paper({
        'title': 'Unique title',
        'paper_id': 'unique-id',
        'fetched_at': base_time,
    })

    removed = repo.deduplicate()

    assert removed['removed_by_paper_id'] == 0
    assert removed['removed_by_title'] == 1

    remaining = repo.get_all_papers()
    remaining_ids = {paper.paper_id for paper in remaining}
    assert 'dup-b' in remaining_ids
    assert 'dup-a' not in remaining_ids
    assert 'unique-id' in remaining_ids
    assert len(remaining_ids) == 2


def test_is_duplicate_checks_title_and_id(db_session):
    repo = PaperRepository(db_session)
    repo.add_paper({
        'title': 'Test Title',
        'paper_id': 'paper-123',
    })

    assert repo.is_duplicate(paper_id='paper-123') is True
    assert repo.is_duplicate(title=' test title ') is True
    assert repo.is_duplicate(title='Another title') is False


def test_ensure_unique_index_and_cli(tmp_path):
    db_path = tmp_path / 'papers.db'
    db_url = f'sqlite:///{db_path}'

    init_database(db_url)
    repo = PaperRepository()
    repo.add_paper({'title': 'Index Test', 'paper_id': 'idx-1'})
    repo.add_paper({'title': 'Index Test', 'paper_id': 'idx-2'})
    repo.session.close()

    result = run_dedupe(database_url=db_url)

    assert result['removed_by_paper_id'] == 0
    assert result['removed_by_title'] == 1
    assert result['index_created'] is True
    assert result['total_after'] == 1

    # Reset global session to avoid leaking config to other tests
    init_database('sqlite:///:memory:')
