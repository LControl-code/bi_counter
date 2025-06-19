#!/usr/bin/env python3
"""
Modern Professional BI Counter Approval Interface
Enhanced with contemporary design, improved UX, and professional aesthetics
Fixed: Removed auto-refresh, Fixed batch approve functionality
"""

import sys
import logging
from datetime import datetime
from flask import (
    Flask,
    render_template_string,
    request,
    redirect,
    url_for,
    flash,
    jsonify,
    session,
)
from functools import wraps
import secrets

# Import the configurable counter class
from main import BinarySearchFileCounter

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

# Global variable to store config file path
CONFIG_FILE = "config.json"

# Simple authentication (replace with proper auth in production)
USERS = {
    "quality": "quality123",
    "admin": "admin123",
}


def require_auth(f):
    """Authentication decorator"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)

    return decorated_function


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username in USERS and USERS[username] == password:
            session["user"] = username
            flash(f"Welcome {username}!", "success")
            return redirect(url_for("index"))
        else:
            flash("Invalid credentials", "error")

    return render_template_string("""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>BI Counter - Secure Login</title>
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 20px;
            }
            
            .login-container {
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(20px);
                border-radius: 20px;
                padding: 48px;
                width: 100%;
                max-width: 420px;
                box-shadow: 0 25px 50px rgba(0, 0, 0, 0.15);
                border: 1px solid rgba(255, 255, 255, 0.2);
            }
            
            .logo {
                text-align: center;
                margin-bottom: 32px;
            }
            
            .logo-icon {
                width: 64px;
                height: 64px;
                background: linear-gradient(135deg, #667eea, #764ba2);
                border-radius: 16px;
                display: inline-flex;
                align-items: center;
                justify-content: center;
                font-size: 24px;
                color: white;
                margin-bottom: 16px;
            }
            
            .logo h1 {
                font-size: 24px;
                font-weight: 700;
                color: #1a202c;
                margin-bottom: 8px;
            }
            
            .logo p {
                color: #718096;
                font-size: 14px;
                font-weight: 400;
            }
            
            .form-group {
                margin-bottom: 24px;
            }
            
            .form-group label {
                display: block;
                margin-bottom: 8px;
                font-weight: 500;
                color: #2d3748;
                font-size: 14px;
            }
            
            .form-group input {
                width: 100%;
                padding: 16px;
                border: 2px solid #e2e8f0;
                border-radius: 12px;
                font-size: 16px;
                font-family: inherit;
                background: white;
                transition: all 0.2s ease;
            }
            
            .form-group input:focus {
                outline: none;
                border-color: #667eea;
                box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
            }
            
            .btn-login {
                width: 100%;
                padding: 16px;
                background: linear-gradient(135deg, #667eea, #764ba2);
                color: white;
                border: none;
                border-radius: 12px;
                font-size: 16px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.2s ease;
                font-family: inherit;
            }
            
            .btn-login:hover {
                transform: translateY(-2px);
                box-shadow: 0 10px 25px rgba(102, 126, 234, 0.3);
            }
            
            .btn-login:active {
                transform: translateY(0);
            }
            
            .flash-messages {
                margin-bottom: 24px;
            }
            
            .flash-error {
                background: #fed7d7;
                color: #c53030;
                padding: 12px 16px;
                border-radius: 8px;
                border-left: 4px solid #e53e3e;
                font-size: 14px;
            }
            
            .flash-success {
                background: #c6f6d5;
                color: #2f855a;
                padding: 12px 16px;
                border-radius: 8px;
                border-left: 4px solid #38a169;
                font-size: 14px;
            }
            
            .demo-credentials {
                margin-top: 32px;
                padding: 16px;
                background: #f7fafc;
                border-radius: 12px;
                border: 1px solid #e2e8f0;
            }
            
            .demo-credentials h4 {
                color: #2d3748;
                font-size: 12px;
                font-weight: 600;
                margin-bottom: 8px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            
            .demo-credentials p {
                color: #718096;
                font-size: 13px;
                margin-bottom: 4px;
            }
        </style>
    </head>
    <body>
        <div class="login-container">
            <div class="logo">
                <div class="logo-icon">🔧</div>
                <h1>BI Counter</h1>
                <p>Quality Management Portal</p>
            </div>
            
            <div class="flash-messages">
                {% with messages = get_flashed_messages(with_categories=true) %}
                    {% if messages %}
                        {% for category, message in messages %}
                            <div class="flash-{{ category }}">{{ message }}</div>
                        {% endfor %}
                    {% endif %}
                {% endwith %}
            </div>
            
            <form method="post">
                <div class="form-group">
                    <label for="username">Username</label>
                    <input type="text" id="username" name="username" required autocomplete="username">
                </div>
                <div class="form-group">
                    <label for="password">Password</label>
                    <input type="password" id="password" name="password" required autocomplete="current-password">
                </div>
                <button type="submit" class="btn-login">Sign In</button>
            </form>
            
            <div class="demo-credentials">
                <h4>Demo Credentials</h4>
                <p><strong>quality</strong> / quality123</p>
                <p><strong>admin</strong> / admin123</p>
            </div>
        </div>
    </body>
    </html>
    """)


@app.route("/logout")
def logout():
    session.pop("user", None)
    flash("Signed out successfully", "success")
    return redirect(url_for("login"))


# Modern Professional Approval Interface Template
MODERN_APPROVAL_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BI Counter - Quality Management Dashboard</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary-50: #eff6ff;
            --primary-100: #dbeafe;
            --primary-500: #3b82f6;
            --primary-600: #2563eb;
            --primary-700: #1d4ed8;
            --primary-900: #1e3a8a;
            
            --success-50: #f0fdf4;
            --success-100: #dcfce7;
            --success-500: #22c55e;
            --success-600: #16a34a;
            --success-700: #15803d;
            
            --warning-50: #fffbeb;
            --warning-100: #fef3c7;
            --warning-500: #f59e0b;
            --warning-600: #d97706;
            --warning-700: #b45309;
            
            --error-50: #fef2f2;
            --error-100: #fee2e2;
            --error-500: #ef4444;
            --error-600: #dc2626;
            --error-700: #b91c1c;
            
            --neutral-50: #f8fafc;
            --neutral-100: #f1f5f9;
            --neutral-200: #e2e8f0;
            --neutral-300: #cbd5e1;
            --neutral-400: #94a3b8;
            --neutral-500: #64748b;
            --neutral-600: #475569;
            --neutral-700: #334155;
            --neutral-800: #1e293b;
            --neutral-900: #0f172a;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: var(--neutral-50);
            color: var(--neutral-900);
            line-height: 1.6;
            min-height: 100vh;
        }
        
        .container {
            max-width: 1440px;
            margin: 0 auto;
            padding: 0 24px;
        }
        
        /* Header Styles */
        .header {
            background: linear-gradient(135deg, var(--primary-600), var(--primary-700));
            color: white;
            padding: 24px 0;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
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
            background: url('data:image/svg+xml,<svg width="60" height="60" viewBox="0 0 60 60" xmlns="http://www.w3.org/2000/svg"><g fill="none" fill-rule="evenodd"><g fill="%23ffffff" fill-opacity="0.05"><circle cx="30" cy="30" r="30"/></g></svg>') repeat;
            opacity: 0.1;
        }
        
        .header-content {
            position: relative;
            z-index: 1;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 16px;
        }
        
        .header-left {
            display: flex;
            align-items: center;
            gap: 16px;
        }
        
        .logo {
            display: flex;
            align-items: center;
            gap: 12px;
        }
        
        .logo-icon {
            width: 48px;
            height: 48px;
            background: rgba(255, 255, 255, 0.2);
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 20px;
        }
        
        .logo-text h1 {
            font-size: 24px;
            font-weight: 700;
            margin-bottom: 2px;
        }
        
        .logo-text p {
            font-size: 14px;
            opacity: 0.9;
        }
        
        .header-right {
            display: flex;
            align-items: center;
            gap: 24px;
        }
        
        .user-info {
            display: flex;
            align-items: center;
            gap: 12px;
            font-size: 14px;
        }
        
        .user-avatar {
            width: 32px;
            height: 32px;
            background: rgba(255, 255, 255, 0.2);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 14px;
        }
        
        .logout-btn {
            color: white;
            text-decoration: none;
            padding: 8px 16px;
            border-radius: 8px;
            background: rgba(255, 255, 255, 0.1);
            transition: all 0.2s ease;
            font-size: 14px;
            font-weight: 500;
        }
        
        .logout-btn:hover {
            background: rgba(255, 255, 255, 0.2);
            transform: translateY(-1px);
        }
        
        .refresh-btn {
            color: white;
            text-decoration: none;
            padding: 8px 16px;
            border-radius: 8px;
            background: rgba(255, 255, 255, 0.1);
            transition: all 0.2s ease;
            font-size: 14px;
            font-weight: 500;
            border: none;
            cursor: pointer;
        }
        
        .refresh-btn:hover {
            background: rgba(255, 255, 255, 0.2);
            transform: translateY(-1px);
        }
        
        .last-update {
            font-size: 13px;
            opacity: 0.8;
            margin-top: 8px;
        }
        
        /* Status Banner */
        .status-banner {
            background: var(--primary-50);
            border: 1px solid var(--primary-200);
            border-radius: 12px;
            padding: 16px 24px;
            margin: 24px 0;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 12px;
        }
        
        .mode-indicator {
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .mode-production { background: var(--error-100); color: var(--error-700); }
        .mode-test { background: var(--warning-100); color: var(--warning-700); }
        .mode-dev { background: var(--success-100); color: var(--success-700); }
        
        /* Statistics Cards */
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 24px;
            margin-bottom: 32px;
        }
        
        .stat-card {
            background: white;
            border-radius: 16px;
            padding: 24px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
            border: 1px solid var(--neutral-200);
            transition: all 0.2s ease;
            position: relative;
            overflow: hidden;
        }
        
        .stat-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(135deg, var(--primary-500), var(--primary-600));
        }
        
        .stat-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        }
        
        .stat-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 16px;
        }
        
        .stat-icon {
            width: 48px;
            height: 48px;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 20px;
            color: white;
        }
        
        .stat-icon.pending { background: linear-gradient(135deg, var(--warning-500), var(--warning-600)); }
        .stat-icon.devices { background: linear-gradient(135deg, var(--primary-500), var(--primary-600)); }
        .stat-icon.approved { background: linear-gradient(135deg, var(--success-500), var(--success-600)); }
        
        .stat-number {
            font-size: 32px;
            font-weight: 700;
            color: var(--neutral-900);
            line-height: 1;
        }
        
        .stat-label {
            color: var(--neutral-600);
            font-size: 14px;
            font-weight: 500;
            margin-top: 4px;
        }
        
        /* Main Content Cards */
        .content-card {
            background: white;
            border-radius: 16px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
            border: 1px solid var(--neutral-200);
            margin-bottom: 32px;
            overflow: hidden;
        }
        
        .card-header {
            padding: 24px 32px;
            border-bottom: 1px solid var(--neutral-200);
            background: var(--neutral-50);
        }
        
        .card-title {
            display: flex;
            align-items: center;
            gap: 12px;
            font-size: 20px;
            font-weight: 600;
            color: var(--neutral-900);
        }
        
        .card-subtitle {
            color: var(--neutral-600);
            font-size: 14px;
            margin-top: 4px;
        }
        
        .card-content {
            padding: 32px;
        }
        
        /* Bulk Actions */
        .bulk-actions {
            background: linear-gradient(135deg, var(--neutral-800), var(--neutral-900));
            color: white;
            padding: 20px 32px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 16px;
        }
        
        .bulk-actions-left {
            display: flex;
            align-items: center;
            gap: 16px;
        }
        
        .bulk-actions-right {
            display: flex;
            align-items: center;
            gap: 12px;
        }
        
        .bulk-btn {
            padding: 10px 20px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 500;
            transition: all 0.2s ease;
        }
        
        .bulk-approve {
            background: var(--success-500);
            color: white;
        }
        
        .bulk-approve:hover {
            background: var(--success-600);
            transform: translateY(-1px);
        }
        
        .bulk-reject {
            background: var(--error-500);
            color: white;
        }
        
        .bulk-reject:hover {
            background: var(--error-600);
            transform: translateY(-1px);
        }
        
        .bulk-input {
            padding: 10px 16px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 8px;
            background: rgba(255, 255, 255, 0.1);
            color: white;
            font-size: 14px;
        }
        
        .bulk-input::placeholder {
            color: rgba(255, 255, 255, 0.7);
        }
        
        /* Approval Items */
        .approval-item {
            background: white;
            border: 1px solid var(--neutral-200);
            border-radius: 12px;
            margin-bottom: 24px;
            position: relative;
            transition: all 0.2s ease;
            overflow: hidden;
        }
        
        .approval-item::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            bottom: 0;
            width: 4px;
            background: linear-gradient(135deg, var(--warning-500), var(--warning-600));
        }
        
        .approval-item:hover {
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
            transform: translateY(-1px);
        }
        
        .approval-header {
            padding: 24px 32px 16px;
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
        }
        
        .approval-checkbox {
            width: 20px;
            height: 20px;
            border-radius: 4px;
            border: 2px solid var(--neutral-300);
            cursor: pointer;
            transition: all 0.2s ease;
        }
        
        .approval-checkbox:checked {
            background: var(--primary-500);
            border-color: var(--primary-500);
        }
        
        .device-info h3 {
            font-size: 18px;
            font-weight: 600;
            color: var(--neutral-900);
            margin-bottom: 8px;
        }
        
        .tier-transition {
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 16px;
        }
        
        .tier-badge {
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .tier-24 { background: var(--error-100); color: var(--error-700); }
        .tier-12 { background: var(--warning-100); color: var(--warning-700); }
        .tier-6 { background: #fef3c7; color: #92400e; }
        .tier-3 { background: var(--primary-100); color: var(--primary-700); }
        .tier-2 { background: var(--success-100); color: var(--success-700); }
        
        .tier-arrow {
            font-size: 18px;
            color: var(--neutral-400);
        }
        
        .approval-details {
            padding: 0 32px 16px;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
        }
        
        .detail-item {
            padding: 16px;
            background: var(--neutral-50);
            border-radius: 8px;
            border: 1px solid var(--neutral-200);
        }
        
        .detail-label {
            font-size: 12px;
            font-weight: 600;
            color: var(--neutral-600);
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 4px;
        }
        
        .detail-value {
            font-size: 14px;
            font-weight: 500;
            color: var(--neutral-900);
        }
        
        .approval-actions {
            padding: 24px 32px;
            border-top: 1px solid var(--neutral-200);
            background: var(--neutral-50);
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 16px;
            flex-wrap: wrap;
        }
        
        .action-form {
            display: flex;
            align-items: center;
            gap: 12px;
        }
        
        .approver-input {
            padding: 10px 16px;
            border: 1px solid var(--neutral-300);
            border-radius: 8px;
            font-size: 14px;
            min-width: 180px;
        }
        
        .approver-input:focus {
            outline: none;
            border-color: var(--primary-500);
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
        }
        
        .action-btn {
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 600;
            transition: all 0.2s ease;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .btn-approve {
            background: var(--success-500);
            color: white;
        }
        
        .btn-approve:hover {
            background: var(--success-600);
            transform: translateY(-1px);
        }
        
        .btn-reject {
            background: var(--error-500);
            color: white;
        }
        
        .btn-reject:hover {
            background: var(--error-600);
            transform: translateY(-1px);
        }
        
        /* Device Status Table */
        .device-table {
            width: 100%;
            border-collapse: collapse;
        }
        
        .device-table th {
            background: var(--neutral-50);
            padding: 16px;
            text-align: left;
            font-weight: 600;
            color: var(--neutral-700);
            font-size: 14px;
            border-bottom: 2px solid var(--neutral-200);
        }
        
        .device-table td {
            padding: 16px;
            border-bottom: 1px solid var(--neutral-200);
            font-size: 14px;
        }
        
        .device-table tr:hover {
            background: var(--neutral-50);
        }
        
        .device-name {
            font-weight: 600;
            color: var(--neutral-900);
        }
        
        .count-value {
            font-size: 18px;
            font-weight: 700;
            color: var(--primary-600);
        }
        
        .progress-container {
            width: 200px;
            height: 8px;
            background: var(--neutral-200);
            border-radius: 4px;
            overflow: hidden;
            position: relative;
            margin-bottom: 4px;
        }
        
        .progress-bar {
            height: 100%;
            border-radius: 4px;
            transition: width 0.3s ease;
        }
        
        .progress-text {
            font-size: 12px;
            font-weight: 500;
            color: var(--neutral-600);
        }
        
        .status-badge {
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 500;
            display: inline-flex;
            align-items: center;
            gap: 4px;
        }
        
        .status-pending { background: var(--warning-100); color: var(--warning-700); }
        .status-approved { background: var(--success-100); color: var(--success-700); }
        .status-rejected { background: var(--error-100); color: var(--error-700); }
        .status-counting { background: var(--primary-100); color: var(--primary-700); }
        
        /* Empty State */
        .empty-state {
            text-align: center;
            padding: 64px 32px;
        }
        
        .empty-icon {
            width: 80px;
            height: 80px;
            background: var(--success-100);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 32px;
            color: var(--success-600);
            margin: 0 auto 24px;
        }
        
        .empty-title {
            font-size: 20px;
            font-weight: 600;
            color: var(--neutral-900);
            margin-bottom: 8px;
        }
        
        .empty-description {
            color: var(--neutral-600);
            font-size: 16px;
        }
        
        /* History Items */
        .history-item {
            padding: 16px 0;
            border-bottom: 1px solid var(--neutral-200);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .history-item:last-child {
            border-bottom: none;
        }
        
        .history-main {
            font-weight: 500;
            color: var(--neutral-900);
        }
        
        .history-meta {
            font-size: 14px;
            color: var(--neutral-600);
        }
        
        /* Responsive Design */
        @media (max-width: 768px) {
            .container {
                padding: 0 16px;
            }
            
            .header-content {
                flex-direction: column;
                text-align: center;
            }
            
            .stats-grid {
                grid-template-columns: 1fr;
            }
            
            .card-content {
                padding: 24px 16px;
            }
            
            .approval-header,
            .approval-details,
            .approval-actions {
                padding-left: 16px;
                padding-right: 16px;
            }
            
            .bulk-actions {
                flex-direction: column;
                align-items: stretch;
            }
            
            .device-table {
                font-size: 12px;
            }
            
            .device-table th,
            .device-table td {
                padding: 12px 8px;
            }
        }
    </style>
</head>
<body>
    <header class="header">
        <div class="container">
            <div class="header-content">
                <div class="header-left">
                    <div class="logo">
                        <div class="logo-icon">🔧</div>
                        <div class="logo-text">
                            <h1>BI Counter</h1>
                            <p>Quality Management Dashboard</p>
                        </div>
                    </div>
                </div>
                <div class="header-right">
                    <button class="refresh-btn" onclick="location.reload()">🔄 Refresh</button>
                    <div class="user-info">
                        <div class="user-avatar">👤</div>
                        <span>{{ current_user }}</span>
                        <a href="{{ url_for('logout') }}" class="logout-btn">Sign Out</a>
                    </div>
                </div>
            </div>
            <div class="last-update">
                Last updated: {{ last_update }}
            </div>
        </div>
    </header>

    <main class="container">
        <div class="status-banner">
            📁 Configuration: <strong>{{ config_file }}</strong>
            <span class="mode-indicator mode-{{ mode_class }}">{{ mode_text }}</span>
        </div>

        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-header">
                    <div>
                        <div class="stat-number">{{ pending_count }}</div>
                        <div class="stat-label">Pending Approvals</div>
                    </div>
                    <div class="stat-icon pending">⏳</div>
                </div>
            </div>
            <div class="stat-card">
                <div class="stat-header">
                    <div>
                        <div class="stat-number">{{ devices_count }}</div>
                        <div class="stat-label">Active Devices</div>
                    </div>
                    <div class="stat-icon devices">📱</div>
                </div>
            </div>
            <div class="stat-card">
                <div class="stat-header">
                    <div>
                        <div class="stat-number">{{ approved_today }}</div>
                        <div class="stat-label">Approved Today</div>
                    </div>
                    <div class="stat-icon approved">✅</div>
                </div>
            </div>
        </div>

        <div class="content-card">
            <div class="card-header">
                <div class="card-title">
                    📋 Tier Advancement Approvals
                </div>
                <div class="card-subtitle">Review and approve device tier advancements</div>
            </div>
            
            {% if pending_approvals %}
            <div class="bulk-actions">
                <div class="bulk-actions-left">
                    <strong>Bulk Operations:</strong>
                </div>
                <div class="bulk-actions-right">
                    <input type="text" id="bulk-approver" placeholder="Enter your name" class="bulk-input">
                    <button type="button" class="bulk-btn bulk-approve" onclick="bulkAction('APPROVE')">
                        ✅ Approve Selected
                    </button>
                    <button type="button" class="bulk-btn bulk-reject" onclick="bulkAction('REJECT')">
                        ❌ Reject Selected
                    </button>
                </div>
            </div>
            {% endif %}
            
            <div class="card-content">
                {% if pending_approvals %}
                    {% for approval_id, approval in pending_approvals.items() %}
                        <div class="approval-item">
                            <div class="approval-header">
                                <div class="device-info">
                                    <h3>{{ approval.device_name }}</h3>
                                    <div class="tier-transition">
                                        <span class="tier-badge tier-{{ approval.current_tier.replace('h', '') }}">
                                            {{ approval.current_tier }}
                                        </span>
                                        <span class="tier-arrow">→</span>
                                        <span class="tier-badge tier-{{ approval.proposed_tier.replace('h', '') }}">
                                            {{ approval.proposed_tier }}
                                        </span>
                                    </div>
                                </div>
                                <input type="checkbox" class="approval-checkbox" name="selected_approvals" value="{{ approval_id }}">
                            </div>
                            
                            <div class="approval-details">
                                <div class="detail-item">
                                    <div class="detail-label">Approval ID</div>
                                    <div class="detail-value">{{ approval_id }}</div>
                                </div>
                                <div class="detail-item">
                                    <div class="detail-label">Unit Count</div>
                                    <div class="detail-value">{{ approval.unit_count }} units</div>
                                </div>
                                <div class="detail-item">
                                    <div class="detail-label">Request Date</div>
                                    <div class="detail-value">{{ approval.request_date[:19] }}</div>
                                </div>
                            </div>
                            
                            <div class="approval-actions">
                                <form method="POST" action="{{ url_for('process_approval') }}" class="action-form">
                                    <input type="hidden" name="approval_id" value="{{ approval_id }}">
                                    <input type="hidden" name="decision" value="APPROVE">
                                    <input type="text" name="approver" placeholder="Enter your name" required class="approver-input">
                                    <button type="submit" class="action-btn btn-approve">
                                        <span>✅</span> Approve
                                    </button>
                                </form>
                                
                                <form method="POST" action="{{ url_for('process_approval') }}" class="action-form">
                                    <input type="hidden" name="approval_id" value="{{ approval_id }}">
                                    <input type="hidden" name="decision" value="REJECT">
                                    <input type="text" name="approver" placeholder="Enter your name" required class="approver-input">
                                    <button type="submit" class="action-btn btn-reject">
                                        <span>❌</span> Reject
                                    </button>
                                </form>
                            </div>
                        </div>
                    {% endfor %}
                {% else %}
                    <div class="empty-state">
                        <div class="empty-icon">✅</div>
                        <div class="empty-title">All caught up!</div>
                        <div class="empty-description">No pending approvals at this time.</div>
                    </div>
                {% endif %}
            </div>
        </div>

        <div class="content-card">
            <div class="card-header">
                <div class="card-title">
                    📊 Device Status Overview
                </div>
                <div class="card-subtitle">Current status and progress of all devices</div>
            </div>
            <div class="card-content">
                <div style="overflow-x: auto;">
                    <table class="device-table">
                        <thead>
                            <tr>
                                <th>Device</th>
                                <th>Current Tier</th>
                                <th>Count</th>
                                <th>Next Tier</th>
                                <th>Progress</th>
                                <th>Total Files</th>
                                <th>Status</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for device_name, device_info in sorted_devices %}
                                <tr>
                                    <td>
                                        <div class="device-name">{{ device_name }}</div>
                                    </td>
                                    <td>
                                        <span class="tier-badge tier-{{ device_info.current_tier.replace('h', '') }}">
                                            {{ device_info.current_tier }}
                                        </span>
                                    </td>
                                    <td>
                                        <div class="count-value">{{ device_info.count }}</div>
                                    </td>
                                    <td>
                                        {% if device_info.next_tier %}
                                            <span class="tier-badge tier-{{ device_info.next_tier.replace('h', '') }}">
                                                {{ device_info.next_tier }}
                                            </span>
                                            <div style="font-size: 12px; color: var(--neutral-600); margin-top: 4px;">
                                                {{ device_info.next_requirement }} needed
                                            </div>
                                        {% else %}
                                            <span style="color: var(--success-600); font-weight: 600;">Final Tier</span>
                                        {% endif %}
                                    </td>
                                    <td>
                                        {% if device_info.next_tier %}
                                            <div class="progress-container">
                                                <div class="progress-bar" style="width: {{ device_info.progress_percentage }}%; background-color: {{ device_info.progress_color }};"></div>
                                            </div>
                                            <div class="progress-text">{{ device_info.progress_percentage }}% ({{ device_info.remaining }} remaining)</div>
                                        {% else %}
                                            <div class="progress-container">
                                                <div class="progress-bar" style="width: 100%; background-color: var(--success-500);"></div>
                                            </div>
                                            <div class="progress-text">Complete</div>
                                        {% endif %}
                                    </td>
                                    <td>{{ device_info.total_files }}</td>
                                    <td>
                                        {% if device_info.approval_status == 'PENDING_APPROVAL' %}
                                            <span class="status-badge status-pending">⏳ Pending</span>
                                        {% elif device_info.approval_status == 'APPROVED' %}
                                            <span class="status-badge status-approved">✅ Approved</span>
                                        {% elif device_info.approval_status == 'REJECTED' %}
                                            <span class="status-badge status-rejected">❌ Rejected</span>
                                        {% else %}
                                            <span class="status-badge status-counting">🔄 Counting</span>
                                        {% endif %}
                                    </td>
                                </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>

        <div class="content-card">
            <div class="card-header">
                <div class="card-title">
                    🕒 Recent Activity
                </div>
                <div class="card-subtitle">Latest approval decisions</div>
            </div>
            <div class="card-content">
                {% if approval_history %}
                    {% for approval in approval_history[-5:] %}
                        <div class="history-item">
                            <div class="history-main">
                                <strong>{{ approval.device_name }}</strong>: {{ approval.current_tier }} → {{ approval.proposed_tier }}
                            </div>
                            <div class="history-meta">
                                {{ approval.status }} by {{ approval.approver }} · {{ approval.decision_date[:19] }}
                            </div>
                        </div>
                    {% endfor %}
                {% else %}
                    <div class="empty-state">
                        <div class="empty-icon">📝</div>
                        <div class="empty-title">No activity yet</div>
                        <div class="empty-description">Approval history will appear here.</div>
                    </div>
                {% endif %}
            </div>
        </div>
    </main>

    <script>
        function bulkAction(action) {
            const approver = document.getElementById('bulk-approver').value.trim();
            if (!approver) {
                alert('Please enter your name for bulk operations');
                document.getElementById('bulk-approver').focus();
                return;
            }
            
            const selected = document.querySelectorAll('input[name="selected_approvals"]:checked');
            if (selected.length === 0) {
                alert('Please select at least one approval to proceed');
                return;
            }
            
            const actionText = action === 'APPROVE' ? 'approve' : 'reject';
            if (confirm(`${actionText.charAt(0).toUpperCase() + actionText.slice(1)} ${selected.length} item(s) as ${approver}?`)) {
                // Create a single form with multiple approval IDs
                const form = document.createElement('form');
                form.method = 'POST';
                form.action = '{{ url_for("bulk_process_approval") }}';
                form.style.display = 'none';
                
                // Add decision and approver
                const decision = document.createElement('input');
                decision.type = 'hidden';
                decision.name = 'decision';
                decision.value = action;
                form.appendChild(decision);
                
                const approverInput = document.createElement('input');
                approverInput.type = 'hidden';
                approverInput.name = 'approver';
                approverInput.value = approver;
                form.appendChild(approverInput);
                
                // Add all selected approval IDs
                selected.forEach(checkbox => {
                    const approvalId = document.createElement('input');
                    approvalId.type = 'hidden';
                    approvalId.name = 'approval_ids';
                    approvalId.value = checkbox.value;
                    form.appendChild(approvalId);
                });
                
                document.body.appendChild(form);
                form.submit();
            }
        }
    </script>
</body>
</html>
"""


def create_bi_counter():
    """Create and return BinarySearchFileCounter instance"""
    return BinarySearchFileCounter(CONFIG_FILE)


@app.route("/")
@require_auth
def index():
    """Main approval interface page with modern design"""
    try:
        counter = create_bi_counter()

        # Get data
        pending_approvals = counter.pending_approvals.get("pending", {})
        device_states = counter.state.get("devices", {})
        approval_history = counter.pending_approvals.get("history", [])

        # Calculate stats
        pending_count = len(pending_approvals)
        devices_count = len(device_states)

        # Count approvals made today
        today = datetime.now().date()
        approved_today = 0
        for approval in approval_history:
            if approval.get("decision_date"):
                decision_date = datetime.fromisoformat(approval["decision_date"]).date()
                if decision_date == today and approval.get("status") == "APPROVE":
                    approved_today += 1

        # Enhance device information with progress data
        tier_requirements = counter.config.get(
            "tier_requirements",
            {"24h_to_12h": 250, "12h_to_6h": 500, "6h_to_3h": 1000, "3h_to_2h": 2000},
        )

        enhanced_devices = []
        for device_name, device_state in device_states.items():
            device_info = calculate_device_progress(device_state, tier_requirements)
            enhanced_devices.append((device_name, device_info))

        # Sort devices by proximity to next tier advancement
        sorted_devices = sorted(
            enhanced_devices,
            key=lambda x: x[1].get("progress_percentage", 0),
            reverse=True,
        )

        # Determine mode information
        if counter.is_local_test:
            mode_text = "🧪 Local Test"
            mode_class = "test"
        elif counter.is_production:
            mode_text = "🏭 Production"
            mode_class = "production"
        else:
            mode_text = "🔧 Development"
            mode_class = "dev"

        return render_template_string(
            MODERN_APPROVAL_TEMPLATE,
            pending_approvals=pending_approvals,
            device_states=device_states,
            sorted_devices=sorted_devices,
            approval_history=approval_history,
            pending_count=pending_count,
            devices_count=devices_count,
            approved_today=approved_today,
            last_update=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            config_file=CONFIG_FILE,
            mode_text=mode_text,
            mode_class=mode_class,
            current_user=session.get("user", "Unknown"),
        )

    except Exception as e:
        app.logger.error(f"Error loading approval interface: {e}")
        return f"Error loading approval interface: {e}", 500


def calculate_device_progress(device_state, tier_requirements):
    """Calculate progress information for a device"""
    current_tier = device_state.get("current_tier", "24h")
    current_count = device_state.get("count", 0)

    # Tier progression mapping
    tier_progression = {
        "24h": ("12h", tier_requirements.get("24h_to_12h", 250)),
        "12h": ("6h", tier_requirements.get("12h_to_6h", 500)),
        "6h": ("3h", tier_requirements.get("6h_to_3h", 1000)),
        "3h": ("2h", tier_requirements.get("3h_to_2h", 2000)),
        "2h": (None, None),  # Final tier
    }

    next_tier, next_requirement = tier_progression.get(current_tier, (None, None))

    # Create enhanced device info
    device_info = device_state.copy()
    device_info["next_tier"] = next_tier
    device_info["next_requirement"] = next_requirement

    if next_tier and next_requirement:
        # Calculate progress
        progress_percentage = min(100, (current_count / next_requirement) * 100)
        remaining = max(0, next_requirement - current_count)

        device_info["progress_percentage"] = round(progress_percentage, 1)
        device_info["remaining"] = remaining

        # Color code progress bar
        if progress_percentage >= 90:
            device_info["progress_color"] = "#ef4444"  # Red - very close
        elif progress_percentage >= 75:
            device_info["progress_color"] = "#f59e0b"  # Orange - getting close
        elif progress_percentage >= 50:
            device_info["progress_color"] = "#eab308"  # Yellow - halfway
        else:
            device_info["progress_color"] = "#3b82f6"  # Blue - still building
    else:
        # Final tier
        device_info["progress_percentage"] = 100
        device_info["remaining"] = 0
        device_info["progress_color"] = "#22c55e"  # Green - complete

    return device_info


@app.route("/process_approval", methods=["POST"])
@require_auth
def process_approval():
    """Process approval decision with enhanced logging"""
    try:
        approval_id = request.form.get("approval_id")
        decision = request.form.get("decision")
        approver = request.form.get("approver")

        if not all([approval_id, decision, approver]):
            flash("Missing required information", "error")
            return redirect(url_for("index"))

        if decision not in ["APPROVE", "REJECT"]:
            flash("Invalid decision type", "error")
            return redirect(url_for("index"))

        approval_id_str = str(approval_id)
        decision_str = str(decision)

        counter = create_bi_counter()
        current_user = session.get("user", "Unknown")
        full_approver = f"{approver} ({current_user})"

        success = counter.process_approval_decision(
            approval_id_str, decision_str, full_approver
        )

        if success:
            action = "approved" if decision == "APPROVE" else "rejected"
            flash(f"Successfully {action} tier advancement", "success")
            app.logger.info(
                f"User {current_user} {action} approval {approval_id} as {approver}"
            )
        else:
            flash("Failed to process approval decision", "error")

        return redirect(url_for("index"))

    except Exception as e:
        app.logger.error(f"Error processing approval: {e}")
        flash(f"Error processing approval: {e}", "error")
        return redirect(url_for("index"))


@app.route("/bulk_process_approval", methods=["POST"])
@require_auth
def bulk_process_approval():
    """Process multiple approval decisions in a single transaction"""
    try:
        approval_ids = request.form.getlist("approval_ids")
        decision = request.form.get("decision")
        approver = request.form.get("approver")

        if not all([approval_ids, decision, approver]):
            flash("Missing required information for bulk operation", "error")
            return redirect(url_for("index"))

        if decision not in ["APPROVE", "REJECT"]:
            flash("Invalid decision type", "error")
            return redirect(url_for("index"))

        counter = create_bi_counter()
        current_user = session.get("user", "Unknown")
        full_approver = f"{approver} ({current_user})"

        success_count = 0
        total_count = len(approval_ids)

        # Process each approval
        for approval_id in approval_ids:
            try:
                success = counter.process_approval_decision(
                    str(approval_id), str(decision), full_approver
                )
                if success:
                    success_count += 1
                    app.logger.info(
                        f"Bulk operation: User {current_user} {decision.lower()}d approval {approval_id} as {approver}"
                    )
            except Exception as e:
                app.logger.error(f"Error processing approval {approval_id}: {e}")

        # Provide feedback
        if success_count == total_count:
            action = "approved" if decision == "APPROVE" else "rejected"
            flash(
                f"Successfully {action} {success_count} tier advancement(s)", "success"
            )
        elif success_count > 0:
            action = "approved" if decision == "APPROVE" else "rejected"
            flash(
                f"Partially successful: {action} {success_count} of {total_count} items",
                "warning",
            )
        else:
            flash("Failed to process any bulk approval decisions", "error")

        return redirect(url_for("index"))

    except Exception as e:
        app.logger.error(f"Error in bulk processing: {e}")
        flash(f"Error in bulk processing: {e}", "error")
        return redirect(url_for("index"))


@app.route("/api/status")
@require_auth
def api_status():
    """API endpoint for current status"""
    try:
        counter = create_bi_counter()

        status = {
            "pending_approvals": len(counter.pending_approvals.get("pending", {})),
            "devices": len(counter.state.get("devices", {})),
            "last_scan": counter.state.get("last_scan"),
            "config_file": CONFIG_FILE,
            "production_mode": counter.is_production,
            "local_test_mode": counter.is_local_test,
            "current_user": session.get("user", "Unknown"),
            "timestamp": datetime.now().isoformat(),
            "status": "healthy",
        }

        return jsonify(status)

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == "__main__":
    # Configuration setup
    if len(sys.argv) > 1:
        CONFIG_FILE = sys.argv[1]
        print(f"📁 Using config file: {CONFIG_FILE}")
    else:
        print(f"📁 Using default config file: {CONFIG_FILE}")

    # Setup logging
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    mode_str = ""
    try:
        test_counter = BinarySearchFileCounter(CONFIG_FILE)
        if test_counter.is_local_test:
            mode_str = " (Local Test Mode)"
        elif test_counter.is_production:
            mode_str = " (Production Mode)"
        else:
            mode_str = " (Development Mode)"
    except Exception:
        pass

    print("=" * 60)
    print("🚀 BI Counter - Quality Management Dashboard")
    print("=" * 60)
    print(f"📊 Mode: {mode_str.strip()}")
    print("🔐 Authentication: Enabled")
    print("🔄 Manual refresh: Click refresh button")
    print("📋 Bulk operations: Fixed and working")
    print("🌐 Access URL: http://localhost:8080")
    print("=" * 60)
    print("💡 Press Ctrl+C to stop the server")
    print("🔑 Login credentials:")
    print("   • quality / quality123")
    print("   • admin / admin123")
    print("=" * 60)

    # Run the Flask app
    app.run(host="0.0.0.0", port=8080, debug=False, threaded=True)
