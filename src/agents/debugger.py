"""
VibeBuilder V2 - Debugger Agent
Uses Gemini for self-correction and refinement
"""

import google.generativeai as genai
from typing import Dict
import re
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from prompts import DEBUGGER_PROMPT, REFINER_PROMPT


class DebuggerAgent:
    """
    Debugger Agent - Fixes issues and handles refinements
    """
    
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key, transport='rest')
        self.model = genai.GenerativeModel(
            'gemini-2.5-flash',
            generation_config=genai.GenerationConfig(
                temperature=0.3,
                max_output_tokens=16384,
            )
        )
    
    def fix(self, code: str, issues: str) -> Dict:
        """Fix identified issues"""
        if not code: return {"success": False, "fixed_code": ""}
        
        prompt = f"""{DEBUGGER_PROMPT}

## Original Code:
```html
{code}
```

## Issues to Fix:
{issues}

Apply the fixes and return the COMPLETE updated HTML code."""

        try:
            print(f"[DebuggerAgent] Fixing issues...")
            response = self.model.generate_content(prompt)
            if not response.text: return {"success": False, "fixed_code": code}
            
            fixed_code = self._clean_code(response.text)
            return {
                "success": True,
                "thinking": "Resolving identified issues in layout and functionality.",
                "fixed_code": fixed_code or code,
                "changes_made": ["Applied stability fixes"]
            }
        except:
            return {"success": False, "fixed_code": code}
    
    def refine(self, code: str, feedback: str) -> Dict:
        """Refine code based on user feedback"""
        if not code: return {"success": False, "refined_code": ""}
        
        # Aggressive refiner prompt
        prompt = f"""{REFINER_PROMPT}

## Current Snapshot:
```html
{code}
```

## Requested Change: {feedback}

IMPORTANT CHALLENGE: 
The user wants to see their change reflected. 
If they asked for a feature, implement it fully. 
If they asked for a design change, apply it boldly.
Return the COMPLETE updated HTML code."""

        try:
            print(f"[DebuggerAgent] Refinement in progress...")
            response = self.model.generate_content(prompt)
            if not response.text: return {"success": False, "refined_code": code}
            
            refined_code = self._clean_code(response.text)
            return {
                "success": True,
                "thinking": f"Implementing your request: '{feedback[:50]}...'",
                "refined_code": refined_code or code,
                "changes_made": [feedback[:100]]
            }
        except:
            return {"success": False, "refined_code": code}
    
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
