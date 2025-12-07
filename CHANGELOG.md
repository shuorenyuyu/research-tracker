# Changelog

All notable changes to the Research Tracker project will be documented in this file.

## [2.0.0] - 2025-12-07

### 🎯 Major Redesign: One Paper Per Day Architecture

#### Changed
- **Strategy Shift**: From bulk fetching (100 papers/day) to curated selection (1 paper/day)
- **Primary Source**: Switched from arXiv to Semantic Scholar (built-in citation data)
- **AI Engine**: Replaced Volcano Engine (火山方舟) with Azure OpenAI
- **Focus**: Quality over quantity - high-citation papers with actionable insights

#### Added
- ✅ **Phase 1 Complete**: Semantic Scholar integration with deduplication
  - `src/scrapers/semantic_scholar_scraper.py` - Citation-based paper fetching
  - `src/scheduler/daily_scheduler.py` - One paper per day automation
  - Deduplication by `paper_id` to prevent re-fetching

- 🚧 **Phase 2 Ready**: Azure OpenAI summarization
  - `src/processors/azure_summarizer.py` - Chinese summary + investment insights
  - `src/scheduler/process_papers.py` - Daily processing script
  - Structured prompts for consistent output quality

- 📋 **Phase 3 Planned**: Lark Bot publishing
  - Framework ready in `src/publishers/`

- 📚 **Documentation Overhaul**:
  - `README.md` - Complete rewrite with quick start guide
  - `ARCHITECTURE.md` - Comprehensive system design (10KB)
  - `CHANGELOG.md` - Version history tracking

- 🚀 **Deployment**:
  - `deployment/manage_scheduler.sh` - Service management for macOS
  - `deployment/com.researchtracker.scheduler.plist` - LaunchAgent config
  - Automated daily runs at UTC 00:00

- 🛠️ **Utilities**:
  - `scripts/show_papers.py` - View database contents
  - Database methods: `count_all()`, `count_unprocessed()`, `get_unprocessed()`

#### Removed
- ❌ **Test Scripts** (7 files):
  - `debug_arxiv.py`, `fetch_with_citations.py`, `quick_citation_test.py`
  - `quick_test.py`, `test_scraper.py`, `test_semantic_scholar.py`, `verify_citations.py`

- ❌ **Outdated Documentation** (4 files):
  - `CITATION_STRATEGY.md`, `AUTOMATION_COMPLETE.md`, `SCHEDULING.md`, `copilot.md`

- ❌ **Test Data**:
  - `data/latest_papers.json`, `data/top_cited_papers.json`
  - All `.DS_Store` files

- ❌ **Volcano Engine Integration**:
  - Removed all references to 火山方舟大模型
  - Replaced with Azure OpenAI configuration

#### Fixed
- **Citation Problem**: Previous approach fetched papers too new (0 citations)
  - Solution: Semantic Scholar provides papers with existing citations (50-669 range)
- **Database Schema**: Added `doi` field for better paper identification
- **Rate Limiting**: Implemented 3-second delays and 429 error handling for Semantic Scholar
- **.gitignore**: Cleaned up duplicates, added `data/*.json`, `data/*.db`

#### Technical Details
- **Database**: SQLite with `paper_id` unique constraint for deduplication
- **Keywords**: artificial intelligence, machine learning, deep learning, robotics
- **Fetch Strategy**: Top 100 papers by citations → filter duplicates → add 1 new paper
- **Token Cost**: ~$0.30/month (30 papers × ~1,900 tokens × GPT-4 pricing)
- **Runtime**: ~60 seconds per daily cycle (fetch + summarize + publish)

---

## [1.0.0] - 2025-12-06

### Initial Release

#### Added
- Basic arXiv scraper with multi-keyword support
- SQLite database with Paper model
- Virtual environment setup
- Git repository initialization
- Basic project structure (`src/`, `scripts/`, `tests/`, `data/`)

#### Features
- Fetch papers from arXiv API
- Store in local SQLite database
- Support for multiple research keywords
- Basic citation enrichment (attempted)

#### Known Issues
- arXiv API date filtering limitations
- Papers too new (0 citations)
- No deduplication mechanism
- Manual execution only (no automation)

---

## Version History

- **v2.0.0** (Current) - One Paper Per Day + Azure OpenAI
- **v1.0.0** - Initial arXiv scraper

---

## Roadmap

### Phase 2: AI Summarization (In Progress)
- [ ] Azure OpenAI credentials setup
- [ ] Test Chinese summary generation
- [ ] Test investment insights extraction
- [ ] Integrate into daily scheduler
- [ ] Error handling and retry logic

### Phase 3: Publishing (Planned)
- [ ] Lark Bot webhook integration
- [ ] Message card formatting
- [ ] Daily digest automation
- [ ] Mark papers as `published=True`

### Future Enhancements
- [ ] Multi-language support (English summaries)
- [ ] Topic clustering (NLP, CV, RL categories)
- [ ] Citation velocity tracking (hot topics)
- [ ] Author network analysis
- [ ] Company mention extraction
- [ ] Weekly trend digest
- [ ] User feedback integration

---

**Maintained by**: shuorenyuyu  
**Repository**: https://github.com/shuorenyuyu/research-tracker  
**License**: MIT
