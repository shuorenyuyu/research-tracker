# GitHub Copilot Instructions for Research Tracker

## Project Overview
**Research Tracker** is an automated research paper tracking system that fetches **one high-quality research paper daily** from cutting-edge fields (AI, Robotics, New Energy, Biotechnology, Quantum Computing, etc.), generates Chinese summaries with Azure OpenAI, and provides investment insights.

### Philosophy: Quality Over Quantity
Instead of drowning in 100+ papers daily, we deliver **one carefully selected paper per day**:
- ✅ Ranked by **citation count** (community validation)
- ✅ Filtered by **AI/ML/Robotics/New Energy/Biotech keywords**
- ✅ **Deduplicated** (never fetch same paper twice)
- ✅ **Chinese summary** + investment insights
- ✅ Runs **fully automated** at UTC 00:00

## Tech Stack
- **Language**: Python 3.11+
- **Database**: SQLite (data/papers.db)
- **APIs**: Semantic Scholar (free), Azure OpenAI (GPT-4)
- **Automation**: macOS LaunchAgent (or cron for Linux)
- **Framework**: SQLAlchemy for ORM
- **Testing**: pytest with 99% coverage requirement

## Critical Development Rules

### 1. Test Coverage - **99% MINIMUM** 🎯
**MANDATORY**: After ANY code modification, you MUST:
1. Write comprehensive tests covering all new/modified code
2. Run the test suite: `pytest --cov=. --cov-report=json --cov-report=html`
3. Verify coverage is **≥99%** in `coverage.json` or `.coverage`
4. If coverage drops below 99%, add more tests until it reaches 99%+

**Test Requirements**:
- Unit tests for all functions and methods
- Mock external APIs (Semantic Scholar, Azure OpenAI)
- Test deduplication logic thoroughly
- Test both success and failure scenarios
- Edge cases: rate limits, network errors, empty results

**Example Test Structure**:
```python
# tests/test_semantic_scholar_scraper.py
import pytest
from unittest.mock import Mock, patch
from src.scrapers.semantic_scholar_scraper import SemanticScholarScraper

class TestSemanticScholarScraper:
    def test_fetch_papers_success(self):
        # Test successful paper fetch with mocked API
        pass
    
    def test_fetch_papers_rate_limit(self):
        # Test 429 rate limit handling
        pass
    
    def test_deduplication_existing_paper(self):
        # Test that existing papers are skipped
        pass
```

### 2. Code Quality Standards
- **Type hints**: All functions must have type annotations
- **Docstrings**: Required for all public functions/classes (Google style)
- **Error handling**: Always handle API failures gracefully
- **Logging**: Use proper logging (not print statements)
- **Code style**: Follow PEP 8, use `black` for formatting

### 3. Semantic Scholar API Guidelines
**Rate Limits**: 100 requests / 5 minutes (free tier)

**Best Practices**:
- Add 3-second delays between requests
- Implement retry logic for 429 errors (wait 60s, retry once)
- Cache responses when possible
- Use `fields` parameter to limit data size

**Example API Call**:
```python
import requests
import time

def fetch_papers(keyword: str, year: int) -> list:
    """
    Fetch papers from Semantic Scholar.
    
    Args:
        keyword: Search keyword (e.g., 'deep learning')
        year: Minimum publication year
    
    Returns:
        List of paper dictionaries
    
    Raises:
        requests.HTTPError: If API returns error status
    """
    url = f"https://api.semanticscholar.org/graph/v1/paper/search"
    params = {
        "query": keyword,
        "year": f"{year}-",
        "limit": 100,
        "fields": "title,authors,year,citationCount,abstract"
    }
    
    time.sleep(3)  # Rate limiting
    response = requests.get(url, params=params)
    
    if response.status_code == 429:
        logger.warning("Rate limit hit, retrying in 60s...")
        time.sleep(60)
        response = requests.get(url, params=params)
    
    response.raise_for_status()
    return response.json().get("data", [])
```

### 4. Azure OpenAI Integration Guidelines
**Prompt Engineering**:
- Keep prompts concise and structured
- Use system messages for role definition
- Specify output format and length clearly
- Test with multiple papers to ensure consistency

**Token Economics**:
- Summary: ~800 tokens (prompt) + ~300 tokens (response)
- Insights: ~600 tokens (prompt) + ~200 tokens (response)
- **Total per paper**: ~1,900 tokens (~$0.01 USD with GPT-4)
- **Monthly cost**: ~$0.30 USD (30 papers)

**Example Summarization**:
```python
from openai import AzureOpenAI

def generate_summary(paper: dict) -> str:
    """
    Generate Chinese summary using Azure OpenAI.
    
    Args:
        paper: Dictionary with title, abstract, authors
    
    Returns:
        Chinese summary (800-1500 characters)
    
    Raises:
        Exception: If Azure OpenAI API fails
    """
    client = AzureOpenAI(
        endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version="2024-02-15-preview"
    )
    
    prompt = f"""你是一位专业的AI研究分析师。请用中文总结以下论文：

标题：{paper['title']}
摘要：{paper['abstract']}

请包括：
1. 研究背景和动机
2. 主要方法/技术
3. 核心贡献和创新点
4. 实验结果（如有）
5. 潜在应用场景

字数：800-1500字"""
    
    response = client.chat.completions.create(
        model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
        messages=[
            {"role": "system", "content": "你是专业的AI研究分析师"},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=800
    )
    
    return response.choices[0].message.content
```

### 5. Database & Data Management
**Deduplication Strategy**:
- Use `paper_id` as unique constraint (Semantic Scholar canonical ID)
- Check database BEFORE adding new paper
- Log skipped duplicates for monitoring

**Example Repository Pattern**:
```python
from sqlalchemy.orm import Session
from src.database.models import Paper

class PaperRepository:
    def __init__(self, session: Session):
        self.session = session
    
    def paper_exists(self, paper_id: str) -> bool:
        """Check if paper already exists in database."""
        return self.session.query(Paper).filter(
            Paper.paper_id == paper_id
        ).first() is not None
    
    def add_paper(self, paper_data: dict) -> Paper:
        """Add new paper to database."""
        paper = Paper(**paper_data)
        self.session.add(paper)
        self.session.commit()
        return paper
```

### 6. Daily Scheduler Guidelines
**Workflow**:
1. **Phase 1** (00:00:00 - 00:00:15): Fetch top 100 papers by citations
2. **Phase 2** (00:00:15 - 00:00:45): Generate summary + insights with Azure OpenAI
3. **Phase 3** (00:00:45 - 00:00:50): Export to WeChat-formatted article (on-demand)

**Error Handling**:
- If Semantic Scholar fails → Log error, exit gracefully (retry tomorrow)
- If Azure OpenAI fails → Don't mark as processed (retry tomorrow)
- If no new papers found → Log "No new papers", exit successfully

**Example Scheduler**:
```python
def daily_fetch_one_paper():
    """Daily scheduled task to fetch one high-quality paper."""
    logger.info("Starting daily paper fetch...")
    
    try:
        # Fetch papers from multiple keywords
        all_papers = []
        for keyword in KEYWORDS:
            papers = scraper.fetch_papers(keyword, year=current_year - 1)
            all_papers.extend(papers)
        
        # Sort by citation count (descending)
        all_papers.sort(key=lambda p: p.get("citationCount", 0), reverse=True)
        
        # Find first new paper
        for paper in all_papers:
            if not repository.paper_exists(paper["paperId"]):
                repository.add_paper(paper)
                logger.info(f"Added: {paper['title']}")
                return
        
        logger.info("No new papers found today")
    
    except Exception as e:
        logger.error(f"Daily fetch failed: {e}")
        raise
```

### 7. Git Workflow
**Commit Message Format**:
```
feat: add citation velocity tracking
fix: handle Semantic Scholar rate limits better
test: add 99% coverage for scraper module
docs: update API documentation
```

**Before Committing**:
1. Run tests: `pytest --cov=. --cov-report=json`
2. Check coverage: Must be ≥99%
3. Run linter: `black . && flake8 .`
4. Update CHANGELOG.md if significant change

### 8. Deployment & Production
**macOS LaunchAgent** (Recommended):
```bash
# Install service (runs at UTC 00:00)
./deployment/manage_scheduler.sh install

# Check status
./deployment/manage_scheduler.sh status

# View logs
./deployment/manage_scheduler.sh logs

# Manual test run
./deployment/manage_scheduler.sh run-once
```

**Linux Cron** (Alternative):
```bash
# Add to crontab (runs at UTC 00:00 daily)
0 0 * * * cd ~/research-tracker && ./venv/bin/python src/scheduler/daily_scheduler.py --run-once >> data/logs/cron.log 2>&1
```

### 9. Documentation
**Update these files when modifying code**:
- `README.md` - For user-facing features
- `ARCHITECTURE.md` - For system design changes
- `CHANGELOG.md` - For version history
- `DEPLOYMENT.md` - For deployment instructions
- Docstrings - For all functions and classes

### 10. Performance & Optimization
**Current Metrics**:
- Total runtime per day: ~60 seconds
- Network calls: 6-8 (4 Semantic Scholar + 2 Azure OpenAI)
- Database size: ~1MB per 100 papers
- Cost: ~$0.01 per paper (Azure OpenAI)

**Optimization Guidelines**:
- Cache Semantic Scholar responses (1 hour TTL)
- Batch Azure OpenAI calls if processing multiple papers
- Use database indexes on `paper_id`, `processed`, `fetched_at`
- Monitor API usage to avoid rate limits

## Common Tasks Reference

### Running Tests
```bash
# Run all tests with coverage
pytest --cov=src --cov-report=json --cov-report=html

# Run specific test file
pytest tests/test_semantic_scholar_scraper.py -v

# Check coverage report
python -c "import json; print(json.load(open('coverage.json'))['totals']['percent_covered'])"
open htmlcov/index.html  # View HTML report
```

### Manual Operations
```bash
# Fetch one paper manually
python3 src/scheduler/daily_scheduler.py --run-once

# Process unprocessed papers
python3 src/scheduler/process_papers.py --one

# View database contents
python3 scripts/show_papers.py

# Generate WeChat article
python3 scripts/generate_wechat_article.py
```

### Database Inspection
```bash
# Count total papers
sqlite3 data/papers.db "SELECT COUNT(*) FROM papers;"

# Count unprocessed papers
sqlite3 data/papers.db "SELECT COUNT(*) FROM papers WHERE processed=0;"

# Top cited papers
sqlite3 data/papers.db "SELECT title, citation_count FROM papers ORDER BY citation_count DESC LIMIT 10;"

# Check duplicates (should be 0)
sqlite3 data/papers.db "SELECT paper_id, COUNT(*) FROM papers GROUP BY paper_id HAVING COUNT(*) > 1;"
```

### Environment Setup
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure Azure OpenAI
cp .env.example .env
# Edit .env with your credentials
```

## Project Structure Reference
```
research-tracker/
├── src/
│   ├── config/
│   │   └── settings.py          # Environment variables, paths
│   ├── database/
│   │   ├── models.py            # SQLAlchemy Paper model
│   │   └── repository.py        # CRUD operations
│   ├── scrapers/
│   │   └── semantic_scholar_scraper.py  # Primary data source
│   ├── processors/
│   │   └── azure_summarizer.py  # Azure OpenAI integration
│   └── scheduler/
│       ├── daily_scheduler.py   # Phase 1: Fetch papers
│       └── process_papers.py    # Phase 2: Summarize with Azure
├── scripts/
│   ├── show_papers.py           # View database contents
│   └── generate_wechat_article.py  # Export to WeChat format
├── tests/                       # Unit tests (99% coverage required)
├── deployment/                  # macOS LaunchAgent config
├── data/
│   ├── papers.db               # SQLite database
│   ├── wechat_articles/        # Exported articles
│   └── logs/                   # Scheduler and processor logs
└── requirements.txt            # Python dependencies
```

## Database Schema
```sql
CREATE TABLE papers (
    id INTEGER PRIMARY KEY,
    paper_id VARCHAR(200) UNIQUE NOT NULL,  -- Deduplication key
    source VARCHAR(50) DEFAULT 'semantic_scholar',
    title TEXT NOT NULL,
    authors TEXT,
    year INTEGER,
    venue VARCHAR(200),
    abstract TEXT,
    url VARCHAR(500),
    pdf_url VARCHAR(500),
    doi VARCHAR(200),
    citation_count INTEGER DEFAULT 0,
    summary_zh TEXT,              -- Chinese summary (Azure OpenAI)
    investment_insights TEXT,     -- Investment analysis (Azure OpenAI)
    keywords VARCHAR(500),
    fetched_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    processed BOOLEAN DEFAULT 0,  -- AI summarization done?
    published BOOLEAN DEFAULT 0   -- Exported to article?
);

CREATE INDEX idx_paper_id ON papers(paper_id);
CREATE INDEX idx_processed ON papers(processed, fetched_at);
```

## Integration with alpha-research
This project provides research data for the **alpha-research** dashboard:
- **Database sync**: `alpha-research` reads from `data/papers.db`
- **API integration**: alpha-research API serves papers to frontend
- **Deployment**: Both projects run on same Azure VM (20.51.208.13)

## Questions or Issues?
Refer to:
- `README.md` - Quick start guide and overview
- `ARCHITECTURE.md` - Detailed system design
- `DEPLOYMENT.md` - Production deployment guide
- `SEMANTIC_SCHOLAR_API.md` - API usage examples

---

**REMEMBER**: 99% test coverage is NOT optional. Every code change MUST include tests!

**Key Metrics to Monitor**:
- Daily fetch success rate (should be 100%)
- Deduplication accuracy (no duplicate papers)
- Azure OpenAI success rate (should be >95%)
- Test coverage (must stay ≥99%)
