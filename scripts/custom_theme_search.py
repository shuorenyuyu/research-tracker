"""
Custom Theme Search - Generate summaries based on user-provided keywords
Allows users to search for papers on specific topics and get AI summaries
"""

import sys
import argparse
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.logger import setup_logger
from src.scrapers.semantic_scholar_scraper import SemanticScholarScraper
from src.scrapers.openalex_scraper import OpenAlexScraper
from src.database.repository import PaperRepository
from src.config.settings import Settings

# Try to import Azure summarizer, fallback to manual implementation
try:
    from src.processors.azure_summarizer import AzureSummarizer
    AZURE_AVAILABLE = True
except ImportError:
    AZURE_AVAILABLE = False
    print("Warning: AzureSummarizer not available, using fallback implementation")


class CustomThemeSearch:
    """Search and summarize papers based on user-provided themes"""
    
    def __init__(self):
        self.logger = setup_logger("custom_theme")
        self.paper_repo = PaperRepository()
        
        # Initialize scrapers with fallback
        ss_api_key = Settings.SEMANTIC_SCHOLAR_API_KEY or None
        self.ss_scraper = SemanticScholarScraper(
            self.logger, 
            rate_limit_delay=3,
            api_key=ss_api_key
        )
        self.openalex_scraper = OpenAlexScraper(self.logger, rate_limit_delay=1)
        
        # Initialize AI summarizer
        if AZURE_AVAILABLE:
            self.summarizer = AzureSummarizer()
        else:
            self.summarizer = None
            self.logger.warning("Azure summarizer not available - summaries will be limited")
    
    def search_by_theme(self, theme_keywords: list, max_papers: int = 5, 
                       year_filter: str = "2024-") -> list:
        """
        Search for papers matching theme keywords
        
        Args:
            theme_keywords: List of keywords (e.g., ['quantum computing', 'machine learning'])
            max_papers: Maximum papers to retrieve
            year_filter: Year filter (e.g., '2024-' for 2024 onwards)
            
        Returns:
            List of papers sorted by citations
        """
        self.logger.info(f"Searching for theme: {', '.join(theme_keywords)}")
        
        papers = []
        
        # Try each keyword
        for keyword in theme_keywords:
            self.logger.info(f"Searching with keyword: '{keyword}'")
            
            # Try Semantic Scholar first
            try:
                keyword_papers = self.ss_scraper.search(
                    query=keyword,
                    max_results=max_papers,
                    year_filter=year_filter
                )
                
                if keyword_papers:
                    papers.extend(keyword_papers)
                    self.logger.info(f"✓ Semantic Scholar: Found {len(keyword_papers)} papers")
                    continue
            except Exception as e:
                self.logger.warning(f"Semantic Scholar failed: {e}")
            
            # Fallback to OpenAlex
            try:
                keyword_papers = self.openalex_scraper.search(
                    query=keyword,
                    max_results=max_papers,
                    year_filter=year_filter
                )
                
                if keyword_papers:
                    papers.extend(keyword_papers)
                    self.logger.info(f"✓ OpenAlex: Found {len(keyword_papers)} papers")
            except Exception as e:
                self.logger.error(f"Both APIs failed for '{keyword}': {e}")
        
        # Remove duplicates by paper_id
        seen_ids = set()
        unique_papers = []
        for paper in papers:
            pid = paper.get('paper_id')
            if pid and pid not in seen_ids:
                seen_ids.add(pid)
                unique_papers.append(paper)
        
        # Sort by citations
        unique_papers.sort(key=lambda p: p.get('citation_count', 0), reverse=True)
        
        self.logger.info(f"Total unique papers found: {len(unique_papers)}")
        return unique_papers[:max_papers]
    
    def generate_themed_summary(self, papers: list, theme: str, 
                                focus_areas: list = None) -> dict:
        """
        Generate a themed summary across multiple papers
        
        Args:
            papers: List of paper dictionaries
            theme: Main theme/topic (e.g., "Quantum Computing in Drug Discovery")
            focus_areas: Specific aspects to focus on (optional)
            
        Returns:
            Dictionary with themed summary and individual paper summaries
        """
        if not papers:
            self.logger.warning("No papers to summarize")
            return None
        
        self.logger.info(f"Generating themed summary for: '{theme}'")
        self.logger.info(f"Analyzing {len(papers)} papers...")
        
        # Generate individual summaries
        paper_summaries = []
        for i, paper in enumerate(papers, 1):
            self.logger.info(f"[{i}/{len(papers)}] Summarizing: {paper['title'][:60]}...")
            
            try:
                if self.summarizer:
                    summary = self.summarizer.generate_summary(paper)
                    insights = self.summarizer.generate_investment_insights(paper)
                else:
                    # Fallback: use abstract as summary
                    summary = paper.get('abstract', 'No summary available')
                    insights = "Azure OpenAI not configured - investment insights unavailable"
                
                paper_summaries.append({
                    'title': paper['title'],
                    'authors': paper.get('authors', 'Unknown'),
                    'year': paper.get('year'),
                    'citations': paper.get('citation_count', 0),
                    'summary': summary,
                    'insights': insights,
                    'url': paper.get('url'),
                    'pdf_url': paper.get('pdf_url')
                })
            except Exception as e:
                self.logger.error(f"Failed to summarize paper: {e}")
                continue
        
        # Generate comprehensive themed overview
        self.logger.info("Generating comprehensive themed overview...")
        overview = self._generate_themed_overview(theme, paper_summaries, focus_areas)
        
        return {
            'theme': theme,
            'focus_areas': focus_areas or [],
            'paper_count': len(paper_summaries),
            'overview': overview,
            'papers': paper_summaries,
            'generated_at': datetime.now().isoformat()
        }
    
    def _generate_themed_overview(self, theme: str, paper_summaries: list, 
                                  focus_areas: list = None) -> str:
        """
        Generate a comprehensive overview combining insights from all papers
        
        Args:
            theme: Main theme
            paper_summaries: List of paper summaries
            focus_areas: Specific aspects to emphasize
            
        Returns:
            Comprehensive themed overview in Chinese
        """
        # Combine all summaries for context
        combined_context = "\n\n".join([
            f"论文{i+1}: {ps['title']}\n摘要: {ps['summary'][:300]}..."
            for i, ps in enumerate(paper_summaries)
        ])
        
        # Build prompt for comprehensive overview
        focus_text = ""
        if focus_areas:
            focus_text = f"\n请特别关注以下方面：\n" + "\n".join([f"- {area}" for area in focus_areas])
        
        prompt = f"""你是一位资深的AI研究分析师和投资顾问。请基于以下{len(paper_summaries)}篇研究论文，生成一份关于"{theme}"的综合分析报告。

研究论文摘要：
{combined_context}
{focus_text}

请用中文生成一份1500-2000字的综合报告，包括：

1. **主题概述** (200字)
   - {theme}领域的当前研究趋势
   - 主要研究方向和热点

2. **技术进展** (500字)
   - 关键技术突破和创新点
   - 跨论文的共性技术和差异化方法
   - 技术成熟度评估

3. **应用场景** (400字)
   - 实际应用案例和潜在应用
   - 行业落地可行性
   - 商业化前景

4. **投资价值分析** (400字)
   - 投资机会和方向
   - 风险评估
   - 相关企业和领域
   - 投资时间窗口

5. **未来展望** (300字)
   - 技术发展趋势
   - 潜在研究方向
   - 行业影响预测

请用专业、客观的语言，确保分析有深度且具有实际参考价值。"""
        
        try:
            # Try to use AzureSummarizer's existing client if available
            if self.summarizer and hasattr(self.summarizer, 'client'):
                response = self.summarizer.client.chat.completions.create(
                    model=self.summarizer.deployment,
                    messages=[
                        {"role": "system", "content": "你是专业的AI研究分析师和投资顾问"},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=2500
                )
                
                overview = response.choices[0].message.content
                self.logger.info(f"Generated themed overview ({len(overview)} characters)")
                return overview
            else:
                # Fallback: combine individual summaries
                overview = f"# {theme} 综合分析\n\n"
                overview += f"基于 {len(paper_summaries)} 篇高引用论文的分析：\n\n"
                
                for i, ps in enumerate(paper_summaries, 1):
                    overview += f"## 论文 {i}: {ps['title']}\n\n"
                    overview += f"{ps['summary'][:500]}...\n\n"
                
                self.logger.info("Generated basic overview (Azure OpenAI not available)")
                return overview
            
        except Exception as e:
            self.logger.error(f"Failed to generate themed overview: {e}")
            return f"无法生成综合概述：{str(e)}"
    
    def save_themed_report(self, result: dict, output_dir: Path = None):
        """
        Save themed report to file
        
        Args:
            result: Result dictionary from generate_themed_summary
            output_dir: Output directory (default: data/themed_reports/)
        """
        if not output_dir:
            output_dir = Settings.DATA_DIR / "themed_reports"
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate filename from theme
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_theme = "".join(c if c.isalnum() or c in (' ', '_') else '_' for c in result['theme'])
        filename = f"{safe_theme}_{timestamp}.md"
        filepath = output_dir / filename
        
        # Build markdown report
        content = f"""# {result['theme']} - 主题研究报告

**生成时间**: {result['generated_at']}  
**分析论文数**: {result['paper_count']}篇  

---

## 综合分析

{result['overview']}

---

## 详细论文分析

"""
        
        for i, paper in enumerate(result['papers'], 1):
            content += f"""
### {i}. {paper['title']}

**作者**: {paper['authors']}  
**年份**: {paper['year']}  
**引用数**: {paper['citations']}  
**链接**: {paper.get('url', 'N/A')}  
{f"**PDF**: {paper['pdf_url']}" if paper.get('pdf_url') else ''}

#### 研究摘要

{paper['summary']}

#### 投资洞察

{paper['insights']}

---
"""
        
        # Save to file
        filepath.write_text(content, encoding='utf-8')
        self.logger.info(f"Themed report saved to: {filepath}")
        
        return filepath


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Search and generate themed summaries based on custom keywords",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Search for quantum computing papers
  python scripts/custom_theme_search.py --keywords "quantum computing" "quantum algorithms"
  
  # Search with specific theme and focus areas
  python scripts/custom_theme_search.py \\
    --keywords "AI healthcare" "medical diagnosis" \\
    --theme "AI在医疗诊断中的应用" \\
    --focus "准确率" "成本效益" "监管合规"
  
  # Limit to 3 papers from 2023 onwards
  python scripts/custom_theme_search.py \\
    --keywords "robotics" "autonomous systems" \\
    --max-papers 3 \\
    --year 2023-
        """
    )
    
    parser.add_argument(
        '--keywords', '-k',
        nargs='+',
        required=True,
        help='Keywords to search for (space-separated)'
    )
    
    parser.add_argument(
        '--theme', '-t',
        help='Theme/topic for the report (default: first keyword)'
    )
    
    parser.add_argument(
        '--focus', '-f',
        nargs='*',
        help='Specific focus areas for analysis (optional)'
    )
    
    parser.add_argument(
        '--max-papers', '-m',
        type=int,
        default=5,
        help='Maximum number of papers to analyze (default: 5)'
    )
    
    parser.add_argument(
        '--year', '-y',
        default='2024-',
        help='Year filter (e.g., "2024-" or "2023-2024", default: 2024-)'
    )
    
    parser.add_argument(
        '--no-save',
        action='store_true',
        help='Do not save report to file (only print to console)'
    )
    
    args = parser.parse_args()
    
    # Initialize theme search
    theme_search = CustomThemeSearch()
    
    # Determine theme
    theme = args.theme or args.keywords[0]
    
    print("=" * 80)
    print(f"主题搜索: {theme}")
    print(f"关键词: {', '.join(args.keywords)}")
    print(f"年份过滤: {args.year}")
    print(f"最大论文数: {args.max_papers}")
    print("=" * 80)
    
    # Search for papers
    print("\n[1/3] 搜索相关论文...")
    papers = theme_search.search_by_theme(
        theme_keywords=args.keywords,
        max_papers=args.max_papers,
        year_filter=args.year
    )
    
    if not papers:
        print("\n❌ 未找到相关论文")
        return
    
    print(f"\n✓ 找到 {len(papers)} 篇论文")
    for i, paper in enumerate(papers, 1):
        print(f"  {i}. {paper['title'][:60]}... (引用: {paper.get('citation_count', 0)})")
    
    # Generate themed summary
    print(f"\n[2/3] 生成主题分析报告...")
    result = theme_search.generate_themed_summary(
        papers=papers,
        theme=theme,
        focus_areas=args.focus
    )
    
    if not result:
        print("\n❌ 生成报告失败")
        return
    
    print(f"\n✓ 报告生成完成")
    
    # Save report
    if not args.no_save:
        print(f"\n[3/3] 保存报告...")
        filepath = theme_search.save_themed_report(result)
        print(f"\n✓ 报告已保存: {filepath}")
    else:
        print("\n[3/3] 跳过保存 (--no-save)")
    
    # Print summary
    print("\n" + "=" * 80)
    print("综合分析预览")
    print("=" * 80)
    print(result['overview'][:500] + "...\n")
    print(f"完整报告包含 {result['paper_count']} 篇论文的详细分析")
    print("=" * 80)


if __name__ == "__main__":
    main()
