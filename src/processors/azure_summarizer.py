"""
Azure OpenAI-based paper summarizer
Generates Chinese summaries and investment insights
"""
import os
import logging
from typing import Dict, Optional
from openai import AzureOpenAI

from ..config.settings import Settings

logger = logging.getLogger(__name__)


class AzureSummarizer:
    """Generates summaries and insights using Azure OpenAI"""
    
    def __init__(self):
        """Initialize Azure OpenAI client"""
        self.endpoint = Settings.AZURE_OPENAI_ENDPOINT
        self.api_key = Settings.AZURE_OPENAI_API_KEY
        self.deployment = Settings.AZURE_OPENAI_DEPLOYMENT_NAME
        self.api_version = Settings.AZURE_OPENAI_API_VERSION
        
        if not self.endpoint or not self.api_key:
            raise ValueError(
                "Azure OpenAI credentials not configured. "
                "Please set AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_KEY in .env"
            )
        
        self.client = AzureOpenAI(
            azure_endpoint=self.endpoint,
            api_key=self.api_key,
            api_version=self.api_version
        )
        
        logger.info(f"Azure OpenAI client initialized (deployment: {self.deployment})")
    
    def generate_summary(self, paper: Dict) -> Optional[str]:
        """
        Generate Chinese summary for a research paper
        
        Args:
            paper: Dictionary containing paper metadata (title, abstract, authors, etc.)
        
        Returns:
            Chinese summary string, or None if generation fails
        """
        try:
            prompt = self._build_summary_prompt(paper)
            
            response = self.client.chat.completions.create(
                model=self.deployment,
                messages=[
                    {
                        "role": "system",
                        "content": "你是一位专业的AI和机器人领域研究分析师，擅长用中文总结学术论文的核心内容。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            summary = response.choices[0].message.content.strip()
            logger.info(f"Generated summary for paper: {paper.get('title', 'Unknown')[:50]}...")
            return summary
            
        except Exception as e:
            logger.error(f"Failed to generate summary: {str(e)}")
            return None
    
    def generate_investment_insights(self, paper: Dict, summary: str) -> Optional[str]:
        """
        Generate investment insights based on paper content
        
        Args:
            paper: Dictionary containing paper metadata
            summary: Chinese summary of the paper
        
        Returns:
            Investment insights string, or None if generation fails
        """
        try:
            prompt = self._build_insights_prompt(paper, summary)
            
            response = self.client.chat.completions.create(
                model=self.deployment,
                messages=[
                    {
                        "role": "system",
                        "content": "你是一位AI/机器人领域的投资分析师，擅长识别技术趋势和投资机会。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=800
            )
            
            insights = response.choices[0].message.content.strip()
            logger.info(f"Generated insights for paper: {paper.get('title', 'Unknown')[:50]}...")
            return insights
            
        except Exception as e:
            logger.error(f"Failed to generate investment insights: {str(e)}")
            return None
    
    def _build_summary_prompt(self, paper: Dict) -> str:
        """Build prompt for summary generation"""
        title = paper.get('title', 'Unknown')
        abstract = paper.get('abstract', 'No abstract available')
        authors = paper.get('authors', 'Unknown')
        year = paper.get('year', 'Unknown')
        venue = paper.get('venue', 'Unknown')
        citations = paper.get('citation_count', 0)
        
        return f"""请用中文总结以下学术论文的核心内容（300-500字）：

标题：{title}
作者：{authors}
年份：{year}
发表于：{venue}
引用次数：{citations}

摘要：
{abstract}

请包括：
1. 研究背景和动机
2. 主要方法/技术
3. 核心贡献和创新点
4. 实验结果（如有）
5. 潜在应用场景

用简洁、专业的中文表达，便于投资人快速理解。"""
    
    def _build_insights_prompt(self, paper: Dict, summary: str) -> str:
        """Build prompt for investment insights generation"""
        title = paper.get('title', 'Unknown')
        citations = paper.get('citation_count', 0)
        year = paper.get('year', 'Unknown')
        
        return f"""基于以下AI/机器人领域的学术论文，分析其投资价值和技术趋势（200-400字）：

论文标题：{title}
发表年份：{year}
引用次数：{citations}

论文总结：
{summary}

请从投资角度分析：
1. 技术成熟度（早期研究 vs 应用就绪）
2. 商业化潜力（可能的产品/服务方向）
3. 相关行业/公司（可能受益的领域）
4. 投资建议（关注点/风险提示）

用中文回答，重点突出投资相关信息。"""
