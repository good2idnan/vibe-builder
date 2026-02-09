"""
VibeBuilder V2 - Coder Agent
Uses Gemini for code generation
"""

import google.generativeai as genai
from typing import Dict, List
import re
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from prompts import CODER_PROMPT


class CoderAgent:
    """
    Coder Agent - Generates complete, beautiful code
    """
    
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key, transport='rest')
        self.model = genai.GenerativeModel(
            'gemini-2.5-flash',
            generation_config=genai.GenerationConfig(
                temperature=0.4,
                max_output_tokens=16384,
            )
        )
    
    def generate(self, idea: str, plan: str, research: str = "") -> Dict:
        """
        Generate complete code based on plan and research
        """
        research_context = f"\n\n## Research Insights:\n{research}" if research else ""
        
        prompt = f"""{CODER_PROMPT}

## Original Idea: {idea}
## Architecture Plan: {plan}
{research_context}

Generate a COMPLETE, WORKING HTML file.
Include a BRIEF comment at the top explaining your technical approach for this specific app (1-2 sentences)."""

        try:
            print(f"[CoderAgent] Generating code...")
            response = self.model.generate_content(prompt)
            
            if not response.text:
                return {"success": False, "code": self._fallback_code(idea), "features": []}
            
            cleaned_code = self._clean_code(response.text)
            thinking = self._extract_thinking(cleaned_code)
            
            return {
                "success": True,
                "thinking": thinking or f"Building a responsive {idea} with optimized assets and modern layout.",
                "code": cleaned_code,
                "language": "html",
                "features": self._detect_features(cleaned_code)
            }
            
        except Exception as e:
            return {"success": False, "code": self._fallback_code(idea), "features": []}
    
    def _extract_thinking(self, code: str) -> str:
        # Match the first comment in HTML
        match = re.search(r'<!--\s*(.*?)\s*-->', code, re.DOTALL)
        if match:
            text = match.group(1).strip()
            if len(text) > 10 and len(text) < 300: return text
        return ""

    def _fallback_code(self, idea: str) -> str:
        return f"<!DOCTYPE html><html><body><h1>{idea}</h1><p>Generation failed.</p></body></html>"
    
    def _clean_code(self, code: str) -> str:
        if not code: return ""
        code = re.sub(r'^```html?\s*\n?', '', code, flags=re.MULTILINE)
        code = re.sub(r'^```\s*$', '', code, flags=re.MULTILINE)
        code = re.sub(r'```$', '', code)
        code = code.strip()
        html_start = code.lower().find('<!doctype')
        if html_start == -1: html_start = code.lower().find('<html')
        if html_start > 0: code = code[html_start:]
        return code
    
    def _detect_features(self, code: str) -> list:
        features = []
        code_lower = code.lower()
        checks = {
            "🌙 Dark Mode": "dark" in code_lower,
            "📱 Responsive": "@media" in code_lower,
            "✨ Animations": "keyframes" in code_lower,
            "💾 Data Persistence": "localstorage" in code_lower,
            "🎨 Custom Themes": "--" in code_lower, 
            "📝 Dynamic Forms": "addeventlistener" in code_lower and "submit" in code_lower
        }
        for f, c in checks.items():
            if c: features.append(f)
        return features[:6]
