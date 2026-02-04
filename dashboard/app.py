"""
Web Dashboard for Crypto Signal System
Flask-based monitoring interface
"""
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from datetime import datetime
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import DatabaseManager

app = Flask(__name__)
CORS(app)

# Initialize database
db = DatabaseManager()

@app.route('/')
def index():
    """Home page - System status"""
    stats = db.get_performance_stats()
    return render_template('index.html', stats=stats, current_time=datetime.now())

@app.route('/signals')
def signals():
    """Signals page - All signals"""
    signals_list = db.get_signal_history(days=7)
    return render_template('signals.html', signals=signals_list)

@app.route('/performance')
def performance():
    """Performance page - Charts and analytics"""
    stats = db.get_performance_stats()
    return render_template('performance.html', stats=stats)

@app.route('/api/stats')
def api_stats():
    """API endpoint for real-time stats"""
    stats = db.get_performance_stats()
    return jsonify(stats)

@app.route('/api/signals')
def api_signals():
    """API endpoint for signals list"""
    limit = request.args.get('limit', 20, type=int)
    signals = db.get_recent_signals(limit=limit)
    return jsonify(signals)

@app.route('/api/open_signals')
def api_open_signals():
    """API endpoint for open signals"""
    signals = db.get_open_signals()
    return jsonify(signals)

if __name__ == '__main__':
    print("🌐 Dashboard starting at http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
