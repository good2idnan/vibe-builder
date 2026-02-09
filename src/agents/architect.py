"""
VibeBuilder V2 - Architect Agent
Uses Gemini for planning
"""

import google.generativeai as genai
from typing import Dict, List
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from prompts import ARCHITECT_PROMPT


class ArchitectAgent:
    """
    Architect Agent - Plans architecture concisely
    """
    
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key, transport='rest')
        self.thinking_model = 'gemini-2.5-flash' # Using 2.5 Flash for thinking as well
        self.fallback_model = 'gemini-2.5-flash'
        self.model = genai.GenerativeModel(
            'gemini-2.5-flash', # Simplified: Always use flash for planning speed
            generation_config=genai.GenerationConfig(
                temperature=0.4,
                max_output_tokens=1024,
            )
        )
    
    def plan(self, idea: str, research: str = "") -> Dict:
        """
        Create architecture plan concisely
        """
        prompt = f"""{ARCHITECT_PROMPT}

## App Idea: {idea}
## Research: {research[:500]}

Define the technical blueprint. 
Provide:
1. "Architect Thoughts" (concise reasoning)
2. "Core Components" (bullet points)
3. "Plan" (high-level technical description)

Be extremely professional and brief."""

        try:
            print(f"[ArchitectAgent] Planning: {idea}")
            response = self.model.generate_content(prompt)
            
            plan_text = response.text if response.text else ""
            thinking = self._extract_section(plan_text, "Architect Thoughts")
            components = self._extract_components(plan_text)
            
            return {
                "success": True,
                "thinking": thinking or f"Designing a modular structure for {idea}.",
                "plan": plan_text,
                "components": components if components else ["UI Shell", "State Manager", "Feature Modules"]
            }
            
        except Exception as e:
            return {
                "success": False,
                "thinking": "Planning the core structure...",
                "plan": f"Basic plan for: {idea}",
                "components": ["HTML Structure", "CSS Styles", "JS Logic"]
            }
    
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
                if line.strip().startswith(('**', '#')) and ':' in line: break
                if line.strip(): content.append(line.strip())
            if len(content) > 3: break
        return ' '.join(content)

    def _extract_components(self, plan: str) -> List[str]:
        components = []
        lines = plan.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith(('-', '*', '•')) and len(line) > 5:
                components.append(line.lstrip('-*• ').strip()[:50])
        return components[:6]
