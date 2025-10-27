"""
Flask WAF Integration Example

This example shows how to protect a Flask application with VESSA WAF.
"""

from flask import Flask, request, jsonify
from services.waf.integrations import FlaskWAF
from services.waf import WAFConfig
from services.waf.waf_config import BlockingMode

# Create Flask app
app = Flask(__name__)

# Configure WAF
waf_config = WAFConfig(
    mode=BlockingMode.BLOCK,
    enabled=True,
    log_blocked_requests=True
)

# Option 1: Protect entire app
waf = FlaskWAF(app, config=waf_config)

# All routes are now protected!

@app.route('/')
def index():
    return 'Hello, World!'


@app.route('/api/data')
def get_data():
    """API endpoint - automatically protected."""
    return jsonify({
        'data': [1, 2, 3, 4, 5],
        'status': 'success'
    })


@app.route('/api/login', methods=['POST'])
def login():
    """Login endpoint - protected against injection attacks."""
    username = request.form.get('username')
    password = request.form.get('password')
    
    # WAF blocks SQL injection attempts automatically
    # No need for manual input validation
    
    return jsonify({'token': 'abc123'})


@app.route('/api/search')
def search():
    """Search endpoint - protected against XSS."""
    query = request.args.get('q', '')
    
    # WAF blocks XSS attempts like: ?q=<script>alert('xss')</script>
    
    return jsonify({'query': query, 'results': []})


# WAF stats endpoint
@app.route('/waf/stats')
def waf_stats():
    """Get WAF statistics."""
    return jsonify(waf.get_stats())


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

