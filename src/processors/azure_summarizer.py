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
        
        return f"""你是一位资深的AI/机器人领域投资分析师，正在为投资决策者撰写一份深度技术解读报告。

📄 论文信息：
标题：{title}
作者：{authors}
年份：{year}
发表于：{venue}
引用次数：{citations}

摘要：
{abstract}

请撰写一份800-1500字的中文深度解读，采用以下五模块结构：

## 一、研究背景（150-250字）
回答三个问题：
1. **行业痛点**：当前技术/市场存在什么具体问题？用数据或案例说明
2. **时机判断**：为什么是现在解决这个问题？（技术成熟度、市场需求、政策环境等）
3. **研究动机**：作者团队为什么要做这个研究？他们的独特优势是什么？

## 二、核心问题（150-250字）
聚焦问题本质：
1. **问题定义**：用一句话概括要解决的核心技术难题
2. **影响范围**：这个问题影响哪些行业/场景？市场规模有多大？
3. **现有方案缺陷**：列举2-3个主流方法的具体不足（最好有性能对比数据）
4. **突破难度**：为什么这个问题之前没被解决？技术壁垒在哪里？

## 三、技术突破（250-400字）
详细拆解创新点：
1. **核心方法**：用通俗语言解释新方法的工作原理（避免过多数学公式）
2. **创新亮点**：列举3个关键创新点，说明每个创新解决了什么具体问题
3. **技术对比**：与baseline方法对比，优势在哪里？（架构、效率、成本、可扩展性等）
4. **实现难度**：这个方法容易复现吗？需要什么样的资源（算力、数据、人才）？

## 四、关键结果（200-300字）
用数据说话：
1. **性能指标**：列举核心性能指标的具体数值（准确率、速度、成本等）
2. **对比优势**：比SOTA方法提升了多少？用百分比或倍数表示
3. **实验验证**：在什么数据集/场景下测试的？结果的可信度如何？
4. **局限性**：坦诚指出方法的不足或适用边界（什么情况下不work）

## 五、商业价值（250-350字）
投资视角分析：
1. **应用场景**：列举3-5个具体的商业应用场景，说明每个场景的市场规模
2. **落地可行性**：技术成熟度如何？距离产品化还有多远？（实验室 → 原型 → 产品 → 规模化）
3. **竞争态势**：哪些公司/团队在做类似方向？本研究的竞争优势是什么？
4. **投资机会**：
   - 短期（6-12月）：可关注哪些应用方向或公司？
   - 中期（1-3年）：可能催生哪些新产品/服务？
   - 长期（3-5年）：对行业格局有什么影响？
5. **风险提示**：技术风险、市场风险、政策风险各是什么？

---
撰写要求：
✅ 总字数严格控制在800-1500字
✅ 每个模块必须包含具体数据、案例或对比（避免空洞描述）
✅ 使用投资人易懂的语言，减少学术术语
✅ **首次出现的缩写/术语必须给出完整解释**（例如："SCARE（Surgical CAse REport，外科病例报告）指南"）
✅ 突出商业价值和投资机会
✅ 客观评估，包含风险提示
✅ 每个关键观点都要有依据（来自摘要或常识推理）
✅ 在文末添加"术语解释"部分，列出所有重要缩写和专业术语的中文说明"""
    
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
