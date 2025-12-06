# Research Tracker - Technical Decisions & Implementation Plan

## Project Overview
An intelligent research assistant that fetches, analyzes, and summarizes the newest Google Scholar papers in AI and robotics. Designed to help investors stay ahead of technological trends and make data-driven investment decisions.

## Tech Stack Decisions

### 1. Paper Fetching & Data Collection
**Decision: scholarly (Python library)**
- ✅ FREE - No API costs
- ✅ Direct Google Scholar scraping
- ✅ Python-native, easy integration
- ⚠️ Respectful rate limiting required
- 📦 Backup: arXiv API for supplementary papers

**Keywords to track:**
- Artificial Intelligence
- Machine Learning
- Deep Learning
- Computer Vision
- Natural Language Processing
- Robotics
- Autonomous Systems
- Reinforcement Learning
- LLM / Large Language Models
- Generative AI

### 2. AI Summarization & Translation
**Decision: 火山方舟大模型 API (Volcano Engine / ByteDance)**
- ✅ Cost-effective for Chinese market
- ✅ Native Chinese language support
- ✅ Can handle both summarization + translation in one call
- ✅ Good for technical content
- 🔄 **To be implemented after fetch process is complete**

**Alternative considered:**
- DeepSeek API (backup option)
- OpenAI GPT-4o-mini (if Volcano Engine doesn't work)

**Output Language:** Chinese (中文)
**Summary Focus:** Investment insights, technology trends, commercial viability

### 3. Publishing & Notifications
**Decision: Lark (Feishu/飞书) Bot API**
- ✅ FREE webhook integration
- ✅ Rich message formatting (cards, markdown)
- ✅ Easy group notifications
- ✅ Better API than WeChat Official Account
- ✅ Supports images, links, interactive cards

**Message Format:**
- Daily digest at 9:00 AM
- Top 5-10 papers with summaries
- Trend highlights
- Investment signals

### 4. Database & Storage
**To be decided based on scale:**
- SQLite (initial development)
- PostgreSQL (production)
- Optional: Vector DB for semantic search later

### 5. Scheduling
**Options:**
- APScheduler (Python, simple)
- Cron job (Unix)
- GitHub Actions (cloud option)

## Implementation Phases

### Phase 1: Data Collection (Current Focus)
- [ ] Set up project structure
- [ ] Implement scholarly scraper
- [ ] Add keyword filtering
- [ ] Test daily paper fetching
- [ ] Store raw data (JSON/SQLite)

### Phase 2: AI Processing (After Phase 1)
- [ ] Integrate 火山方舟大模型 API
- [ ] Design prompts for investment-focused summaries
- [ ] Generate Chinese summaries
- [ ] Extract key insights

### Phase 3: Publishing
- [ ] Set up Lark Bot
- [ ] Design message templates
- [ ] Implement daily digest
- [ ] Add error handling

### Phase 4: Enhancement
- [ ] Add trend analysis
- [ ] Historical data comparison
- [ ] Citation tracking
- [ ] Web dashboard (optional)

## Development Notes

**Rate Limiting:**
- Google Scholar: Be respectful, add delays (2-5 seconds between requests)
- Implement exponential backoff on failures
- Cache results to avoid re-fetching

**Data Quality:**
- Filter by publication date (last 24-48 hours)
- Filter by citation count (optional quality threshold)
- Deduplicate papers
- Validate metadata

**Error Handling:**
- Retry logic for network failures
- Fallback to arXiv if Scholar fails
- Log all errors
- Send alerts on critical failures

## Environment Variables Needed

```env
# 火山方舟大模型 API (Phase 2)
VOLCANO_API_KEY=your_api_key_here
VOLCANO_API_ENDPOINT=https://ark.cn-beijing.volces.com/api/v3

# Lark Bot (Phase 3)
LARK_WEBHOOK_URL=your_webhook_url_here

# Optional
ARXIV_API_KEY=optional
SMTP_CONFIG=for_email_backup
```

## Dependencies (requirements.txt)

```txt
# Data Collection
scholarly>=1.7.11
arxiv>=2.0.0
requests>=2.31.0
beautifulsoup4>=4.12.0

# Data Processing
pandas>=2.1.0
python-dateutil>=2.8.2

# AI/LLM (Phase 2)
openai>=1.0.0  # For Volcano Engine SDK
httpx>=0.25.0

# Database
sqlalchemy>=2.0.0
sqlite3  # Built-in

# Scheduling
apscheduler>=3.10.0

# Utilities
python-dotenv>=1.0.0
pyyaml>=6.0

# Logging
loguru>=0.7.0
```

## Project Structure

```
research-tracker/
├── copilot.md                    # This file
├── README.md                     # Project overview
├── requirements.txt              # Python dependencies
├── .env.example                  # Environment template
├── .gitignore                    # Git ignore rules
├── src/
│   ├── __init__.py
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py          # Configuration management
│   ├── scrapers/
│   │   ├── __init__.py
│   │   ├── base_scraper.py      # Base scraper class
│   │   ├── scholar_scraper.py   # Google Scholar with scholarly
│   │   └── arxiv_scraper.py     # arXiv backup
│   ├── processors/
│   │   ├── __init__.py
│   │   ├── summarizer.py        # Volcano Engine summarization
│   │   └── translator.py        # If needed separately
│   ├── publishers/
│   │   ├── __init__.py
│   │   └── lark_bot.py          # Lark/Feishu notifications
│   ├── database/
│   │   ├── __init__.py
│   │   ├── models.py            # Data models
│   │   └── repository.py        # Database operations
│   └── utils/
│       ├── __init__.py
│       ├── logger.py            # Logging setup
│       └── helpers.py           # Utility functions
├── scripts/
│   ├── daily_fetch.py           # Main daily job
│   └── test_scraper.py          # Testing scripts
├── data/
│   ├── papers.db                # SQLite database
│   └── logs/                    # Log files
└── tests/
    ├── __init__.py
    └── test_scraper.py          # Unit tests
```

## Next Steps

1. ✅ Create project structure
2. ✅ Set up Python virtual environment
3. ⏳ Implement scholarly scraper (Phase 1)
4. ⏳ Test with real queries
5. ⏳ Add data storage
6. 🔄 Integrate Volcano Engine API (Phase 2)
7. 🔄 Set up Lark Bot (Phase 3)

---

**Last Updated:** December 7, 2025  
**Status:** Planning & Initial Setup  
**Current Phase:** Phase 1 - Data Collection
