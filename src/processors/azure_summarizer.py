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
                        "content": "你是一位专业的AI和机器人领域研究分析师，擅长用中文撰写详细、深入的学术论文解读。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=3000
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
        
        return f"""请用中文撰写一篇详细的学术论文解读（800-1500字），采用以下五个模块结构：

标题：{title}
作者：{authors}
年份：{year}
发表于：{venue}
引用次数：{citations}

摘要：
{abstract}

请按照以下五个模块撰写：

## 一、研究背景
- 介绍该研究所处的学术和技术背景
- 说明当前领域存在的问题或挑战
- 阐述为什么需要进行这项研究

## 二、核心问题
- 明确指出本研究要解决的核心问题
- 说明该问题的重要性和影响
- 对比现有方法的不足之处

## 三、方法创新
- 详细描述研究采用的新方法或技术
- 解释创新点在哪里（算法、架构、流程等）
- 说明与传统方法的本质区别

## 四、关键结果
- 总结实验或理论分析的主要发现
- 列举重要的性能指标或突破
- 说明结果的统计显著性和可靠性

## 五、应用价值
- 分析该研究的实际应用场景
- 评估技术落地的可行性
- 展望未来可能的发展方向和影响范围

撰写要求：
- 总字数控制在800-1500字之间
- 使用专业但易懂的中文表达
- 每个模块内容充实，避免空洞描述
- 突出论文的创新性和实用价值
- 适合投资人和技术决策者阅读"""
    
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
