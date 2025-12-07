#!/usr/bin/env python3
"""
Generate WeChat-formatted article from today's processed paper
Output: Markdown file ready to copy/paste to WeChat 公众号 editor
"""
import os
import sqlite3
from datetime import datetime


def generate_wechat_article():
    """Generate WeChat article from latest processed paper"""
    
    # Connect to database
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'papers.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get today's processed paper
    cursor.execute("""
        SELECT 
            title, authors, year, venue, citation_count,
            abstract, url, summary_zh, investment_insights,
            fetched_at
        FROM papers 
        WHERE processed = 1 
        ORDER BY fetched_at DESC 
        LIMIT 1
    """)
    
    result = cursor.fetchone()
    conn.close()
    
    if not result:
        print("❌ No processed papers found")
        return None
    
    paper = result
    
    # Format WeChat article
    article = f"""# 🔬 今日AI前沿论文解读

---

## 📄 论文信息

**标题：** {paper[0]}

**作者：** {paper[1]}

**发表：** {paper[3]} ({paper[2]})

**引用数：** {paper[4]} 次

**论文链接：** {paper[6]}

---

## 📖 深度解读

{paper[7]}

---

## 💰 投资视角

{paper[8]}

---

## 📌 原文摘要

{paper[5]}

---

> 💡 **关于本系列**
> 每日精选一篇高引用AI/机器人领域论文，提供中文深度解读和投资分析。
> 
> 📅 发布时间：{datetime.now().strftime('%Y年%m月%d日')}

---

**#AI前沿 #学术论文 #投资分析 #技术趋势**
"""
    
    # Save to file
    output_dir = "data/wechat_articles"
    os.makedirs(output_dir, exist_ok=True)
    
    today = datetime.now().strftime('%Y%m%d')
    output_file = f"{output_dir}/wechat_{today}.md"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(article)
    
    print(f"✅ WeChat article generated: {output_file}")
    print(f"\n📋 Preview (first 300 chars):\n{article[:300]}...\n")
    
    # Also save as HTML for rich formatting
    html_file = f"{output_dir}/wechat_{today}.html"
    html_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{paper[0]}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
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
            margin-bottom: 10px;
            border-left: 4px solid #007AFF;
            padding-left: 15px;
        }}
        h3 {{
            color: #34495e;
            margin-top: 18px;
            margin-bottom: 6px;
        }}
        h4 {{
            color: #555;
            margin-top: 8px;
            margin-bottom: 4px;
        }}
        h5 {{
            color: #666;
            margin-top: 6px;
            margin-bottom: 3px;
            font-size: 15px;
        }}
        .meta {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            margin: 15px 0;
        }}
        .meta p {{
            margin: 5px 0;
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
            line-height: 1.6;
        }}
        .content ul {{
            margin: 10px 0;
            padding-left: 20px;
        }}
        .abstract {{
            background: #f0f7ff;
            padding: 15px;
            border-left: 4px solid #007AFF;
            margin: 15px 0;
            font-style: italic;
        }}
        .footer {{
            margin-top: 25px;
            padding-top: 15px;
            border-top: 2px solid #eee;
            color: #666;
            font-size: 14px;
        }}
        .footer p {{
            margin: 6px 0;
        }}
        a {{
            color: #007AFF;
            text-decoration: none;
        }}
        a:hover {{
            text-decoration: underline;
        }}
        .tags {{
            margin-top: 20px;
        }}
        .tag {{
            display: inline-block;
            background: #007AFF;
            color: white;
            padding: 5px 15px;
            border-radius: 15px;
            margin: 5px;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🔬 今日AI前沿论文解读</h1>
        
        <div class="meta">
            <p><strong>📄 标题：</strong>{paper[0]}</p>
            <p><strong>👥 作者：</strong>{paper[1]}</p>
            <p><strong>📅 发表：</strong>{paper[3]} ({paper[2]})</p>
            <p><strong>📊 引用数：</strong>{paper[4]} 次</p>
            <p><strong>🔗 论文链接：</strong><a href="{paper[6]}" target="_blank">{paper[6]}</a></p>
        </div>
        
        <div class="content">
            <h2>📖 深度解读</h2>
            {_format_html_content(paper[7])}
            
            <h2>💰 投资视角</h2>
            {_format_html_content(paper[8])}
            
            <h2>📌 原文摘要</h2>
            <div class="abstract">
                {paper[5]}
            </div>
        </div>
        
        <div class="footer">
            <p>💡 <strong>关于本系列</strong></p>
            <p>每日精选一篇高引用AI/机器人领域论文，提供中文深度解读和投资分析。</p>
            <p>📅 发布时间：{datetime.now().strftime('%Y年%m月%d日')}</p>
            
            <div class="tags">
                <span class="tag">#AI前沿</span>
                <span class="tag">#学术论文</span>
                <span class="tag">#投资分析</span>
                <span class="tag">#技术趋势</span>
            </div>
        </div>
    </div>
</body>
</html>
"""
    
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ HTML version saved: {html_file}")
    print(f"\n🌐 You can open HTML in browser and copy formatted content to WeChat")
    
    return output_file


def _format_html_content(text):
    """Convert markdown-style content to HTML"""
    if not text:
        return ""
    
    # Simple markdown to HTML conversion
    lines = text.split('\n')
    html_lines = []
    
    for line in lines:
        if line.startswith('#### '):
            html_lines.append(f'<h5>{line[5:]}</h5>')
        elif line.startswith('### '):
            html_lines.append(f'<h4>{line[4:]}</h4>')
        elif line.startswith('## '):
            html_lines.append(f'<h3>{line[3:]}</h3>')
        elif line.startswith('- '):
            # Convert **bold** to <strong>
            formatted_line = line[2:].replace('**', '<strong>', 1).replace('**', '</strong>', 1)
            # Handle multiple bold sections
            while '**' in formatted_line:
                formatted_line = formatted_line.replace('**', '<strong>', 1).replace('**', '</strong>', 1)
            html_lines.append(f'<li>{formatted_line}</li>')
        elif line.strip():
            # Convert **bold** to <strong> in paragraphs
            formatted_line = line
            while '**' in formatted_line:
                formatted_line = formatted_line.replace('**', '<strong>', 1).replace('**', '</strong>', 1)
            html_lines.append(f'<p>{formatted_line}</p>')
        # Skip empty lines - no <br> tags
    
    return '\n'.join(html_lines)


if __name__ == '__main__':
    generate_wechat_article()
