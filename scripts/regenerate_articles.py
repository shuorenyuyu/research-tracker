#!/usr/bin/env python3
"""
Regenerate WeChat articles (both MD and HTML) for specific dates
"""
import sys
import os
import sqlite3
from datetime import datetime, timedelta

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Title mapping for well-known papers
TITLE_MAPPING = {
    "GPT-4": "GPT-4技术报告：多模态大模型的新突破",
    "LLaMA": "LLaMA：开源高效的基础语言模型",
    "Visual Instruction": "视觉指令微调：多模态AI的新范式",
    "Segment Anything": "Segment Anything：通用图像分割的革命性突破",
    "Constitutional AI": "宪法AI：通过AI反馈实现无害化",
    "Tree of Thoughts": "思维树：大模型的深思熟虑式问题解决",
    "RLHF": "人类反馈强化学习：让AI更懂人类意图",
    "Transformer": "Transformer：注意力机制颠覆深度学习",
    "Attention Is All You Need": "Attention机制：改变AI的关键突破"
}

def get_article_title(paper_title):
    """Generate engaging title based on paper title"""
    for key, title in TITLE_MAPPING.items():
        if key.lower() in paper_title.lower():
            return title
    
    # Fallback
    if len(paper_title) > 30:
        return f"{paper_title[:30]}...：AI前沿研究解读"
    else:
        return f"{paper_title}：AI前沿研究解读"

def format_html_content(content):
    """Convert markdown-style content to HTML"""
    if not content:
        return ""
    
    lines = content.strip().split('\n')
    html_lines = []
    in_list = False
    in_glossary = False
    
    for line in lines:
        # Check for glossary section
        if '术语速查' in line and line.startswith('###'):
            html_lines.append('<div class="glossary">')
            html_lines.append('<h4>📚 术语速查</h4>')
            html_lines.append('<ul>')
            in_glossary = True
            in_list = True
            continue
        
        # Handle headings
        if line.startswith('## '):
            if in_list:
                html_lines.append('</ul>')
                if in_glossary:
                    html_lines.append('</div>')
                    in_glossary = False
                in_list = False
            html_lines.append(f'<h3>{line[3:]}</h3>')
        elif line.startswith('### '):
            if in_list:
                html_lines.append('</ul>')
                if in_glossary:
                    html_lines.append('</div>')
                    in_glossary = False
                in_list = False
            html_lines.append(f'<h4>{line[4:]}</h4>')
        elif line.startswith('- '):
            if not in_list:
                if not in_glossary:
                    html_lines.append('<ul>')
                in_list = True
            formatted_line = line[2:]
            formatted_line = convert_bold(formatted_line)
            html_lines.append(f'<li>{formatted_line}</li>')
        elif line.strip() and not line.strip().startswith('---'):
            if in_list and not in_glossary:
                html_lines.append('</ul>')
                in_list = False
            formatted_line = convert_bold(line)
            html_lines.append(f'<p>{formatted_line}</p>')
    
    if in_list:
        html_lines.append('</ul>')
        if in_glossary:
            html_lines.append('</div>')
    
    return '\n'.join(html_lines)

def convert_bold(text):
    """Convert markdown **bold** to HTML <strong> tags"""
    result = text
    while '**' in result:
        result = result.replace('**', '<strong>', 1).replace('**', '</strong>', 1)
    return result

def generate_articles_for_date(target_date, output_dir="data/wechat_articles"):
    """Generate both MD and HTML articles for a specific date"""
    
    db_path = "data/papers.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            title, authors, year, venue, citation_count,
            abstract, url, summary_zh, investment_insights,
            fetched_at
        FROM papers 
        WHERE processed = 1 
        AND DATE(fetched_at) = ?
        LIMIT 1
    """, (target_date,))
    
    result = cursor.fetchone()
    conn.close()
    
    if not result:
        print(f"❌ No paper found for {target_date}")
        return False
    
    # Extract paper data
    title, authors, year, venue, citation_count, abstract, url, summary_zh, investment_insights, fetched_at = result
    
    # Generate article title
    article_title = get_article_title(title)
    
    # Parse date
    try:
        fetch_date = datetime.fromisoformat(str(fetched_at).split(".")[0])
        date_str = fetch_date.strftime("%Y年%m月%d日")
        output_date = fetch_date.strftime("%Y%m%d")
    except:
        parts = target_date.split('-')
        date_str = f"{parts[0]}年{parts[1]}月{parts[2]}日"
        output_date = target_date.replace("-", "")
    
    # Generate Markdown
    markdown = f"""# 🔬 {article_title}

> 📅 {date_str} | 📊 {citation_count} 次引用 | 🏛️ {venue}

---

## 📄 论文信息

**标题：** {title}

**作者：** {authors}

**发表：** {venue} ({year})

**引用数：** {citation_count} 次

**论文链接：** {url}

---

## 📖 深度解读

{summary_zh}

---

## 💰 投资视角

{investment_insights or "暂无投资分析"}

---

*本文基于AI自动分析生成，仅供参考*
"""
    
    # Generate HTML
    summary_html = format_html_content(summary_zh)
    insights_html = format_html_content(investment_insights or "")
    
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{article_title}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", sans-serif;
            line-height: 1.6;
            max-width: 800px;
            margin: 40px auto;
            padding: 20px;
            color: #333;
            background: #f5f5f5;
        }}
        .container {{
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #1a1a1a;
            border-bottom: 3px solid #007AFF;
            padding-bottom: 10px;
            margin-bottom: 15px;
        }}
        h2 {{
            color: #2c3e50;
            margin-top: 25px;
            border-left: 4px solid #007AFF;
            padding-left: 15px;
        }}
        h3 {{
            color: #34495e;
            margin-top: 18px;
        }}
        h4 {{
            color: #555;
            margin-top: 12px;
        }}
        .meta {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            margin: 15px 0;
            font-size: 14px;
            color: #666;
        }}
        .paper-info {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            margin: 15px 0;
        }}
        .paper-info p {{
            margin: 8px 0;
        }}
        .content {{
            font-size: 16px;
            line-height: 1.7;
        }}
        .content p {{
            margin: 8px 0;
        }}
        .content li {{
            margin: 6px 0;
        }}
        .content ul {{
            margin: 10px 0;
            padding-left: 20px;
        }}
        .glossary {{
            background: #fff9e6;
            padding: 15px 20px;
            border-radius: 8px;
            margin: 20px 0;
            border-left: 4px solid #ffa500;
        }}
        .glossary h4 {{
            color: #d97706;
            margin-top: 0;
        }}
        .glossary ul {{
            list-style: none;
            padding-left: 0;
        }}
        .glossary li {{
            margin: 8px 0;
            padding-left: 20px;
            position: relative;
        }}
        .glossary li:before {{
            content: "📌";
            position: absolute;
            left: 0;
        }}
        a {{
            color: #007AFF;
            text-decoration: none;
        }}
        a:hover {{
            text-decoration: underline;
        }}
        .footer {{
            margin-top: 25px;
            padding-top: 15px;
            border-top: 2px solid #eee;
            color: #666;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🔬 {article_title}</h1>
        
        <div class="meta">
            📅 {date_str} | 📊 {citation_count} 次引用 | 🏛️ {venue}
        </div>
        
        <div class="paper-info">
            <h2>📄 论文信息</h2>
            <p><strong>标题：</strong>{title}</p>
            <p><strong>作者：</strong>{authors}</p>
            <p><strong>发表：</strong>{venue} ({year})</p>
            <p><strong>引用数：</strong>{citation_count} 次</p>
            <p><strong>论文链接：</strong><a href="{url}" target="_blank">{url}</a></p>
        </div>
        
        <div class="content">
            <h2>📖 深度解读</h2>
            {summary_html}
            
            <h2>💰 投资视角</h2>
            {insights_html or "<p>暂无投资分析</p>"}
        </div>
        
        <div class="footer">
            <p><em>本文基于AI自动分析生成，仅供参考</em></p>
        </div>
    </div>
</body>
</html>
"""
    
    # Save files
    os.makedirs(output_dir, exist_ok=True)
    
    md_file = os.path.join(output_dir, f"wechat_{output_date}.md")
    html_file = os.path.join(output_dir, f"wechat_{output_date}.html")
    
    with open(md_file, "w", encoding="utf-8") as f:
        f.write(markdown)
    
    with open(html_file, "w", encoding="utf-8") as f:
        f.write(html)
    
    return article_title, output_date

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Regenerate WeChat articles for specific dates')
    parser.add_argument('--date', help='Target date (YYYY-MM-DD)')
    parser.add_argument('--range', help='Date range (e.g., 2025-12-01:2025-12-07)')
    
    args = parser.parse_args()
    
    if args.range:
        # Parse range
        start_str, end_str = args.range.split(':')
        start = datetime.strptime(start_str, '%Y-%m-%d')
        end = datetime.strptime(end_str, '%Y-%m-%d')
        
        current = start
        count = 0
        while current <= end:
            date_str = current.strftime('%Y-%m-%d')
            result = generate_articles_for_date(date_str)
            if result:
                title, output_date = result
                print(f"✅ {date_str}: {title}")
                count += 1
            current += timedelta(days=1)
        
        print(f"\n✅ Regenerated {count} articles!")
    
    elif args.date:
        result = generate_articles_for_date(args.date)
        if result:
            title, output_date = result
            print(f"✅ Generated: {title}")
            print(f"   Files: wechat_{output_date}.md, wechat_{output_date}.html")
    
    else:
        # Default: regenerate Dec 1-7
        print("Regenerating articles for Dec 1-7, 2025...\n")
        for day in range(1, 8):
            date_str = f"2025-12-0{day}"
            result = generate_articles_for_date(date_str)
            if result:
                title, _ = result
                print(f"✅ Dec {day}: {title}")
        print(f"\n✅ All articles regenerated!")

if __name__ == '__main__':
    main()
