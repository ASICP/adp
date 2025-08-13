#!/usr/bin/env python3
"""
Flask wrapper for ADP Demo - Render deployment
"""

import os
import json
import asyncio
from flask import Flask, render_template_string, request, jsonify
from adp_demo_script import ADPMasterController

app = Flask(__name__)

# Initialize Master Controller globally
mc = ADPMasterController("demo-mc-render-001")

# HTML template for the demo page
DEMO_HTML = """<!DOCTYPE html>
<html>
<head>
    <title>ADP (Alignment Delegation Protocol) Demo</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; line-height: 1.6; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .header { background: #2c3e50; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; text-align: center; }
        .demo-section { margin: 20px 0; padding: 20px; border: 1px solid #ddd; border-radius: 8px; }
        .query-form { background: #ecf0f1; padding: 20px; border-radius: 8px; }
        input[type="text"] { width: 60%; padding: 12px; margin: 5px; border: 1px solid #ddd; border-radius: 4px; }
        select { padding: 12px; margin: 5px; border: 1px solid #ddd; border-radius: 4px; }
        button { padding: 12px 24px; background: #3498db; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 16px; }
        button:hover { background: #2980b9; }
        .result { background: #f8f9fa; padding: 20px; border-radius: 8px; margin-top: 15px; border-left: 4px solid #28a745; }
        .error { border-left-color: #dc3545; background: #f8d7da; }
        .loading { text-align: center; padding: 20px; color: #666; }
        pre { white-space: pre-wrap; font-size: 12px; overflow-x: auto; background: #f1f1f1; padding: 15px; border-radius: 4px; }
        .status-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 15px; margin-top: 15px; }
        .stat-card { background: #e8f4fd; padding: 15px; border-radius: 8px; border-left: 4px solid #3498db; }
        .status { padding: 5px 10px; border-radius: 4px; color: white; display: inline-block; font-weight: bold; }
        .safe { background: #28a745; }
        .flagged { background: #dc3545; }
        .degraded { background: #ffc107; color: #000; }
        @media (max-width: 768px) {
            input[type="text"] { width: 90%; }
            .container { margin: 10px; padding: 15px; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 ADP (Alignment Delegation Protocol)</h1>
            <p>Live Demo - Intelligent AI Model Delegation with Alignment Oversight</p>
            <small>Hosted on Render Free Tier | Version 1.0</small>
        </div>
        
        <div class="demo-section">
            <h3>🎯 Test ADP Delegation</h3>
            <p>Enter a query below and watch ADP intelligently route it to specialized AI models with real-time alignment monitoring.</p>
            
            <div class="query-form">
                <form id="queryForm">
                    <div style="margin-bottom: 15px;">
                        <input type="text" id="query" placeholder="Enter your query (e.g., 'What are symptoms of chest pain?')" required>
                    </div>
                    <div style="margin-bottom: 15px;">
                        <select id="domain">
                            <option value="medical">🏥 Medical</option>
                            <option value="legal">⚖️ Legal</option>
                            <option value="technical">💻 Technical</option>
                            <option value="financial">💰 Financial</option>
                        </select>
                        <select id="priority">
                            <option value="normal">📋 Normal</option>
                            <option value="high">⚡ High</option>
                            <option value="urgent">🚨 Urgent</option>
                        </select>
                    </div>
                    <button type="submit">🚀 Delegate Query</button>
                </form>
            </div>
            
            <div id="queryResult"></div>
        </div>
        
        <div class="demo-section">
            <h3>📊 System Status</h3>
            <button onclick="loadStatus()">🔄 Refresh Status</button>
            <div id="statusDisplay">Click refresh to load system status...</div>
        </div>
        
        <div class="demo-section">
            <h3>📋 About ADP Protocol</h3>
            <p><strong>ADP Version 1.0</strong> demonstrates:</p>
            <ul>
                <li>🎯 <strong>Intelligent Routing:</strong> Selects best Narrow Models based on domain, load, and performance</li>
                <li>🔄 <strong>Validation:</strong> Multiple NMs process queries for alignment verification</li>
                <li>🛡️ <strong>Safety Monitoring:</strong> Real-time alignment assessment and logging</li>
                <li>⚡ <strong>Load Balancing:</strong> Round-robin and weighted selection algorithms</li>
                <li>🌐 <strong>Transparency:</strong> Full audit trail for AI delegation decisions</li>
            </ul>
            
            <h4>Example Queries to Try:</h4>
            <ul>
                <li><strong>Medical:</strong> "What are the symptoms of chest pain?"</li>
                <li><strong>Legal:</strong> "Review contract compliance requirements"</li>
                <li><strong>Technical:</strong> "Analyze network security vulnerabilities"</li>
                <li><strong>Financial:</strong> "Assess investment risk factors"</li>
            </ul>
        </div>
    </div>
    
    <script>
        document.getElementById('queryForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const query = document.getElementById('query').value;
            const domain = document.getElementById('domain').value;
            const priority = document.getElementById('priority').value;
            
            const resultDiv = document.getElementById('queryResult');
            resultDiv.innerHTML = '<div class="loading">🔄 Processing query through ADP...</div>';
            
            try {
                const response = await fetch('/api/query', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ query, domain, priority })
                });
                
                const result = await response.json();
                
                if (result.error) {
                    resultDiv.innerHTML = `<div class="result error">❌ Error: ${result.error}</div>`;
                } else {
                    const summary = result.summary;
                    const alignmentStatus = summary.alignment_status.includes('SAFE') ? 'safe' : 'flagged';
                    
                    resultDiv.innerHTML = `
                        <div class="result">
                            <h4>📋 Query Summary</h4>
                            <p><strong>Query:</strong> ${query}</p>
                            <p><strong>Primary NM:</strong> ${summary.primary_nm}</p>
                            <p><strong>Confidence:</strong> ${summary.primary_confidence}</p>
                            <p><strong>Status:</strong> <span class="status ${alignmentStatus}">${summary.alignment_status}</span></p>
                            <p><strong>Processing Time:</strong> ${summary.processing_time}</p>
                            ${summary.validation_count > 0 ? `<p><strong>Validation:</strong> ${summary.validation_count} models, ${summary.validation_consensus || 'N/A'} consensus</p>` : ''}
                        </div>
                        
                        <div class="result">
                            <h4>🤖 Primary Response</h4>
                            <pre>${result.primary_response.payload.response_content}</pre>
                        </div>
                        
                        <div class="result">
                            <h4>🔧 Technical Details</h4>
                            <p><strong>Routing Method:</strong> ${result.routing.routing_method}</p>
                            <p><strong>Available NMs:</strong> ${result.routing.total_available}</p>
                            <details>
                                <summary>View Full JSON Response</summary>
                                <pre>${JSON.stringify(result, null, 2)}</pre>
                            </details>
                        </div>
                    `;
                }
            } catch (error) {
                resultDiv.innerHTML = `<div class="result error">❌ Error: ${error.message}</div>`;
            }
        });
        
        async function loadStatus() {
            const statusDiv = document.getElementById('statusDisplay');
            statusDiv.innerHTML = '<div class="loading">Loading status...</div>';
            
            try {
                const response = await fetch('/api/status');
                const data = await response.json();
                
                statusDiv.innerHTML = `
                    <div class="status-grid">
                        <div class="stat-card">
                            <h4>System Health</h4>
                            <p>${data.system_health}</p>
                        </div>
                        <div class="stat-card">
                            <h4>Total NMs</h4>
                            <p>${data.routing_stats.total_nms}</p>
                        </div>
                        <div class="stat-card">
                            <h4>Overall Health</h4>
                            <p>${(data.routing_stats.overall_health * 100).toFixed(1)}%</p>
                        </div>
                        <div class="stat-card">
                            <h4>CA Logs</h4>
                            <p>${data.ca_logs}</p>
                        </div>
                        <div class="stat-card">
                            <h4>Total Transactions</h4>
                            <p>${data.total_transactions}</p>
                        </div>
                        <div class="stat-card">
                            <h4>Timestamp</h4>
                            <p>${new Date(data.timestamp).toLocaleString()}</p>
                        </div>
                    </div>
                    <details style="margin-top: 20px;">
                        <summary>View Full Status JSON</summary>
                        <pre>${JSON.stringify(data, null, 2)}</pre>
                    </details>
                `;
            } catch (error) {
                statusDiv.innerHTML = `<div class="result error">Error loading status: ${error.message}</div>`;
            }
        }
    </script>
</body>
</html>"""

@app.route('/')
def home():
    """Serve the main demo page"""
    return render_template_string(DEMO_HTML)

@app.route('/api/status')
def get_status():
    """API endpoint for system status"""
    try:
        status = mc.get_system_status()
        return jsonify(status)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/query', methods=['POST'])
def process_query():
    """API endpoint for processing queries"""
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        domain = data.get('domain', 'medical')
        priority = data.get('priority', 'normal')
        
        if not query:
            return jsonify({"error": "Query is required"}), 400
        
        # Process query asynchronously
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(mc.process_user_query(query, domain, priority))
            return jsonify(result)
        finally:
            loop.close()
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/health')
def health_check():
    """Health check endpoint for Render"""
    return jsonify({"status": "healthy", "service": "adp-demo"})

if __name__ == '__main__':
    # Use PORT environment variable (required for Render)
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
