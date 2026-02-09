"""
VibeBuilder V2 - Researcher Agent
Uses Gemini for research
"""

import google.generativeai as genai
from typing import Dict, List


class ResearcherAgent:
    """
    Research Agent - Searches for best practices before coding
    """
    
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key, transport='rest')
        self.model = genai.GenerativeModel(
            'gemini-2.5-flash',
            tools=[{'google_search_retrieval': {}}],
            generation_config=genai.GenerationConfig(
                temperature=0.3,
                max_output_tokens=1024,
            )
        )
    
    def research(self, idea: str) -> Dict:
        """
        Research best practices for the given app idea
        """
        prompt = f"""Identify 3-5 critical best practices and UI/UX patterns for a modern '{idea}' application.
If a URL is provided, please prioritize analyzing and summarizing it to find core themes, color palettes, and specific components.

Focus on:
1. **Current Best Practices (2025+)** - State-of-the-art web trends.
2. **Component Analysis** - Breakdown of essential interactive elements.
3. **Professional UI/UX Patterns** - Modern layouts and accessibility.

Return a structured response with:
- "Thinking Process": Brief explanation of your analysis strategy.
- "Key Findings": Actionable bullet points for the architect and coder.

Be extremely concise and professional. No fluff."""

        try:
            print(f"[Researcher] Researching: {idea}")
            response = self.model.generate_content(prompt)
            
            if response.text:
                thinking = self._extract_section(response.text, "Thinking Process")
                findings = self._extract_section(response.text, "Key Findings")
                
                return {
                    "success": True,
                    "summary": response.text,
                    "thinking": thinking or "Analyzing market leaders and UX patterns.",
                    "findings": findings or "Prioritizing mobile-first design and accessibility.",
                    "insights": self._extract_key_insights(response.text)
                }
            else:
                return {"success": False, "thinking": "No results found.", "findings": "", "insights": []}
            
        except Exception as e:
            return {"success": False, "thinking": "Research error.", "findings": "", "insights": []}
    
    def _extract_section(self, text: str, section_name: str) -> str:
        if section_name not in text: return ""
        lines = text.split('\n')
        content = []
        found = False
        for line in lines:
            if section_name.lower() in line.lower():
                found = True
                continue
            if found:
                if line.strip().startswith('**') and ':' in line: break # Next section
                if line.strip(): content.append(line.strip())
            if len(content) > 5: break
        return ' '.join(content) if section_name == "Thinking Process" else '\n'.join(content)

    def _extract_key_insights(self, text: str) -> List[str]:
        insights = []
        if not text: return insights
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith(('-', '*', '•')) and len(line) > 5:
                insights.append(line.lstrip('-*• ').strip()[:150])
        return insights[:5]
