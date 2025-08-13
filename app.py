#!/usr/bin/env python3
"""
Enhanced ADP Demo Flask App - Demo2 with improved UI/UX
"""

import os
import json
import asyncio
from flask import Flask, render_template_string, request, jsonify
from adp_demo_script import ADPMasterController

app = Flask(__name__)

# Initialize Master Controller globally
mc = ADPMasterController("demo-mc-render-002")

# Enhanced HTML template with sophisticated UI
DEMO_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ADP - Alignment Delegation Protocol</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        :root {
            --primary-color: #1a1a2e;
            --secondary-color: #16213e;
            --accent-color: #e94560;
            --success-color: #0f3460;
            --warning-color: #f39c12;
            --danger-color: #e74c3c;
            --text-primary: #ffffff;
            --text-secondary: #a8a8a8;
            --background-dark: #0f0f23;
            --card-background: rgba(255, 255, 255, 0.05);
            --border-color: rgba(255, 255, 255, 0.1);
            --gradient-primary: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            --gradient-accent: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            --shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: var(--background-dark);
            color: var(--text-primary);
            line-height: 1.6;
            min-height: 100vh;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }

        .header {
            background: var(--gradient-primary);
            padding: 40px 20px;
            border-radius: 20px;
            margin-bottom: 30px;
            text-align: center;
            box-shadow: var(--shadow);
            position: relative;
            overflow: hidden;
        }

        .header::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><circle cx="20" cy="20" r="2" fill="white" opacity="0.1"/><circle cx="80" cy="40" r="1.5" fill="white" opacity="0.1"/><circle cx="40" cy="80" r="1" fill="white" opacity="0.1"/></svg>');
            pointer-events: none;
        }

        .header h1 {
            font-size: 2.8rem;
            font-weight: 700;
            margin-bottom: 10px;
            text-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
        }

        .header .subtitle {
            font-size: 1.2rem;
            opacity: 0.9;
            margin-bottom: 20px;
        }

        .status-badge {
            display: inline-block;
            padding: 8px 16px;
            background: rgba(255, 255, 255, 0.2);
            border-radius: 25px;
            font-size: 0.9rem;
            backdrop-filter: blur(10px);
        }

        .main-grid {
            display: grid;
            grid-template-columns: 1fr 350px;
            gap: 30px;
            margin-bottom: 30px;
        }

        .demo-section {
            background: var(--card-background);
            border-radius: 20px;
            padding: 30px;
            border: 1px solid var(--border-color);
            backdrop-filter: blur(10px);
            box-shadow: var(--shadow);
            position: relative;
        }

        .section-header {
            display: flex;
            align-items: center;
            margin-bottom: 25px;
        }

        .section-header i {
            font-size: 1.5rem;
            margin-right: 15px;
            color: var(--accent-color);
        }

        .section-header h3 {
            font-size: 1.5rem;
            font-weight: 600;
        }

        .query-interface {
            background: rgba(255, 255, 255, 0.02);
            border-radius: 15px;
            padding: 25px;
            border: 1px solid var(--border-color);
        }

        .form-group {
            margin-bottom: 20px;
        }

        .form-group label {
            display: block;
            margin-bottom: 8px;
            font-weight: 500;
            color: var(--text-secondary);
        }

        .form-control {
            width: 100%;
            padding: 12px 16px;
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid var(--border-color);
            border-radius: 10px;
            color: var(--text-primary);
            font-size: 1rem;
            transition: all 0.3s ease;
        }

        .form-control:focus {
            outline: none;
            border-color: var(--accent-color);
            box-shadow: 0 0 0 3px rgba(233, 69, 96, 0.2);
            background: rgba(255, 255, 255, 0.08);
        }

        .form-control::placeholder {
            color: var(--text-secondary);
        }

        .form-row {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
        }

        .btn {
            padding: 14px 28px;
            border: none;
            border-radius: 25px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 1px;
            position: relative;
            overflow: hidden;
        }

        .btn-primary {
            background: var(--gradient-accent);
            color: white;
        }

        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(233, 69, 96, 0.4);
        }

        .btn-secondary {
            background: rgba(255, 255, 255, 0.1);
            color: var(--text-primary);
            border: 1px solid var(--border-color);
        }

        .btn-secondary:hover {
            background: rgba(255, 255, 255, 0.2);
            transform: translateY(-2px);
        }

        .btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none !important;
        }

        .sidebar {
            display: flex;
            flex-direction: column;
            gap: 20px;
        }

        .status-card {
            background: var(--card-background);
            border-radius: 15px;
            padding: 20px;
            border: 1px solid var(--border-color);
            backdrop-filter: blur(10px);
        }

        .status-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }

        .stat-item {
            background: rgba(255, 255, 255, 0.03);
            padding: 15px;
            border-radius: 10px;
            text-align: center;
            border: 1px solid var(--border-color);
        }

        .stat-value {
            font-size: 1.5rem;
            font-weight: 700;
            color: var(--accent-color);
            margin-bottom: 5px;
        }

        .stat-label {
            font-size: 0.85rem;
            color: var(--text-secondary);
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .result-container {
            margin-top: 25px;
        }

        .result-card {
            background: var(--card-background);
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 20px;
            border: 1px solid var(--border-color);
            backdrop-filter: blur(10px);
            animation: slideIn 0.3s ease;
        }

        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .result-header {
            display: flex;
            justify-content: between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 1px solid var(--border-color);
        }

        .result-status {
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .status-safe {
            background: rgba(39, 174, 96, 0.2);
            color: #27ae60;
            border: 1px solid rgba(39, 174, 96, 0.3);
        }

        .status-flagged {
            background: rgba(231, 76, 60, 0.2);
            color: #e74c3c;
            border: 1px solid rgba(231, 76, 60, 0.3);
        }

        .response-content {
            background: rgba(255, 255, 255, 0.02);
            border-radius: 10px;
            padding: 20px;
            border-left: 4px solid var(--accent-color);
            font-family: 'Consolas', monospace;
            line-height: 1.7;
        }

        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }

        .metric-item {
            background: rgba(255, 255, 255, 0.03);
            padding: 12px;
            border-radius: 8px;
            text-align: center;
        }

        .loading {
            text-align: center;
            padding: 40px 20px;
            color: var(--text-secondary);
        }

        .loading i {
            font-size: 2rem;
            animation: spin 2s linear infinite;
            color: var(--accent-color);
            margin-bottom: 15px;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        .example-queries {
            margin-top: 20px;
        }

        .example-item {
            background: rgba(255, 255, 255, 0.02);
            padding: 12px 16px;
            margin: 8px 0;
            border-radius: 8px;
            border-left: 3px solid var(--accent-color);
            cursor: pointer;
            transition: all 0.2s ease;
        }

        .example-item:hover {
            background: rgba(255, 255, 255, 0.05);
            transform: translateX(5px);
        }

        .example-domain {
            font-weight: 600;
            color: var(--accent-color);
            font-size: 0.85rem;
        }

        .error-card {
            background: rgba(231, 76, 60, 0.1);
            border: 1px solid rgba(231, 76, 60, 0.3);
            color: #e74c3c;
        }

        .about-section {
            background: var(--card-background);
            border-radius: 20px;
            padding: 30px;
            margin-top: 30px;
            border: 1px solid var(--border-color);
            backdrop-filter: blur(10px);
        }

        .feature-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 25px;
        }

        .feature-card {
            background: rgba(255, 255, 255, 0.03);
            padding: 20px;
            border-radius: 15px;
            border: 1px solid var(--border-color);
        }

        .feature-icon {
            font-size: 2rem;
            color: var(--accent-color);
            margin-bottom: 15px;
        }

        @media (max-width: 768px) {
            .main-grid {
                grid-template-columns: 1fr;
            }
            
            .form-row {
                grid-template-columns: 1fr;
            }
            
            .container {
                padding: 15px;
            }
            
            .header h1 {
                font-size: 2rem;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <header class="header">
            <h1><i class="fas fa-brain"></i> ADP Protocol</h1>
            <p class="subtitle">Alignment Delegation Protocol - Intelligent AI Model Routing</p>
            <div class="status-badge">
                <i class="fas fa-satellite-dish"></i> Live Demo v2.0
            </div>
        </header>

        <div class="main-grid">
            <main class="demo-section">
                <div class="section-header">
                    <i class="fas fa-rocket"></i>
                    <h3>Query Delegation Interface</h3>
                </div>

                <div class="query-interface">
                    <form id="queryForm">
                        <div class="form-group">
                            <label for="query">
                                <i class="fas fa-comment-dots"></i> Enter Your Query
                            </label>
                            <input 
                                type="text" 
                                id="query" 
                                class="form-control"
                                placeholder="e.g., 'What are the symptoms of chest pain?' or 'Analyze network security risks'"
                                required
                            >
                        </div>

                        <div class="form-row">
                            <div class="form-group">
                                <label for="domain">
                                    <i class="fas fa-tags"></i> Domain
                                </label>
                                <select id="domain" class="form-control">
                                    <option value="medical">🏥 Medical</option>
                                    <option value="legal">⚖️ Legal</option>
                                    <option value="technical">💻 Technical</option>
                                    <option value="financial">💰 Financial</option>
                                </select>
                            </div>

                            <div class="form-group">
                                <label for="priority">
                                    <i class="fas fa-exclamation-triangle"></i> Priority
                                </label>
                                <select id="priority" class="form-control">
                                    <option value="normal">📋 Normal</option>
                                    <option value="high">⚡ High</option>
                                    <option value="urgent">🚨 Urgent</option>
                                </select>
                            </div>
                        </div>

                        <button type="submit" class="btn btn-primary" id="submitBtn">
                            <i class="fas fa-paper-plane"></i> Delegate Query
                        </button>
                    </form>

                    <div class="example-queries">
                        <h4><i class="fas fa-lightbulb"></i> Example Queries</h4>
                        <div class="example-item" onclick="fillExample('What are the symptoms of chest pain?', 'medical')">
                            <div class="example-domain">MEDICAL</div>
                            <div>What are the symptoms of chest pain?</div>
                        </div>
                        <div class="example-item" onclick="fillExample('Review contract compliance requirements', 'legal')">
                            <div class="example-domain">LEGAL</div>
                            <div>Review contract compliance requirements</div>
                        </div>
                        <div class="example-item" onclick="fillExample('Analyze network security vulnerabilities', 'technical')">
                            <div class="example-domain">TECHNICAL</div>
                            <div>Analyze network security vulnerabilities</div>
                        </div>
                        <div class="example-item" onclick="fillExample('Assess investment risk factors', 'financial')">
                            <div class="example-domain">FINANCIAL</div>
                            <div>Assess investment risk factors</div>
                        </div>
                    </div>
                </div>

                <div id="queryResult"></div>
            </main>

            <aside class="sidebar">
                <div class="status-card">
                    <div class="section-header">
                        <i class="fas fa-chart-line"></i>
                        <h4>System Status</h4>
                    </div>
                    <button onclick="loadStatus()" class="btn btn-secondary">
                        <i class="fas fa-sync-alt"></i> Refresh
                    </button>
                    <div id="statusDisplay">
                        <div class="loading">
                            <div><i class="fas fa-spinner"></i></div>
                            <div>Click refresh to load status</div>
                        </div>
                    </div>
                </div>
            </aside>
        </div>

        <section class="about-section">
            <div class="section-header">
                <i class="fas fa-info-circle"></i>
                <h3>About ADP Protocol v2.0</h3>
            </div>
            
            <div class="feature-grid">
                <div class="feature-card">
                    <div class="feature-icon"><i class="fas fa-route"></i></div>
                    <h4>Intelligent Routing</h4>
                    <p>Advanced algorithms select optimal Narrow Models based on domain expertise, current load, and historical performance metrics.</p>
                </div>
                
                <div class="feature-card">
                    <div class="feature-icon"><i class="fas fa-shield-alt"></i></div>
                    <h4>Alignment Monitoring</h4>
                    <p>Real-time safety assessment with bias detection, hallucination prevention, and harm potential evaluation.</p>
                </div>
                
                <div class="feature-card">
                    <div class="feature-icon"><i class="fas fa-balance-scale"></i></div>
                    <h4>Load Balancing</h4>
                    <p>Dynamic workload distribution using round-robin, weighted selection, and performance-based routing strategies.</p>
                </div>
                
                <div class="feature-card">
                    <div class="feature-icon"><i class="fas fa-eye"></i></div>
                    <h4>Transparency</h4>
                    <p>Complete audit trail of all delegation decisions with comprehensive logging to Coordination Agents.</p>
                </div>
            </div>
        </section>
    </div>

    <script>
        // Global state
        let isProcessing = false;

        // Form submission handler
        document.getElementById('queryForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            if (isProcessing) return;
            
            const query = document.getElementById('query').value.trim();
            const domain = document.getElementById('domain').value;
            const priority = document.getElementById('priority').value;
            
            if (!query) return;
            
            isProcessing = true;
            updateSubmitButton(true);
            
            const resultDiv = document.getElementById('queryResult');
            resultDiv.innerHTML = `
                <div class="result-card">
                    <div class="loading">
                        <div><i class="fas fa-cogs"></i></div>
                        <div>Processing query through ADP network...</div>
                        <div style="font-size: 0.9rem; margin-top: 10px;">Routing → Analysis → Validation → Response</div>
                    </div>
                </div>
            `;
            
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
                    resultDiv.innerHTML = `
                        <div class="result-card error-card">
                            <div class="result-header">
                                <h4><i class="fas fa-exclamation-triangle"></i> Error</h4>
                            </div>
                            <div>${result.error}</div>
                        </div>
                    `;
                } else {
                    displayResult(result, query, domain, priority);
                }
            } catch (error) {
                resultDiv.innerHTML = `
                    <div class="result-card error-card">
                        <div class="result-header">
                            <h4><i class="fas fa-wifi"></i> Connection Error</h4>
                        </div>
                        <div>Failed to connect to ADP network: ${error.message}</div>
                    </div>
                `;
            } finally {
                isProcessing = false;
                updateSubmitButton(false);
            }
        });

        function updateSubmitButton(processing) {
            const btn = document.getElementById('submitBtn');
            if (processing) {
                btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
                btn.disabled = true;
            } else {
                btn.innerHTML = '<i class="fas fa-paper-plane"></i> Delegate Query';
                btn.disabled = false;
            }
        }

        function displayResult(result, query, domain, priority) {
            const summary = result.summary;
            const alignmentStatus = summary.alignment_status.includes('SAFE') ? 'safe' : 'flagged';
            
            document.getElementById('queryResult').innerHTML = `
                <div class="result-container">
                    <div class="result-card">
                        <div class="result-header">
                            <h4><i class="fas fa-chart-bar"></i> Delegation Summary</h4>
                            <div class="result-status status-${alignmentStatus}">
                                <i class="fas fa-${alignmentStatus === 'safe' ? 'check-circle' : 'exclamation-triangle'}"></i>
                                ${summary.alignment_status}
                            </div>
                        </div>
                        
                        <div class="metrics-grid">
                            <div class="metric-item">
                                <div class="stat-value">${summary.primary_nm}</div>
                                <div class="stat-label">Primary NM</div>
                            </div>
                            <div class="metric-item">
                                <div class="stat-value">${summary.primary_confidence}</div>
                                <div class="stat-label">Confidence</div>
                            </div>
                            <div class="metric-item">
                                <div class="stat-value">${summary.processing_time}</div>
                                <div class="stat-label">Processing</div>
                            </div>
                            ${summary.validation_count > 0 ? `
                            <div class="metric-item">
                                <div class="stat-value">${summary.validation_count}</div>
                                <div class="stat-label">Validators</div>
                            </div>` : ''}
                        </div>
                    </div>
                    
                    <div class="result-card">
                        <div class="result-header">
                            <h4><i class="fas fa-robot"></i> Primary Response</h4>
                            <small>From: ${summary.primary_nm}</small>
                        </div>
                        <div class="response-content">
                            ${result.primary_response.payload.response_content}
                        </div>
                    </div>
                    
                    <div class="result-card">
                        <div class="result-header">
                            <h4><i class="fas fa-cogs"></i> Technical Details</h4>
                        </div>
                        <div class="metrics-grid">
                            <div class="metric-item">
                                <div class="stat-value">${result.routing.routing_method}</div>
                                <div class="stat-label">Routing Method</div>
                            </div>
                            <div class="metric-item">
                                <div class="stat-value">${result.routing.total_available || 'N/A'}</div>
                                <div class="stat-label">Available NMs</div>
                            </div>
                        </div>
                        
                        <details style="margin-top: 20px;">
                            <summary style="cursor: pointer; padding: 10px; background: rgba(255,255,255,0.05); border-radius: 5px;">
                                <i class="fas fa-code"></i> View Full JSON Response
                            </summary>
                            <pre style="margin-top: 15px; background: rgba(0,0,0,0.3); padding: 15px; border-radius: 8px; font-size: 0.85rem; overflow-x: auto;">${JSON.stringify(result, null, 2)}</pre>
                        </details>
                    </div>
                </div>
            `;
        }

        function fillExample(query, domain) {
            document.getElementById('query').value = query;
            document.getElementById('domain').value = domain;
            document.getElementById('query').focus();
        }

        async function loadStatus() {
            const statusDiv = document.getElementById('statusDisplay');
            statusDiv.innerHTML = `
                <div class="loading">
                    <div><i class="fas fa-spinner"></i></div>
                    <div>Loading system status...</div>
                </div>
            `;
            
            try {
                const response = await fetch('/api/status');
                const data = await response.json();
                
                statusDiv.innerHTML = `
                    <div class="status-grid">
                        <div class="stat-item">
                            <div class="stat-value">${data.routing_stats.total_nms}</div>
                            <div class="stat-label">Total NMs</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-value">${(data.routing_stats.overall_health * 100).toFixed(0)}%</div>
                            <div class="stat-label">Health</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-value">${data.ca_logs}</div>
                            <div class="stat-label">CA Logs</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-value">${data.total_transactions}</div>
                            <div class="stat-label">Transactions</div>
                        </div>
                    </div>
                    
                    <div style="margin-top: 20px;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                            <span>System Status:</span>
                            <span style="font-weight: bold; color: ${data.system_health.includes('HEALTHY') ? '#27ae60' : data.system_health.includes('DEGRADED') ? '#f39c12' : '#e74c3c'};">
                                ${data.system_health}
                            </span>
                        </div>
                        <div style="font-size: 0.85rem; color: var(--text-secondary);">
                            Last updated: ${new Date(data.timestamp).toLocaleString()}
                        </div>
                    </div>
                `;
            } catch (error) {
                statusDiv.innerHTML = `
                    <div style="text-align: center; color: var(--danger-color); padding: 20px;">
                        <i class="fas fa-exclamation-triangle"></i><br>
                        Error loading status<br>
                        <small>${error.message}</small>
                    </div>
                `;
            }
        }

        // Auto-load status on page load
        window.addEventListener('load', function() {
            setTimeout(loadStatus, 500);
        });
    </script>
</body>
</html>"""

@app.route('/')
def home():
    """Serve the enhanced demo page"""
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
    return jsonify({
        "status": "healthy", 
        "service": "adp-demo-v2",
        "version": "2.0",
        "timestamp": mc.get_system_status()["timestamp"]
    })

@app.route('/api/examples')
def get_examples():
    """API endpoint for example queries"""
    examples = {
        "medical": [
            "What are the symptoms of chest pain?",
            "Explain the side effects of blood pressure medication",
            "What should I know about diabetes management?",
            "How is pneumonia diagnosed and treated?"
        ],
        "legal": [
            "Review contract compliance requirements",
            "What are the key elements of a valid contract?",
            "Explain intellectual property protection basics",
            "What are employment law considerations for remote work?"
        ],
        "technical": [
            "Analyze network security vulnerabilities",
            "Explain best practices for data encryption",
            "What are the latest cybersecurity threats?",
            "How to implement secure API authentication?"
        ],
        "financial": [
            "Assess investment risk factors",
            "Explain portfolio diversification strategies",
            "What are the implications of market volatility?",
            "How does inflation affect investment returns?"
        ]
    }
    return jsonify(examples)

if __name__ == '__main__':
    # Use PORT environment variable (required for Render)
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)