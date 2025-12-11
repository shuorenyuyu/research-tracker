# Custom Theme Search - User Guide

## Overview
Search for research papers on **any topic** you choose and get AI-generated summaries focused on your specific interests.

## Features
- ✅ **Custom Keywords**: Search with any keywords you want
- ✅ **Automatic Fallback**: Uses Semantic Scholar → OpenAlex if blocked
- ✅ **AI Summaries**: Chinese summaries with investment insights (if Azure OpenAI configured)
- ✅ **Themed Reports**: Comprehensive analysis combining multiple papers
- ✅ **Focus Areas**: Specify particular aspects to emphasize
- ✅ **Flexible Output**: Save to file or print to console

## Quick Start

### Basic Usage
```bash
# Search for quantum computing papers
python3 scripts/custom_theme_search.py --keywords "quantum computing"
```

### Search Multiple Keywords
```bash
python3 scripts/custom_theme_search.py \
  --keywords "AI healthcare" "medical diagnosis" "deep learning"
```

### Custom Theme and Focus
```bash
python3 scripts/custom_theme_search.py \
  --keywords "robotics" "autonomous vehicles" \
  --theme "自动驾驶机器人的发展" \
  --focus "安全性" "成本" "法规"
```

### Limit Papers and Year Range
```bash
python3 scripts/custom_theme_search.py \
  --keywords "new energy" "solar cells" \
  --max-papers 3 \
  --year 2023-
```

## Command Options

```
--keywords, -k      Keywords to search (required, space-separated)
--theme, -t         Theme/topic for report (default: first keyword)
--focus, -f         Specific focus areas (optional, space-separated)
--max-papers, -m    Maximum papers to analyze (default: 5)
--year, -y          Year filter (e.g., "2024-", default: 2024-)
--no-save           Don't save report (only print to console)
```

## Examples

### 1. Biotech Research
```bash
python3 scripts/custom_theme_search.py \
  --keywords "CRISPR" "gene editing" "biotechnology" \
  --theme "基因编辑技术在医疗中的应用" \
  --max-papers 5
```

**Output**: Report saved to `data/themed_reports/基因编辑技术在医疗中的应用_20251212_013500.md`

### 2. New Energy Focus
```bash
python3 scripts/custom_theme_search.py \
  --keywords "lithium battery" "solid state battery" \
  --focus "能量密度" "安全性" "成本" \
  --max-papers 3
```

### 3. Quick Preview (No Save)
```bash
python3 scripts/custom_theme_search.py \
  --keywords "large language models" \
  --max-papers 2 \
  --no-save
```

## Output Format

### Report Structure
```markdown
# [Theme] - 主题研究报告

**生成时间**: 2025-12-12T01:35:00
**分析论文数**: 5篇

---

## 综合分析

[AI-generated comprehensive overview covering:]
1. 主题概述 - Current trends and research directions
2. 技术进展 - Key breakthroughs and innovations
3. 应用场景 - Practical applications
4. 投资价值分析 - Investment opportunities
5. 未来展望 - Future trends

---

## 详细论文分析

### 1. [Paper Title]
**作者**: Authors
**年份**: 2024
**引用数**: 500
**链接**: https://...

#### 研究摘要
[Chinese summary]

#### 投资洞察
[Investment insights]

[... repeat for each paper ...]
```

## How It Works

```
User Input Keywords
        ↓
[1/3] Search APIs (Semantic Scholar → OpenAlex fallback)
        ↓
   Find papers sorted by citations
        ↓
[2/3] Generate AI Summaries
        ↓
   Individual paper summaries
   + Comprehensive themed overview
        ↓
[3/3] Save Report
        ↓
   Markdown file in data/themed_reports/
```

## Sample Session

```bash
$ python3 scripts/custom_theme_search.py \
    --keywords "quantum computing" \
    --max-papers 2

================================================================================
主题搜索: quantum computing
关键词: quantum computing
年份过滤: 2024-
最大论文数: 2
================================================================================

[1/3] 搜索相关论文...
✓ Semantic Scholar: Found 2 papers
✓ 找到 2 篇论文
  1. Quantum computing with Qiskit... (引用: 549)
  2. Barren plateaus in variational quantum computing... (引用: 293)

[2/3] 生成主题分析报告...
✓ 报告生成完成

[3/3] 保存报告...
✓ 报告已保存: data/themed_reports/quantum_computing_20251212_013344.md

================================================================================
综合分析预览
================================================================================
# quantum computing 综合分析

基于 2 篇高引用论文的分析：
...
================================================================================
```

## Tips

### Best Practices
1. **Use specific keywords**: "quantum error correction" better than "quantum"
2. **Combine keywords**: Multiple keywords find more diverse papers
3. **Set appropriate max-papers**: 3-5 papers for quick overview, 10+ for deep dive
4. **Use focus areas**: Guide AI to emphasize specific aspects

### Keyword Suggestions

**AI/ML**:
- "large language models", "GPT", "transformer architecture"
- "reinforcement learning", "computer vision", "deep learning"

**Robotics**:
- "autonomous systems", "robot navigation", "robotic manipulation"
- "humanoid robots", "drone technology"

**New Energy**:
- "lithium battery", "solar cells", "hydrogen fuel"
- "energy storage", "renewable energy"

**Biotech**:
- "CRISPR", "gene therapy", "mRNA vaccines"
- "protein folding", "drug discovery"

**Quantum Computing**:
- "quantum algorithms", "quantum error correction"
- "quantum supremacy", "quantum cryptography"

## Integration with Daily Tracker

This tool complements the daily automated tracker:

| Feature | Daily Tracker | Custom Theme Search |
|---------|---------------|---------------------|
| Keywords | Fixed (AI, ML, Robotics) | **User-defined (any topic)** |
| Papers | 1 per day | **1-20 per search** |
| Schedule | Automated daily | **On-demand** |
| Use Case | Continuous monitoring | **Deep dive on specific topic** |

## Troubleshooting

**Problem**: "No papers found"
- **Solution**: Try broader keywords or remove year filter

**Problem**: "Azure OpenAI not available"
- **Solution**: Configure `.env` with Azure credentials, or use `--no-save` for basic search

**Problem**: "Both APIs failed"
- **Solution**: Check network connection, try again later

## Cost

- **Paper Search**: 100% FREE (OpenAlex + Semantic Scholar)
- **AI Summaries**: ~$0.02 per paper (Azure OpenAI GPT-4)
- **Example**: 5-paper report = ~$0.10

## Files Created

Reports saved to: `data/themed_reports/[theme]_[timestamp].md`

Example:
```
data/themed_reports/
├── 量子计算_20251212_013344.md
├── AI医疗诊断_20251212_015520.md
└── 自动驾驶机器人_20251212_020103.md
```

## Next Steps

1. **Try it**: Start with a topic you're interested in
2. **Experiment**: Test different keywords and focus areas
3. **Share**: Export reports for your team or blog
4. **Automate**: Schedule regular themed searches with cron

