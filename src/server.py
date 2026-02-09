"""
VibeBuilder V2 - Flask Backend API
Serves the frontend and handles AI generation requests
"""

from flask import Flask, request, jsonify, send_from_directory, Response
from flask_cors import CORS
import os
import sys
import json
import time
from dotenv import load_dotenv

# Add parent directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

load_dotenv()

# Configure static folder explicitly
static_folder = os.path.join(current_dir, 'static')
app = Flask(__name__, static_folder=static_folder)
CORS(app)

API_KEY = os.getenv("GOOGLE_API_KEY", "")

# Configure Gemini globally with REST transport to avoid gRPC hangs
if API_KEY:
    import google.generativeai as genai
    genai.configure(api_key=API_KEY, transport='rest')

print(f"📂 Serving static files from: {static_folder}")

@app.route('/')
def index():
    """Serve the main HTML page"""
    try:
        return send_from_directory(static_folder, 'index.html')
    except Exception as e:
        return f"Error serving index.html: {e}", 500


@app.route('/<path:path>')
def serve_static(path):
    """Serve static files"""
    try:
        return send_from_directory(static_folder, path)
    except Exception as e:
        return f"Error serving {path}: {e}", 404


@app.route('/api/build', methods=['POST'])
def build():
    """Stream the build process"""
    print("🚀 Received build request")
    data = request.json
    idea = data.get('idea', '')
    
    if not idea:
        return jsonify({"error": "No idea provided"}), 400
    
    if not API_KEY:
        print("❌ API Key missing")
        return jsonify({"error": "API key not configured"}), 500
    
    def generate():
        try:
            print(f"🔨 Starting build for: {idea[:50]}...")
            from agents.orchestrator import VibeBuilderOrchestrator
            orchestrator = VibeBuilderOrchestrator(API_KEY)
            
            # Send initial ping
            yield f"data: {json.dumps({'step': 0, 'status': 'starting', 'message': 'Initializing...'})}\n\n"
            
            for update in orchestrator.build(idea, max_iterations=2):
                print(f"📤 Sending update: {update.get('status')} - {update.get('message')}")
                yield f"data: {json.dumps(update)}\n\n"
                
        except Exception as e:
            print(f"❌ Error during build: {e}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return Response(generate(), mimetype='text/event-stream')


@app.route('/api/refine', methods=['POST'])
def refine():
    """Refine existing code"""
    print("🔧 Received refine request")
    data = request.json
    code = data.get('code', '')
    feedback = data.get('feedback', '')
    
    if not code or not feedback:
        return jsonify({"error": "Missing code or feedback"}), 400
    
    def generate():
        try:
            from agents.orchestrator import VibeBuilderOrchestrator
            orchestrator = VibeBuilderOrchestrator(API_KEY)
            
            for update in orchestrator.refine(code, feedback):
                yield f"data: {json.dumps(update)}\n\n"
            
        except Exception as e:
            print(f"❌ Error during refine: {e}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return Response(generate(), mimetype='text/event-stream')


@app.route('/api/health')
def health():
    """Health check"""
    return jsonify({
        "status": "ok",
        "api_configured": bool(API_KEY),
        "static_folder": static_folder
    })


if __name__ == '__main__':
    print("🔨 VibeBuilder V2 Starting...")
    print(f"   API Key: {'Configured ✓' if API_KEY else 'Missing ✗'}")
    print("   Open: http://localhost:5000")
    app.run(debug=True, port=5000, host='0.0.0.0')
