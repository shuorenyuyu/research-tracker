# Research Tracker - System Architecture

## 🎯 Design Philosophy

**One Quality Paper Per Day > 100 Unread Papers**

This system is designed around the principle that **curation beats volume** for investment research. Instead of overwhelming users with hundreds of papers, we deliver one carefully selected, high-citation paper daily from cutting-edge fields (AI, Robotics, New Energy, Biotechnology, Quantum Computing, etc.) with actionable insights.

## 🏗️ Three-Phase Architecture

### Phase 1: Data Collection ✅
**Status**: Complete  
**Frequency**: Daily at UTC 00:00  
**Source**: Semantic Scholar API

```
Keywords: ["artificial intelligence", "machine learning", "deep learning", "robotics", 
          "new energy", "battery technology", "solar energy", 
          "biotechnology", "gene editing", "synthetic biology",
          "quantum computing", "autonomous systems"]
         ↓
Semantic Scholar Search (top 100 by citations, year: current_year - 1 onwards)
         ↓
Deduplication Check (paper_id lookup)
         ↓
Store ONE New Paper (highest citations)
         ↓
SQLite Database (data/papers.db)
```

**Key Design Decisions**:
- **Semantic Scholar over arXiv**: Built-in citation data (no extra enrichment needed)
- **Citation ranking over recency**: Community validation matters more than novelty
- **Recent one year window**: Papers from (current_year - 1) onwards have time to accumulate meaningful citations
- **One paper per day**: Prevents database bloat, ensures each paper gets attention
- **Deduplication by paper_id**: Never fetch same paper twice

**Rate Limits**:
- Semantic Scholar: 100 requests / 5 minutes (free tier)
- Current usage: ~4 requests per run (one per keyword)
- Delays: 3 seconds between requests

### Phase 2: AI Summarization 🚧
**Status**: In Progress  
**Frequency**: Daily after Phase 1  
**Engine**: Azure OpenAI (GPT-4)

```
Unprocessed Papers (processed=False)
         ↓
Azure OpenAI API Call #1: Chinese Summary (300-500 chars)
         ↓
Azure OpenAI API Call #2: Investment Insights (200-400 chars)
         ↓
Update Database (summary_zh, investment_insights, processed=True)
```

**Prompt Engineering**:

**Summary Prompt**:
```
你是一位专业的AI和机器人领域研究分析师，擅长用中文总结学术论文的核心内容。

请包括：
1. 研究背景和动机
2. 主要方法/技术
3. 核心贡献和创新点
4. 实验结果（如有）
5. 潜在应用场景
```

**Insights Prompt**:
```
基于以下AI/机器人领域的学术论文，分析其投资价值和技术趋势。

请从投资角度分析：
1. 技术成熟度（早期研究 vs 应用就绪）
2. 商业化潜力（可能的产品/服务方向）
3. 相关行业/公司（可能受益的领域）
4. 投资建议（关注点/风险提示）
```

**Token Economics**:
- Summary: ~800 tokens (prompt) + ~300 tokens (response)
- Insights: ~600 tokens (prompt) + ~200 tokens (response)
- **Total per paper**: ~1,900 tokens (~$0.01 USD with GPT-4)
- **Monthly cost**: ~$0.30 USD (30 papers)

### Phase 3: Article Export ✅
**Status**: Complete  
**Frequency**: On-demand or daily after Phase 2  
**Destination**: WeChat-formatted Markdown/HTML

```
Processed Papers (processed=True)
         ↓
Generate WeChat Article (Markdown + HTML)
         ↓
Save to data/wechat_articles/
         ↓
Manual copy/paste to WeChat 公众号 editor
```

**Article Format** (WeChat):
```markdown
# 🔬 今日AI前沿论文解读

## 📄 论文信息
标题: [Paper Title]
作者: [Authors]
发表: [Venue] ([Year])
引用数: [Citation Count] 次

## 📖 深度解读
[summary_zh with 5 structured sections]

## 💰 投资视角
[investment_insights]

## 📌 原文摘要
[abstract]

> 💡 关于本系列
> 每日精选一篇高引用AI/机器人领域论文...
```

## 🗄️ Database Schema

**Table**: `papers`

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `id` | INTEGER | Primary key | 1 |
| `paper_id` | VARCHAR(200) | **Unique** identifier from source | `"CorpusID:265213145"` |
| `source` | VARCHAR(50) | Data source | `"semantic_scholar"` |
| `title` | TEXT | Paper title | `"Attention Is All You Need"` |
| `authors` | TEXT | Comma-separated | `"Vaswani, A., Shazeer, N."` |
| `year` | INTEGER | Publication year | `2017` |
| `venue` | VARCHAR(200) | Conference/Journal | `"NeurIPS"` |
| `abstract` | TEXT | Full abstract | `"The dominant..."` |
| `url` | VARCHAR(500) | Semantic Scholar URL | `"https://..."` |
| `pdf_url` | VARCHAR(500) | Direct PDF link | `"https://arxiv.org/pdf/..."` |
| `doi` | VARCHAR(200) | DOI identifier | `"10.48550/arXiv.1706.03762"` |
| `citation_count` | INTEGER | Current citations | `114523` |
| `summary_zh` | TEXT | **Chinese summary** | `"本文提出..."` |
| `investment_insights` | TEXT | **Investment analysis** | `"技术成熟度..."` |
| `keywords` | VARCHAR(500) | Search keywords used | `"deep learning"` |
| `fetched_at` | DATETIME | When scraped | `"2025-12-07 00:00:05"` |
| `processed` | BOOLEAN | AI summarized? | `False` → `True` |
| `published` | BOOLEAN | Exported to article? | `False` → `True` |

**Indexes**:
- `paper_id` (UNIQUE) - Fast deduplication lookup
- `processed, fetched_at` - Query unprocessed papers

## 📁 Code Structure

```
src/
├── config/
│   └── settings.py              # Environment variables, paths
│
├── database/
│   ├── models.py                # SQLAlchemy Paper model
│   └── repository.py            # CRUD operations, queries
│
├── scrapers/
│   ├── arxiv_scraper.py         # Legacy (not used)
│   └── semantic_scholar_scraper.py  # Primary data source
│
├── processors/
│   └── azure_summarizer.py      # Azure OpenAI client
│
└── scheduler/
    ├── daily_scheduler.py       # Phase 1: Fetch papers
    └── process_papers.py        # Phase 2: Summarize with Azure
```

## 🔄 Daily Workflow

### Automated Schedule (macOS LaunchAgent)

**Trigger**: `com.researchtracker.scheduler.plist` (UTC 00:00)

```bash
# Phase 1: Fetch (00:00:00 - 00:00:15)
python3 src/scheduler/daily_scheduler.py --run-once
  → Fetches top 100 papers from Semantic Scholar
  → Checks for duplicates
  → Adds ONE new paper (highest citations)
  → Logs: "Today's paper added: 1"

# Phase 2: Summarize (00:00:15 - 00:00:45)
python3 src/scheduler/process_papers.py --one
  → Finds unprocessed paper
  → Generates Chinese summary (Azure OpenAI)
  → Generates investment insights (Azure OpenAI)
  → Marks processed=True
  → Logs: "✅ Successfully processed: [title]"

# Phase 3: Export (00:00:45 - 00:00:50) [On-demand]
python3 scripts/generate_wechat_article.py
  → Finds latest processed paper
  → Generates WeChat-formatted article
  → Saves Markdown + HTML to data/wechat_articles/
  → Ready for manual copy/paste to WeChat
```

**Total Runtime**: ~60 seconds  
**Network Calls**: 6-8 (4 Semantic Scholar + 2 Azure OpenAI)

## 🛡️ Error Handling

### Semantic Scholar Rate Limiting
```python
try:
    response = requests.get(url)
    if response.status_code == 429:
        logger.warning("Rate limit hit, waiting 60s...")
        time.sleep(60)
        response = requests.get(url)  # Retry once
except Exception as e:
    logger.error(f"Semantic Scholar error: {e}")
    return []  # Graceful degradation
```

### Azure OpenAI Failures
```python
try:
    summary = summarizer.generate_summary(paper)
except Exception as e:
    logger.error(f"Azure OpenAI error: {e}")
    summary = None  # Don't mark as processed
    # Will retry tomorrow
```

### Deduplication Edge Cases
- **Same paper, different IDs**: Prevented by using Semantic Scholar's canonical `paper_id`
- **No new papers**: Logs "No new papers found" but doesn't crash
- **Database corruption**: SQLite auto-recovers, backup in `data/papers.db.backup`

## 🔐 Security & Configuration

**Environment Variables** (`.env`):
```bash
# Azure OpenAI (required for Phase 2)
AZURE_OPENAI_ENDPOINT=https://xxx.openai.azure.com/
AZURE_OPENAI_API_KEY=sk-xxxxxxxxxxxxx
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4
AZURE_OPENAI_API_VERSION=2024-02-15-preview

# Database (default: SQLite)
DATABASE_URL=sqlite:///data/papers.db
```

**Secrets Management**:
- `.env` in `.gitignore` (never committed)
- `.env.example` provides template
- Production: Use macOS Keychain or Azure Key Vault

## 📊 Monitoring & Logs

**Log Files** (`data/logs/`):
- `scheduler.log` - Daily fetch operations
- `processor.log` - Azure OpenAI summaries

**Key Metrics**:
```bash
# Check today's fetch
tail -20 data/logs/scheduler.log

# Count total papers
sqlite3 data/papers.db "SELECT COUNT(*) FROM papers;"

# Count unprocessed
sqlite3 data/papers.db "SELECT COUNT(*) FROM papers WHERE processed=0;"

# Top cited papers
sqlite3 data/papers.db "SELECT title, citation_count FROM papers ORDER BY citation_count DESC LIMIT 10;"
```

## 🚀 Deployment Options

### Option 1: macOS LaunchAgent (Recommended)
```bash
./deployment/manage_scheduler.sh install  # Runs at boot
./deployment/manage_scheduler.sh status   # Check if running
./deployment/manage_scheduler.sh logs     # View output
```

**Pros**: Always running, survives reboots  
**Cons**: macOS only

### Option 2: Docker Container
```bash
docker build -t research-tracker .
docker run -d --env-file .env research-tracker
```

**Pros**: Platform-independent, isolated  
**Cons**: Needs Docker setup

### Option 3: Cloud Function (Future)
- AWS Lambda / Azure Functions
- Triggered by CloudWatch/EventGrid cron
- **Pros**: Serverless, scalable
- **Cons**: Cold starts, vendor lock-in

## 🧪 Testing Strategy

**Unit Tests** (`tests/`):
```bash
pytest tests/test_repository.py      # Database operations
pytest tests/test_scraper.py         # Semantic Scholar API
pytest tests/test_summarizer.py      # Azure OpenAI (mocked)
```

**Integration Tests**:
```bash
# End-to-end daily workflow
python3 src/scheduler/daily_scheduler.py --run-once
python3 src/scheduler/process_papers.py --one
python3 scripts/show_papers.py  # Verify results
```

**Manual QA Checklist**:
- [ ] Deduplication works (no duplicate papers)
- [ ] Citation count > 0 (Semantic Scholar data quality)
- [ ] Chinese summary readable (Azure prompt quality)
- [ ] Investment insights actionable (prompt engineering)
- [ ] Logs show no errors (error handling works)

## 🔮 Future Enhancements

1. **Multi-Language Support**: English summaries for international investors
2. **Topic Clustering**: Group papers by research area (NLP, CV, RL, etc.)
3. **Citation Velocity**: Track how fast citations grow (hot topics)
4. **Author Networks**: Identify influential research groups
5. **Company Mentions**: Extract startup/company references from papers
6. **Weekly Digest**: Roll up 7 papers into trend analysis
7. **User Feedback Loop**: Allow rating papers to improve selection

## 📚 References

- [Semantic Scholar API Docs](https://api.semanticscholar.org/)
- [Azure OpenAI Quickstart](https://learn.microsoft.com/en-us/azure/ai-services/openai/quickstart)
- [APScheduler Documentation](https://apscheduler.readthedocs.io/)

---

**Last Updated**: December 7, 2025  
**Version**: 2.0 (One Paper Per Day)
