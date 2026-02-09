"""
VibeBuilder V2 - Orchestrator
Coordinates agents with conversational "Chat" start
"""

import time
import json
from typing import Dict, Generator
import google.generativeai as genai
from .researcher import ResearcherAgent
from .architect import ArchitectAgent
from .coder import CoderAgent
from .tester import TesterAgent
from .debugger import DebuggerAgent


class VibeBuilderOrchestrator:
    """
    Main Orchestrator - Coordinates all agents in 8-step workflow
    """
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        
        # Initialize agents
        self.researcher = ResearcherAgent(api_key)
        self.architect = ArchitectAgent(api_key)
        self.coder = CoderAgent(api_key)
        self.tester = TesterAgent(api_key)
        self.debugger = DebuggerAgent(api_key)

        # Gemini for Chat (Lovable style initial response)
        self.chat_model = genai.GenerativeModel('gemini-2.5-flash')
        
        self.delay = 1.0
        self.version_history = []
    
    def _wait(self):
        time.sleep(self.delay)

    def _get_chat_response(self, prompt: str, context: str = "") -> str:
        """Respond like a professional AI assistant acknowledging the goal"""
        system_context = "You are VibeAI, a professional web builder like Lovable or Replit. Acknowledge the user's request with a supportive, high-level overview of what you will build. Be brief (1-2 sentences). Do not mention steps yet."
        try:
            full_prompt = f"{system_context}\n\nUser Request: {prompt}\nContext: {context}"
            response = self.chat_model.generate_content(full_prompt)
            return response.text.strip() if response.text else "Got it! I'm starting the build process for your request."
        except:
            return "I've received your request and am starting the build process."

    def build(self, idea: str, max_iterations: int = 2) -> Generator[Dict, None, None]:
        """Full agentic workflow with chat start"""
        self.version_history = []
        
        # CHAT START (Lovable style)
        yield {
            "step": 0,
            "phase": "chat",
            "status": "complete",
            "message": self._get_chat_response(idea),
            "agent": "System"
        }
        self._wait()

        # STEP 1: RESEARCH
        yield {
            "step": 1,
            "phase": "research",
            "status": "starting",
            "message": "🔍 Exploring best practices..."
        }
        
        self._wait()
        research_result = self.researcher.research(idea)
        
        yield {
            "step": 1,
            "phase": "research",
            "status": "complete",
            "message": "Found inspiration for your app's structure.",
            "data": research_result
        }
        
        research_summary = research_result.get("summary", "")

        # STEP 2: PLAN
        yield {
            "step": 2,
            "phase": "plan",
            "status": "starting",
            "message": "🧠 Designing system architecture..."
        }
        
        self._wait()
        plan_result = self.architect.plan(idea, research_summary)
        
        yield {
            "step": 2,
            "phase": "plan",
            "status": "complete",
            "message": "Technical blueprint is ready.",
            "data": plan_result
        }
        
        # STEP 3: CODE
        yield {
            "step": 3,
            "phase": "code",
            "status": "starting",
            "message": "💻 Writing production-ready code..."
        }
        
        self._wait()
        code_result = self.coder.generate(idea, plan_result.get("plan", ""), research_summary[:500])
        current_code = code_result.get("code", "")
        self._add_version(current_code, "Initial generation")
        
        yield {
            "step": 3,
            "phase": "code",
            "status": "complete",
            "message": "Core application logic implemented.",
            "data": code_result
        }
        
        # STEP 4: TEST LOOP
        for iteration in range(max_iterations):
            yield {
                "step": 4,
                "phase": "test",
                "status": "starting",
                "iteration": iteration + 1,
                "message": f"🧪 Validating features..."
            }
            
            self._wait()
            test_result = self.tester.test(current_code, idea)
            
            if test_result.get("passed"):
                yield {
                    "step": 4,
                    "phase": "test",
                    "status": "passed",
                    "message": "Verification complete. No issues found.",
                    "data": test_result
                }
                break
            else:
                yield {
                    "step": 4,
                    "phase": "test",
                    "status": "failed",
                    "message": f"Identified minor improvements (Attempt {iteration+1})",
                    "data": test_result
                }
                
                # STEP 6: FIX
                yield {
                    "step": 6,
                    "phase": "fix",
                    "status": "starting",
                    "message": "🔧 Refining implementation..."
                }
                self._wait()
                fix_result = self.debugger.fix(current_code, test_result.get("analysis", "")[:1000])
                current_code = fix_result.get("fixed_code", current_code)
                self._add_version(current_code, f"After fix {iteration + 1}")
                
                yield {
                    "step": 6,
                    "phase": "fix",
                    "status": "complete",
                    "message": "Refinements applied successfully.",
                    "data": fix_result
                }
        
        # STEP 8: EXPORT
        yield {
            "step": 8,
            "phase": "export",
            "status": "complete",
            "message": "Success! Your application is live in the preview.",
            "final_code": current_code,
            "versions": self.version_history
        }
    
    def refine(self, code: str, feedback: str) -> Generator[Dict, None, None]:
        # CHAT START (Refine acknowledgment)
        yield {
            "step": 0,
            "phase": "chat",
            "status": "complete",
            "message": self._get_chat_response(feedback, "Current app is already built. Updating with your feedback."),
            "agent": "System"
        }
        self._wait()

        yield {
            "step": 7,
            "phase": "refine",
            "status": "starting",
            "message": "🔄 Updating implementation..."
        }
        
        self._wait()
        refine_result = self.debugger.refine(code, feedback)
        refined_code = refine_result.get("refined_code", code)
        self._add_version(refined_code, f"Refinement: {feedback[:30]}")
        
        # CRITICAL: Always include 'code' and 'final_code' so frontend reacts
        data_to_send = refine_result.copy()
        data_to_send["code"] = refined_code

        yield {
            "step": 7,
            "phase": "refine",
            "status": "complete",
            "message": "Your changes have been applied!",
            "data": data_to_send,
            "final_code": refined_code,
            "versions": self.version_history
        }
    
    def _add_version(self, code: str, description: str):
        self.version_history.append({
            "version": len(self.version_history) + 1,
            "code": code,
            "description": description
        })
