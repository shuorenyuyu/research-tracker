# Research Tracker 📚🤖

> Automated research paper tracking system for AI, Robotics, New Energy, Biotechnology, and emerging technology investment research

An intelligent system that **fetches one high-quality research paper daily**, generates Chinese summaries with Azure OpenAI, and provides investment insights. Designed for investors who want to stay informed about cutting-edge technologies without information overload.

## 🎯 Philosophy: Quality Over Quantity

Instead of drowning in 100+ papers daily, we deliver **one carefully selected paper per day**:
- ✅ Ranked by **citation count** (community validation)
- ✅ Filtered by **AI/Robotics/ML keywords**
- ✅ **Deduplicated** (never see the same paper twice)
- ✅ **Chinese summary** + investment insights
- ✅ Runs **fully automated** at UTC 00:00

## 🏗️ Architecture

### Phase 1: Data Collection (✅ Complete)
**Source**: Semantic Scholar API (provides built-in citation data)
- Fetches top 100 papers by citations from **recent one year** (ensures papers have time to accumulate citations)
- Filters for **AI/ML/Robotics + New Energy/Battery + Biotechnology/Gene Editing + Quantum Computing** and other emerging tech keywords
- Stores ONE new paper per day (highest citations)
- Deduplication prevents re-fetching

### Phase 2: AI Summarization (🚧 In Progress)
**Engine**: Azure OpenAI (GPT-4)
- Generates **Chinese summaries** (800-1500 characters)
- Extracts **investment insights** (200-400 characters) with specific industry/company names
- Analyzes: tech maturity, commercialization potential, related industries across AI, new energy, biotech, and emerging fields
- Processes one unprocessed paper daily
- Exports to WeChat-formatted articles for manual publishing

## 🚀 Quick Start

### 1. Clone & Setup
```bash
git clone git@github.com:shuorenyuyu/research-tracker.git
cd research-tracker
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env with your Azure OpenAI credentials:
# - AZURE_OPENAI_ENDPOINT
# - AZURE_OPENAI_API_KEY
# - AZURE_OPENAI_DEPLOYMENT_NAME
```

### 3. Run Daily Fetch (One Paper)
```bash
# Manual test (fetches one paper)
python3 src/scheduler/daily_scheduler.py --run-once

# Check what was fetched
python3 scripts/show_papers.py
```

### 4. Process with Azure OpenAI
```bash
# Summarize the unprocessed paper
python3 src/scheduler/process_papers.py --one
```

### 5. Deploy as Background Service (macOS)
```bash
# Install LaunchAgent (runs at UTC 00:00 daily)
./deployment/manage_scheduler.sh install

# Check status
./deployment/manage_scheduler.sh status

# View logs
./deployment/manage_scheduler.sh logs
```

## 📊 Database Schema

**papers.db** (SQLite):
- `paper_id` - Unique identifier (deduplication key)
- `title`, `authors`, `abstract`, `year`, `venue`
- `citation_count` - Semantic Scholar citations
- `summary_zh` - Chinese summary (Azure OpenAI)
- `investment_insights` - Investment analysis (Azure OpenAI)
- `processed` - Boolean flag for AI processing
- `published` - Boolean flag for export tracking

## 🛠️ Project Structure

```
research-tracker/
├── src/
│   ├── config/          # Settings & environment
│   ├── database/        # SQLAlchemy models & repository
│   ├── scrapers/        # Semantic Scholar API client
│   ├── processors/      # Azure OpenAI summarizer
│   └── scheduler/       # Daily automation scripts
├── scripts/             # Utility scripts
│   ├── show_papers.py   # View database contents
│   └── daily_fetch.py   # Legacy manual fetch
├── deployment/          # macOS LaunchAgent config
├── data/                # SQLite database & logs
└── tests/               # Unit tests
```

## 📖 How It Works

### Daily Workflow
1. **00:00 UTC** - Scheduler wakes up
2. **Fetch** - Query Semantic Scholar for top 100 papers by citations
3. **Filter** - Check against database for duplicates
4. **Store** - Add highest-citation new paper to database
5. **Summarize** - Azure OpenAI generates Chinese summary + insights
6. **Export** - Generate WeChat-formatted article (manual publishing)

### Deduplication Strategy
- Each paper has a unique `paper_id` (from Semantic Scholar)
- Before adding, check if `paper_id` exists in database
- Only add if it's a new paper
- Result: **Never fetch the same paper twice**

## 🔑 Key Features

### Citation-Based Ranking
Papers sorted by **citation count** (not recency):
- High citations = community validation
- Proven research with measurable impact
- Better signal for investment decisions

### Semantic Scholar Integration
- Free API (100 requests / 5 minutes)
- Built-in citation data (no extra enrichment needed)
- Comprehensive metadata (authors, venue, year, DOI)

### Azure OpenAI Summarization
- **Chinese summaries** tailored for Chinese-speaking investors
- **Investment insights** analyze commercialization potential
- Structured prompts ensure consistent output quality

## 📝 Example Output

**Paper**: "Attention Is All You Need"  
**Citations**: 114,000+  
**中文摘要**: 本文提出了Transformer架构，完全基于注意力机制，摒弃了传统的循环神经网络。该模型在机器翻译任务上取得了突破性成果，训练速度显著提升...  
**投资洞察**: 技术成熟度：应用就绪。商业化潜力：已广泛应用于ChatGPT等产品。相关行业：AI芯片(NVIDIA)、云计算(Microsoft Azure)、大模型创业公司。投资建议：关注Transformer衍生技术的商业化落地...

## 🤝 Contributing

This is a personal investment research tool. Feel free to fork and adapt for your own use.

## 📄 License

MIT License
