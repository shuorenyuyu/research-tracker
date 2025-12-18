#!/usr/bin/env python3
"""
Remove duplicate papers from the database and enforce uniqueness.
Keeps the most recently fetched record when duplicates are found.
"""
import argparse
from typing import Dict, Any, Optional

from src.config.settings import Settings
from src.database.models import init_database
from src.database.repository import PaperRepository


def run_dedupe(database_url: Optional[str] = None) -> Dict[str, Any]:
    """
    Run deduplication and return summary stats.

    Args:
        database_url: Optional database URL to override defaults.

    Returns:
        Dictionary with counts and index creation status.
    """
    settings = Settings()
    db_url = database_url or settings.database_url
    init_database(db_url)
    repo = PaperRepository()

    removed = repo.deduplicate()
    index_created = repo.ensure_unique_paper_id_index()

    return {
        "removed_by_paper_id": removed["removed_by_paper_id"],
        "removed_by_title": removed["removed_by_title"],
        "index_created": index_created,
        "total_after": repo.count_all(),
    }


def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(description="Deduplicate papers database")
    parser.add_argument(
        "--database-url",
        dest="database_url",
        help="Optional database URL override (default: Settings.DATABASE_URL)",
    )
    args = parser.parse_args()

    result = run_dedupe(database_url=args.database_url)

    print("=== Deduplication Summary ===")
    print(f"Removed by paper_id: {result['removed_by_paper_id']}")
    print(f"Removed by title:    {result['removed_by_title']}")
    print(f"Unique index created: {result['index_created']}")
    print(f"Total rows after:    {result['total_after']}")


if __name__ == "__main__":
    main()
