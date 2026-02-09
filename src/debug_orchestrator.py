
import os
import sys
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    print("Error: GOOGLE_API_KEY not found in environment")
    sys.exit(1)

try:
    from agents.orchestrator import VibeBuilderOrchestrator
    print("Successfully imported orchestrator")
    
    orchestrator = VibeBuilderOrchestrator(API_KEY)
    print("Orchestrator initialized")
    
    idea = "Weather Dashboard"
    print(f"Starting build for: {idea}")
    
    for update in orchestrator.build(idea, max_iterations=1):
        print(f"Update: {update.get('step')} - {update.get('status')}")
        
    print("Build completed successfully")
    
except Exception as e:
    print(f"CRASH: {e}")
    import traceback
    traceback.print_exc()
