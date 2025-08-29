#!/usr/bin/env python3
"""Simple API server to run DynamoDB evaluations."""

import sys
import json
import os
from datetime import datetime
from pathlib import Path
from flask import Flask, request, jsonify
from flask_cors import CORS

# Add the parent directory to Python path to import the evaluation module
sys.path.append(str(Path(__file__).parent.parent))

try:
    from test_dspy_evals import run_enhanced_evaluation
    from scenarios import BASIC_SCENARIOS
except ImportError as e:
    print(f"Failed to import evaluation module: {e}")
    run_enhanced_evaluation = None
    BASIC_SCENARIOS = []

app = Flask(__name__)
CORS(app)

# Path to the prompt file
PROMPT_PATH = Path(__file__).parent.parent.parent.parent / "awslabs" / "dynamodb_mcp_server" / "prompts" / "dynamodb_architect.md"

# Path to evaluation history
HISTORY_DIR = Path(__file__).parent.parent / "evaluation_history"
HISTORY_FILE = HISTORY_DIR / "evaluation_history.json"

def save_to_history(result, scenario_name):
    """Save evaluation result to history file."""
    try:
        # Create directory if it doesn't exist
        HISTORY_DIR.mkdir(exist_ok=True)
        
        # Load existing history
        history = []
        if HISTORY_FILE.exists():
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                history = json.load(f)
        
        # Add new result with metadata
        history_entry = {
            "id": len(history) + 1,
            "timestamp": datetime.now().isoformat(),
            "scenario_name": scenario_name,
            "result": result
        }
        history.append(history_entry)
        
        # Save updated history
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
            
    except Exception as e:
        print(f"Failed to save to history: {e}")

@app.route('/api/run-evaluation', methods=['POST'])
def run_evaluation():
    if run_enhanced_evaluation is None:
        return jsonify({"error": "Evaluation module not available"}), 500
        
    try:
        data = request.get_json() or {}
        scenario_name = data.get('scenario', 'Simple E-commerce Schema')
        
        # Call the evaluation function directly
        result = run_enhanced_evaluation(
            model_name=None,  # Use default
            scenario_name=scenario_name,
            verbose=False  # Suppress output
        )
        
        # Save to history
        save_to_history(result, scenario_name)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            "error": str(e),
            "type": type(e).__name__
        }), 500

@app.route('/api/history', methods=['GET'])
def get_history():
    try:
        if not HISTORY_FILE.exists():
            return jsonify([])
            
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            history = json.load(f)
            
        # Return history in reverse order (newest first)
        return jsonify(list(reversed(history)))
        
    except Exception as e:
        return jsonify({
            "error": str(e),
            "type": type(e).__name__
        }), 500

@app.route('/api/scenarios', methods=['GET'])
def get_scenarios():
    try:
        return jsonify(BASIC_SCENARIOS)
    except Exception as e:
        return jsonify({
            "error": str(e),
            "type": type(e).__name__
        }), 500

@app.route('/api/prompt', methods=['GET'])
def get_prompt():
    try:
        if not PROMPT_PATH.exists():
            return jsonify({"error": "Prompt file not found"}), 404
            
        with open(PROMPT_PATH, 'r', encoding='utf-8') as f:
            content = f.read()
            
        return jsonify({"content": content})
        
    except Exception as e:
        return jsonify({
            "error": str(e),
            "type": type(e).__name__
        }), 500

@app.route('/api/prompt', methods=['POST'])
def save_prompt():
    try:
        data = request.get_json()
        if not data or 'content' not in data:
            return jsonify({"error": "Content is required"}), 400
            
        content = data['content']
        
        # Create backup
        backup_path = PROMPT_PATH.with_suffix('.md.backup')
        if PROMPT_PATH.exists():
            with open(PROMPT_PATH, 'r', encoding='utf-8') as f:
                backup_content = f.read()
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(backup_content)
        
        # Save new content
        with open(PROMPT_PATH, 'w', encoding='utf-8') as f:
            f.write(content)
            
        return jsonify({"success": True, "message": "Prompt saved successfully"})
        
    except Exception as e:
        return jsonify({
            "error": str(e),
            "type": type(e).__name__
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
