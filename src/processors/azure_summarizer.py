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
                        "content": "你是一位专业的科技领域研究分析师，擅长用中文撰写详细、深入的学术论文解读。你的专业范围包括：AI/机器人、新能源/电池技术、生物技术/基因编辑、量子计算等前沿科技领域。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=4500  # Increased from 3000 to allow longer, more detailed summaries
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
                        "content": "你是一位科技领域的投资分析师，擅长识别 AI/机器人、新能源/电池、生物技术、量子计算等前沿领域的技术趋势和投资机会。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=1200  # Increased from 800 to allow more detailed investment insights
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
        
        return f"""你是一位资深的科技领域投资分析师，正在为投资决策者撰写一份深度技术解读报告。你的专业范围包括：AI/机器人、新能源/电池技术、生物技术/基因编辑、量子计算等前沿科技领域。

📄 论文信息：
标题：{title}
作者：{authors}
年份：{year}
发表于：{venue}
引用次数：{citations}

摘要：
{abstract}

请撰写一份**1200-1800字**的中文深度解读（注意：这是字数下限，不是上限，内容越充实越好）。

**重要：必须按以下格式输出，术语速查必须放在最前面！**

### 术语速查
- **[缩写/术语]**：[完整名称或中文说明] - [一句话解释其含义]

（列出3-5个核心术语，每个术语一行。这部分必须在所有正文之前！）

---

## 一、研究背景（200-300字）
**详细展开**回答三个问题：
1. **行业痛点**：当前技术/市场存在什么具体问题？用数据或案例说明（至少50字）
2. **时机判断**：为什么是现在解决这个问题？（技术成熟度、市场需求、政策环境等，至少50字）
3. **研究动机**：作者团队为什么要做这个研究？他们的独特优势是什么？（至少100字）

## 二、核心问题（200-300字）
**深入分析**聚焦问题本质：
1. **问题定义**：用通俗易懂的语言概括要解决的核心技术难题（至少30字）
2. **影响范围**：这个问题影响哪些行业/场景？市场规模有多大？（至少50字，必须包含具体数字）
3. **现有方案缺陷**：详细列举2-3个主流方法的具体不足，**必须有性能对比数据或案例**（至少80字）
4. **突破难度**：为什么这个问题之前没被解决？技术壁垒在哪里？（至少40字）

## 三、技术突破（350-500字）
**详细拆解**创新点（这是最重要的部分，要写得充实）：
1. **核心方法**：用通俗语言解释新方法的工作原理，可以用类比帮助理解（至少100字）
2. **创新亮点**：详细列举3个关键创新点，**每个创新点至少80字**，说明解决了什么具体问题
3. **技术对比**：与baseline方法深入对比，优势在哪里？（架构、效率、成本、可扩展性等，至少80字，必须有具体对比）
4. **实现难度**：这个方法容易复现吗？需要什么样的资源？（算力、数据、人才，至少50字）

## 四、关键结果（250-350字）
**用数据说话**（必须详细，避免笼统）：
1. **性能指标**：详细列举核心性能指标的具体数值（准确率、速度、成本等），**每个指标至少20字解释其意义**（至少100字）
2. **对比优势**：比SOTA方法提升了多少？用百分比或倍数表示，**必须有具体数字对比**（至少60字）
3. **实验验证**：在什么数据集/场景下测试的？数据集规模？结果的可信度如何？（至少60字）
4. **局限性**：坦诚指出方法的不足或适用边界，什么情况下不work（至少30字）

## 五、商业价值（350-500字）
**投资视角深度分析**（这部分要特别充实）：
1. **应用场景**：详细列举4-6个具体的商业应用场景，**每个场景至少40字，必须说明市场规模**（共至少240字）
2. **落地可行性**：技术成熟度如何？距离产品化还有多远？需要哪些条件？（实验室 → 原型 → 产品 → 规模化，至少60字）
3. **竞争态势**：哪些公司/团队在做类似方向？本研究的竞争优势是什么？**必须提及至少3家具体公司名称**（至少50字）
4. **投资机会**（至少120字，这是投资人最关心的）：
   - 短期（6-12月）：可关注哪些应用方向或公司？**必须提及至少2个具体行业名称和2家公司名称**（至少40字）
   - 中期（1-3年）：可能催生哪些新产品/服务？**需指明至少2个具体行业领域和产品形态**（至少40字）
   - 长期（3-5年）：对行业格局有什么影响？**需说明影响的具体产业和变革方向**（至少40字）
5. **风险提示**：技术风险、市场风险、政策风险各是什么？（至少50字，每类风险至少15字）

---
**撰写要求**：
✅ **术语速查必须是第一部分**，放在所有正文模块之前
✅ **总字数严格控制在1200-1800字（不含术语速查）** - 这是下限不是上限，越详细越好
✅ **每个模块必须达到指定字数要求**，包含具体数据、案例或对比（避免空洞描述）
✅ **商业价值部分必须提及具体的行业名称（至少6个）和公司名称（至少5家）**
✅ 使用投资人易懂的语言，行文流畅自然，段落之间过渡连贯
✅ **正文中首次出现术语时直接使用中文或给出括号解释**
✅ 避免生硬堆砌信息，注重叙述的逻辑性和可读性
✅ 突出商业价值和投资机会，每个观点都要有依据
✅ **不要在文末重复术语解释**

**字数检查**：完成后请自查每个模块是否达到最低字数要求。如果某个模块不足，请补充更多细节、案例或数据。"""

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
   - 短期（6-12月）：可关注哪些应用方向或公司？**必须提及具体行业名称（如：自动驾驶、医疗影像、智能制造等）和代表性公司名称（如：OpenAI、特斯拉、商汤等）**
   - 中期（1-3年）：可能催生哪些新产品/服务？**需指明具体行业领域**
   - 长期（3-5年）：对行业格局有什么影响？**需说明影响的具体产业**
5. **风险提示**：技术风险、市场风险、政策风险各是什么？

---
撰写要求：
✅ **术语速查必须是第一部分**，放在所有正文模块之前
✅ 总字数严格控制在800-1500字（不含术语速查）
✅ 每个模块必须包含具体数据、案例或对比（避免空洞描述）
✅ 使用投资人易懂的语言，行文流畅自然，段落之间过渡连贯
✅ **正文中首次出现术语时直接使用中文或给出括号解释**（如："Transformer架构"、"SCARE（外科病例报告）指南"）
✅ 避免生硬堆砌信息，注重叙述的逻辑性和可读性
✅ 突出商业价值和投资机会
✅ 客观评估，包含风险提示
✅ 每个关键观点都要有依据（来自摘要或合理推理）
✅ **不要在文末重复术语解释**

---
严格按照此格式输出：
### 术语速查
- **[缩写/术语]**：[完整名称或中文说明] - [一句话解释其含义]

（列出3-5个核心术语，每个术语一行）

---

## 一、研究背景
[内容...]

## 二、核心问题
[内容...]

## 三、技术突破
[内容...]

## 四、关键结果
[内容...]

## 五、商业价值
[内容...]"""
    
    def _build_insights_prompt(self, paper: Dict, summary: str) -> str:
        """Build prompt for investment insights generation"""
        title = paper.get('title', 'Unknown')
        citations = paper.get('citation_count', 0)
        year = paper.get('year', 'Unknown')
        
        return f"""基于以下前沿科技领域（AI/机器人、新能源/电池、生物技术、量子计算等）的学术论文，分析其投资价值和技术趋势（**400-600字**）：

论文标题：{title}
发表年份：{year}
引用次数：{citations}

论文总结：
{summary}

请从投资角度**详细深入**分析（必须达到400-600字）：

1. **技术成熟度**（80-100字）
   - 当前处于哪个阶段？（早期研究 vs 中期验证 vs 应用就绪）
   - 技术路线是否清晰？核心技术壁垒是什么？
   - 距离产品化还有多远？需要克服哪些障碍？

2. **商业化潜力**（120-150字）
   - 详细说明3-5个可能的产品/服务方向，每个至少20字
   - 各应用场景的市场规模估计（必须有数据）
   - 哪些场景最容易落地？为什么？
   - 商业模式清晰吗？盈利路径是什么？

3. **相关行业/公司**（120-150字）
   - **必须提及至少3个具体行业名称**（如：自动驾驶、医疗影像、智能制造、金融科技、新能源汽车、机器人、半导体、云计算等）
   - **必须提及至少5家代表性公司名称**（如：OpenAI、特斯拉、商汤科技、百度、华为、腾讯、阿里巴巴、英伟达、谷歌、微软等）
   - 说明每家公司与该技术的关联度和布局情况
   - 哪些公司最有可能率先应用这项技术？

4. **投资建议**（80-120字）
   - **短期关注点**（6-12个月）：哪些领域/公司值得关注？具体理由？
   - **中长期机会**（1-3年）：可能出现哪些新的投资标的或商业模式？
   - **风险提示**：技术风险、市场风险、政策风险各是什么？每类至少15字

用中文回答，重点突出投资相关信息。**务必在分析中包含具体的行业名称（至少3个）和公司名称（至少5家），并说明理由，避免泛泛而谈。**"""
