from flask import Flask, request, render_template_string, session, redirect, url_for, jsonify
import subprocess
import platform
import sys
import socket
import os
import time
import json
import base64
import shutil
import hashlib
import random
import string
import zipfile
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.urandom(24)
PASSWORD = '8471'

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

try:
    from PIL import ImageGrab
    import io
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    import ctypes
    from ctypes import wintypes
    WINDOWS_UI = True
except:
    WINDOWS_UI = False

COMMANDS = [
    ('💻 System', 'System Info', '/sysinfo'),
    ('💻 System', 'SystemInfo', '/systeminfo'),
    ('💻 System', 'Uptime', '/uptime'),
    ('💻 System', 'Computer Name', '/hostname'),
    ('💻 System', 'Who am I', '/whoami'),
    ('💻 System', 'Date/Time', '/date'),
    ('💻 System', 'Environment Variables', '/env'),
    ('💻 System', 'PATH variable', '/path'),
    ('💻 System', 'Screenshot', '/screenshot'),
    ('💻 System', 'Clipboard', '/clipboard'),
    ('💻 System', 'Wi-Fi Info', '/wifi'),
    ('💻 System', 'CPU Info', '/cpu-info'),
    ('⚡ Power', 'Shutdown', '/shutdown'),
    ('⚡ Power', 'Reboot', '/reboot'),
    ('⚡ Power', 'Sleep', '/sleep'),
    ('⚡ Power', 'Hibernate', '/hibernate'),
    ('⚡ Power', 'Lock', '/lock'),
    ('⚡ Power', 'Battery Status', '/battery'),
    ('🌐 Network', 'Ping Google', '/ping 8.8.8.8'),
    ('🌐 Network', 'Ping Yandex', '/ping ya.ru'),
    ('🌐 Network', 'Tracert Google', '/tracert 8.8.8.8'),
    ('🌐 Network', 'NSlookup Google', '/nslookup google.com'),
    ('🌐 Network', 'IPConfig', '/ipconfig'),
    ('🌐 Network', 'IPConfig /all', '/ipconfig /all'),
    ('🌐 Network', 'Netstat', '/netstat'),
    ('🌐 Network', 'Netstat -an', '/netstat -an'),
    ('🌐 Network', 'My IP (external)', '/ip'),
    ('🌐 Network', 'Wi-Fi Info', '/wifi'),
    ('📁 Files', 'List files (current)', '/listdir'),
    ('📁 Files', 'List files C:\\', '/listdir C:\\'),
    ('📁 Files', 'Create folder test', '/mkdir test'),
    ('📁 Files', 'Delete folder test', '/rmdir test'),
    ('📁 Files', 'Delete file test.txt', '/del test.txt'),
    ('📁 Files', 'Show file test.txt', '/type test.txt'),
    ('📁 Files', 'Copy file', '/copy src.txt dst.txt'),
    ('📁 Files', 'Move file', '/move src.txt dst.txt'),
    ('📁 Files', 'Rename file', '/rename old.txt new.txt'),
    ('📁 Files', 'Open folder C:\\', '/open C:\\'),
    ('📁 Files', 'Disk usage', '/disk-usage'),
    ('📁 Files', 'Check disk C:', '/chkdsk'),
    ('📁 Files', 'Clear temp', '/clear-temp'),
    ('📁 Files', 'Zip folder', '/zip archive.zip folder'),
    ('⚙️ Processes', 'Processes (text)', '/processes'),
    ('⚙️ Processes', 'Task Manager', '/taskmanager'),
    ('⚙️ Processes', 'Tasklist', '/tasklist'),
    ('⚙️ Processes', 'Restart Explorer', '/restart-explorer'),
    ('⚙️ Processes', 'Start notepad', '/start notepad'),
    ('⚙️ Processes', 'Close notepad', '/stop notepad.exe'),
    ('⚙️ Processes', 'Start calc', '/start calc'),
    ('⚙️ Processes', 'Kill process 1234', '/kill 1234'),
    ('⚙️ Services', 'List services', '/services'),
    ('⚙️ Services', 'Start service Spooler', '/service-start Spooler'),
    ('⚙️ Services', 'Stop service Spooler', '/service-stop Spooler'),
    ('⚙️ Services', 'Service info Spooler', '/service-info Spooler'),
    ('🔊 Sound', 'Volume 0%', '/volume 0'),
    ('🔊 Sound', 'Volume 30%', '/volume 30'),
    ('🔊 Sound', 'Volume 70%', '/volume 70'),
    ('🔊 Sound', 'Volume 100%', '/volume 100'),
    ('🔊 Sound', 'Mute', '/mute'),
    ('🔊 Sound', 'Volume +10', '/volume-up'),
    ('🔊 Sound', 'Volume -10', '/volume-down'),
    ('🔊 Sound', 'Beep', '/beep'),
    ('🔊 Sound', 'Notify: Hello!', '/notify Hello!'),
    ('🔊 Sound', 'Notify: Test', '/notify Test'),
    ('🔊 Sound', 'Notify: Alert!', '/notify Alert!'),
    ('🔊 Sound', 'Notify: Message', '/notify Message'),
    ('🔐 Hashing', 'MD5 file', '/md5 test.txt'),
    ('🔐 Hashing', 'SHA1 file', '/sha1 test.txt'),
    ('🔐 Hashing', 'SHA256 file', '/sha256 test.txt'),
    ('🔐 Hashing', 'Base64 encode "Hello"', '/base64-encode Hello'),
    ('🔐 Hashing', 'Base64 decode "SGVsbG8="', '/base64-decode SGVsbG8='),
    ('🔐 Hashing', 'URL encode "hello world"', '/urlencode hello world'),
    ('🔐 Hashing', 'URL decode "hello%20world"', '/urldecode hello%20world'),
    ('🔐 Hashing', 'Generate password', '/random-pass'),
    ('🔐 Hashing', 'Download file (example)', '/download https://example.com/file.zip'),
    ('🔐 Hashing', 'Check file hash', '/hash-check file.txt'),
    ('🧩 Utilities', 'Run Calculator', '/start calc'),
    ('🧩 Utilities', 'Run Notepad', '/start notepad'),
    ('🧩 Utilities', 'Run Command Prompt', '/start cmd'),
    ('🧩 Utilities', 'Run Task Manager', '/start taskmgr'),
    ('🧩 Utilities', 'Run Registry Editor', '/start regedit'),
    ('🧩 Utilities', 'Run Disk Management', '/start diskmgmt.msc'),
    ('🧩 Utilities', 'Run Services Management', '/start services.msc'),
    ('🧩 Utilities', 'Turn off monitor', '/monitor-off'),
    ('🧩 Utilities', 'Eject drive D:', '/eject D:'),
    ('🧩 Utilities', 'Show message to user', '/msg Hello'),
]

CATEGORIES = {}
for cat, label, cmd in COMMANDS:
    if cat not in CATEGORIES:
        CATEGORIES[cat] = []
    CATEGORIES[cat].append((label, cmd))

LOGIN_PAGE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login - OGUREZ</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            font-family: 'Segoe UI', system-ui, sans-serif;
            background: radial-gradient(ellipse at center, #0d1117 0%, #161b22 100%);
            overflow: hidden;
        }
        body::before {
            content: '';
            position: fixed;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle at 30% 40%, rgba(255, 107, 107, 0.05) 0%, transparent 50%),
                        radial-gradient(circle at 70% 60%, rgba(77, 150, 255, 0.05) 0%, transparent 50%);
            animation: bgMove 20s infinite alternate;
            z-index: 0;
        }
        @keyframes bgMove {
            0% { transform: translate(0, 0) rotate(0deg); }
            100% { transform: translate(-5%, 5%) rotate(5deg); }
        }
        .login-card {
            position: relative;
            z-index: 1;
            background: rgba(22, 27, 34, 0.7);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            padding: 50px 40px;
            border-radius: 60px;
            max-width: 420px;
            width: 100%;
            box-shadow: 0 40px 80px rgba(0,0,0,0.6), 0 0 0 1px rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.06);
            animation: floatIn 1s ease-out;
        }
        @keyframes floatIn {
            0% { opacity: 0; transform: translateY(30px) scale(0.95); }
            100% { opacity: 1; transform: translateY(0) scale(1); }
        }
        .logo {
            font-size: 40px;
            font-weight: 900;
            text-align: center;
            margin-bottom: 20px;
            background: linear-gradient(135deg, #ff6b6b, #ffd93d, #6bcb77, #4d96ff, #9b59b6);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-shadow: 0 0 40px rgba(255,107,107,0.2);
            letter-spacing: 3px;
            animation: neonPulse 3s infinite;
        }
        @keyframes neonPulse {
            0%, 100% { text-shadow: 0 0 20px rgba(255,107,107,0.2); }
            50% { text-shadow: 0 0 40px rgba(255,215,0,0.5), 0 0 80px rgba(255,215,0,0.2); }
        }
        h2 {
            color: #c9d1d9;
            font-weight: 400;
            margin-bottom: 30px;
            text-align: center;
            font-size: 18px;
            letter-spacing: 0.5px;
        }
        input {
            width: 100%;
            padding: 18px 24px;
            border-radius: 40px;
            border: none;
            background: rgba(255,255,255,0.05);
            color: #f0f6fc;
            font-size: 18px;
            outline: 1px solid rgba(255,255,255,0.08);
            transition: all 0.3s;
            margin-bottom: 20px;
        }
        input:focus { outline: 1px solid #4d96ff; background: rgba(255,255,255,0.08); box-shadow: 0 0 30px rgba(77,150,255,0.1); }
        .btn {
            width: 100%;
            padding: 16px;
            border-radius: 40px;
            border: none;
            background: linear-gradient(135deg, #4d96ff, #7a5cff);
            color: white;
            font-weight: 600;
            font-size: 18px;
            cursor: pointer;
            box-shadow: 0 6px 25px rgba(77,150,255,0.3);
            transition: all 0.3s;
        }
        .btn:hover { transform: scale(1.02); box-shadow: 0 10px 35px rgba(77,150,255,0.5); }
        .error { color: #ff7b7b; text-align: center; margin-top: 15px; }
    </style>
</head>
<body>
<div class="login-card">
    <div class="logo">OGUREZ</div>
    <h2>🔐 Enter password</h2>
    <form method="POST">
        <input type="password" name="password" placeholder="Password" autofocus>
        <button class="btn" type="submit">Login</button>
        {% if error %}
        <div class="error">{{ error }}</div>
        {% endif %}
    </form>
</div>
</body>
</html>
'''

MAIN_PAGE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>⚡ OGUREZ - PC Control</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            background: radial-gradient(ellipse at center, #0d1117 0%, #161b22 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            font-family: 'Segoe UI', system-ui, sans-serif;
            padding: 20px;
            position: relative;
        }
        body::before {
            content: '';
            position: fixed;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle at 20% 30%, rgba(255, 107, 107, 0.04) 0%, transparent 50%),
                        radial-gradient(circle at 80% 70%, rgba(77, 150, 255, 0.04) 0%, transparent 50%);
            animation: bgMove 25s infinite alternate;
            z-index: 0;
        }
        @keyframes bgMove {
            0% { transform: translate(0, 0) rotate(0deg); }
            100% { transform: translate(-3%, 5%) rotate(3deg); }
        }
        #splash {
            position: fixed;
            top: 0; left: 0; width: 100%; height: 100%;
            background: radial-gradient(ellipse at center, #0d1117 0%, #161b22 100%);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 9999;
            opacity: 1;
            transition: opacity 0.8s ease;
            pointer-events: none;
        }
        #splash.hidden {
            opacity: 0;
            pointer-events: none;
        }
        .splash-logo {
            font-size: 80px;
            font-weight: 900;
            background: linear-gradient(135deg, #ff6b6b, #ffd93d, #6bcb77, #4d96ff, #9b59b6);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-shadow: 0 0 60px rgba(255,107,107,0.3);
            animation: splashPulse 1.5s infinite alternate;
            letter-spacing: 5px;
        }
        @keyframes splashPulse {
            0% { transform: scale(0.95); opacity: 0.7; }
            100% { transform: scale(1.1); opacity: 1; }
        }
        .card {
            position: relative;
            z-index: 1;
            background: rgba(22, 27, 34, 0.6);
            backdrop-filter: blur(24px);
            -webkit-backdrop-filter: blur(24px);
            border-radius: 60px;
            padding: 40px 45px;
            max-width: 820px;
            width: 100%;
            box-shadow: 0 40px 80px rgba(0,0,0,0.6), 0 0 0 1px rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.06);
            animation: floatIn 0.8s ease-out;
        }
        @keyframes floatIn {
            0% { opacity: 0; transform: translateY(30px) scale(0.96); }
            100% { opacity: 1; transform: translateY(0) scale(1); }
        }
        .header {
            display: flex;
            align-items: center;
            gap: 16px;
            margin-bottom: 24px;
            border-bottom: 1px solid rgba(255,255,255,0.05);
            padding-bottom: 20px;
        }
        .logo {
            font-size: 32px;
            font-weight: 900;
            background: linear-gradient(135deg, #ff6b6b, #ffd93d, #6bcb77, #4d96ff, #9b59b6);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-shadow: 0 0 30px rgba(255,107,107,0.2);
            letter-spacing: 2px;
            animation: neonPulse 3s infinite;
        }
        @keyframes neonPulse {
            0%, 100% { text-shadow: 0 0 20px rgba(255,107,107,0.2); }
            50% { text-shadow: 0 0 40px rgba(255,215,0,0.4), 0 0 80px rgba(255,215,0,0.15); }
        }
        .status {
            margin-left: auto;
            color: #8b949e;
            font-size: 14px;
            background: rgba(255,255,255,0.04);
            padding: 6px 18px;
            border-radius: 40px;
            border: 1px solid rgba(255,255,255,0.06);
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .status-dot {
            width: 10px; height: 10px;
            background: #4ade80;
            border-radius: 50%;
            display: inline-block;
            animation: pulseDot 1.8s infinite;
        }
        @keyframes pulseDot { 0%,100%{opacity:1;transform:scale(1)} 50%{opacity:0.3;transform:scale(0.7)} }
        .nav-links {
            display: flex;
            gap: 20px;
            margin-bottom: 24px;
        }
        .nav-links a {
            color: #8b949e;
            text-decoration: none;
            font-size: 16px;
            padding: 8px 20px;
            border-radius: 40px;
            background: rgba(255,255,255,0.03);
            border: 1px solid rgba(255,255,255,0.04);
            transition: all 0.3s;
        }
        .nav-links a:hover { background: rgba(255,255,255,0.08); color: #f0f6fc; }
        .nav-links a.active { background: rgba(77,150,255,0.15); border-color: #4d96ff; color: #b0d4ff; }
        .input-area {
            display: flex;
            gap: 12px;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }
        .input-area input {
            flex: 1;
            padding: 16px 24px;
            border-radius: 40px;
            border: none;
            background: rgba(255,255,255,0.05);
            color: #f0f6fc;
            font-size: 16px;
            outline: 1px solid rgba(255,255,255,0.06);
            transition: all 0.3s;
            font-family: inherit;
            min-width: 200px;
        }
        .input-area input:focus { outline: 1px solid #4d96ff; background: rgba(255,255,255,0.08); box-shadow: 0 0 30px rgba(77,150,255,0.08); }
        .input-area input::placeholder { color: #5a6f8a; }
        .btn {
            padding: 16px 34px;
            border-radius: 40px;
            border: none;
            background: linear-gradient(135deg, #4d96ff, #7a5cff);
            color: white;
            font-weight: 600;
            font-size: 16px;
            cursor: pointer;
            transition: all 0.3s;
            display: flex;
            align-items: center;
            gap: 8px;
            box-shadow: 0 6px 20px rgba(77,150,255,0.25);
        }
        .btn:hover { transform: translateY(-2px) scale(1.02); box-shadow: 0 12px 35px rgba(77,150,255,0.4); }
        .btn:active { transform: scale(0.96); }
        .logout-btn {
            background: linear-gradient(135deg, #ff6b6b, #c0392b);
            box-shadow: 0 6px 20px rgba(255,107,107,0.25);
        }
        .logout-btn:hover { box-shadow: 0 12px 35px rgba(255,107,107,0.4); }
        .output-container {
            background: rgba(0,0,0,0.3);
            border-radius: 30px;
            padding: 20px 24px;
            min-height: 200px;
            max-height: 460px;
            overflow-y: auto;
            border: 1px solid rgba(255,255,255,0.04);
            margin-top: 8px;
            transition: all 0.3s;
        }
        .output-container pre {
            white-space: pre-wrap;
            word-break: break-all;
            font-family: 'JetBrains Mono', 'Fira Code', monospace;
            font-size: 14px;
            line-height: 1.7;
            color: #c9d1d9;
            margin: 0;
        }
        .empty-hint { color: #4a6080; font-style: italic; user-select: none; text-align: center; padding-top: 30px; }
        .output-container::-webkit-scrollbar { width: 6px; }
        .output-container::-webkit-scrollbar-track { background: transparent; }
        .output-container::-webkit-scrollbar-thumb { background: #2f405a; border-radius: 12px; }
        .footer {
            margin-top: 24px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            color: #4a6080;
            font-size: 13px;
            border-top: 1px solid rgba(255,255,255,0.04);
            padding-top: 18px;
            flex-wrap: wrap;
            gap: 10px;
        }
        .footer .sysinfo { display: flex; gap: 18px; align-items: center; }
        .footer .sysinfo span { background: rgba(255,255,255,0.03); padding: 4px 16px; border-radius: 40px; border: 1px solid rgba(255,255,255,0.04); }
        .loader {
            display: none;
            width: 20px; height: 20px;
            border: 2px solid rgba(255,255,255,0.1);
            border-top: 2px solid #7a5cff;
            border-radius: 50%;
            animation: spin 0.8s linear infinite;
            margin-left: 12px;
        }
        @keyframes spin { to { transform: rotate(360deg); } }
        .btn.loading .btn-text { display: none; }
        .btn.loading .loader { display: inline-block; }
        .image-result img { max-width: 100%; border-radius: 16px; margin-top: 10px; box-shadow: 0 8px 30px rgba(0,0,0,0.5); }
        @media (max-width: 600px) { .card { padding: 24px; } .input-area { flex-direction: column; } .btn { width: 100%; justify-content: center; } }
    </style>
</head>
<body>
    <div id="splash">
        <div class="splash-logo">OGUREZ</div>
    </div>

    <div class="card">
        <div class="header">
            <div class="logo">OGUREZ</div>
            <div class="status">
                <span class="status-dot"></span>
                {{ local_ip }}
            </div>
        </div>

        <div class="nav-links">
            <a href="/" class="active">🏠 Home</a>
            <a href="/panel">🖥️ Command Panel</a>
        </div>

        <div class="input-area">
            <input type="text" id="cmdInput" placeholder="Enter command or /command" autofocus>
            <button class="btn" id="runBtn">
                <span class="btn-text">▶ Execute</span>
                <div class="loader"></div>
            </button>
            <a href="{{ url_for('logout') }}" style="text-decoration:none;">
                <button class="btn logout-btn" style="padding:16px 24px;">🚪 Logout</button>
            </a>
        </div>

        <div class="output-container" id="outputContainer">
            <pre id="outputPre"><span class="empty-hint">▼ result will appear here</span></pre>
        </div>

        <div class="footer">
            <div class="sysinfo">
                <span>🖥️ {{ os }}</span>
                <span>🐍 Python {{ pyver }}</span>
                {% if psutil_avail %} <span>✅ psutil</span> {% endif %}
                {% if pil_avail %} <span>✅ Pillow</span> {% endif %}
            </div>
            <div>⚙️ <span id="timestamp"></span></div>
        </div>
    </div>

    <script>
        window.addEventListener('load', function() {
            setTimeout(function() {
                document.getElementById('splash').classList.add('hidden');
            }, 2000);
        });

        const cmdInput = document.getElementById('cmdInput');
        const runBtn = document.getElementById('runBtn');
        const outputPre = document.getElementById('outputPre');

        function updateTimestamp() {
            document.getElementById('timestamp').textContent = new Date().toLocaleTimeString();
        }
        updateTimestamp();
        setInterval(updateTimestamp, 10000);

        function executeCommand(cmd) {
            if (!cmd) {
                cmd = cmdInput.value.trim();
            }
            if (!cmd) {
                outputPre.innerHTML = '<span style="color:#ff7b7b;">⚠️ Please enter a command</span>';
                return;
            }
            runBtn.classList.add('loading');
            outputPre.innerHTML = '<span style="color:#5f7a9a;">⏳ executing...</span>';

            fetch('/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: 'cmd=' + encodeURIComponent(cmd)
            })
            .then(response => response.text())
            .then(text => {
                if (text.startsWith('data:image/')) {
                    outputPre.innerHTML = `<div class="image-result"><img src="${text}" alt="screenshot"></div>`;
                } else if (text.startsWith('__TASKMANAGER__')) {
                    outputPre.innerHTML = text.replace('__TASKMANAGER__', '');
                    loadTaskManagerData();
                    if (window.tmInterval) clearInterval(window.tmInterval);
                    window.tmInterval = setInterval(loadTaskManagerData, 3000);
                } else {
                    outputPre.textContent = text || '(empty output)';
                }
            })
            .catch(err => {
                outputPre.innerHTML = '<span style="color:#ff7b7b;">❌ Error: ' + err + '</span>';
            })
            .finally(() => {
                runBtn.classList.remove('loading');
            });
        }

        function loadTaskManagerData() {
            fetch('/api/processes')
            .then(res => res.json())
            .then(data => {
                const table = document.getElementById('tm-table');
                if (!table) return;
                const tbody = table.querySelector('tbody');
                tbody.innerHTML = '';
                data.forEach(p => {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td>${p.pid}</td>
                        <td>${p.name || ''}</td>
                        <td>${p.cpu_percent.toFixed(1)}%</td>
                        <td>${p.memory_percent.toFixed(1)}%</td>
                        <td><button class="kill-btn" data-pid="${p.pid}">Kill</button></td>
                    `;
                    tbody.appendChild(row);
                });
                const ts = document.getElementById('tm-timestamp');
                if (ts) ts.textContent = new Date().toLocaleTimeString();
                document.querySelectorAll('.kill-btn').forEach(btn => {
                    btn.onclick = function() {
                        const pid = this.dataset.pid;
                        if (confirm('Kill process ' + pid + '?')) {
                            fetch('/', {
                                method: 'POST',
                                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                                body: 'cmd=/kill ' + pid
                            })
                            .then(() => loadTaskManagerData())
                            .catch(err => console.error(err));
                        }
                    };
                });
            })
            .catch(err => console.error(err));
        }

        runBtn.addEventListener('click', function() { executeCommand(); });
        cmdInput.addEventListener('keydown', (e) => { if (e.key === 'Enter') executeCommand(); });
        cmdInput.focus();

        window.addEventListener('beforeunload', function() {
            if (window.tmInterval) clearInterval(window.tmInterval);
        });
    </script>
</body>
</html>
'''

PANEL_PAGE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🖥️ OGUREZ - Command Panel</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            background: radial-gradient(ellipse at center, #0d1117 0%, #161b22 100%);
            min-height: 100vh;
            font-family: 'Segoe UI', system-ui, sans-serif;
            padding: 20px;
            display: flex;
            justify-content: center;
            position: relative;
        }
        body::before {
            content: '';
            position: fixed;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle at 30% 40%, rgba(255,107,107,0.04) 0%, transparent 50%),
                        radial-gradient(circle at 70% 60%, rgba(77,150,255,0.04) 0%, transparent 50%);
            animation: bgMove 30s infinite alternate;
            z-index: 0;
        }
        @keyframes bgMove {
            0% { transform: translate(0, 0) rotate(0deg); }
            100% { transform: translate(-5%, 8%) rotate(6deg); }
        }
        #splash {
            position: fixed;
            top: 0; left: 0; width: 100%; height: 100%;
            background: radial-gradient(ellipse at center, #0d1117 0%, #161b22 100%);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 9999;
            opacity: 1;
            transition: opacity 0.8s ease;
            pointer-events: none;
        }
        #splash.hidden {
            opacity: 0;
            pointer-events: none;
        }
        .splash-logo {
            font-size: 80px;
            font-weight: 900;
            background: linear-gradient(135deg, #ff6b6b, #ffd93d, #6bcb77, #4d96ff, #9b59b6);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-shadow: 0 0 60px rgba(255,107,107,0.3);
            animation: splashPulse 1.5s infinite alternate;
            letter-spacing: 5px;
        }
        @keyframes splashPulse {
            0% { transform: scale(0.95); opacity: 0.7; }
            100% { transform: scale(1.1); opacity: 1; }
        }
        .card {
            position: relative;
            z-index: 1;
            background: rgba(22, 27, 34, 0.6);
            backdrop-filter: blur(24px);
            -webkit-backdrop-filter: blur(24px);
            border-radius: 60px;
            padding: 40px 45px;
            max-width: 1400px;
            width: 100%;
            box-shadow: 0 40px 80px rgba(0,0,0,0.6), 0 0 0 1px rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.06);
            max-height: 98vh;
            overflow-y: auto;
            animation: floatIn 0.8s ease-out;
        }
        @keyframes floatIn {
            0% { opacity: 0; transform: translateY(30px) scale(0.96); }
            100% { opacity: 1; transform: translateY(0) scale(1); }
        }
        .card::-webkit-scrollbar { width: 6px; }
        .card::-webkit-scrollbar-track { background: transparent; }
        .card::-webkit-scrollbar-thumb { background: #2f405a; border-radius: 12px; }
        .header {
            display: flex;
            align-items: center;
            gap: 16px;
            margin-bottom: 24px;
            border-bottom: 1px solid rgba(255,255,255,0.05);
            padding-bottom: 20px;
        }
        .logo {
            font-size: 32px;
            font-weight: 900;
            background: linear-gradient(135deg, #ff6b6b, #ffd93d, #6bcb77, #4d96ff, #9b59b6);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-shadow: 0 0 30px rgba(255,107,107,0.2);
            letter-spacing: 2px;
            animation: neonPulse 3s infinite;
        }
        @keyframes neonPulse {
            0%, 100% { text-shadow: 0 0 20px rgba(255,107,107,0.2); }
            50% { text-shadow: 0 0 40px rgba(255,215,0,0.4), 0 0 80px rgba(255,215,0,0.15); }
        }
        .status {
            margin-left: auto;
            color: #8b949e;
            font-size: 14px;
            background: rgba(255,255,255,0.04);
            padding: 6px 18px;
            border-radius: 40px;
            border: 1px solid rgba(255,255,255,0.06);
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .status-dot {
            width: 10px; height: 10px;
            background: #4ade80;
            border-radius: 50%;
            display: inline-block;
            animation: pulseDot 1.8s infinite;
        }
        @keyframes pulseDot { 0%,100%{opacity:1;transform:scale(1)} 50%{opacity:0.3;transform:scale(0.7)} }
        .nav-links {
            display: flex;
            gap: 20px;
            margin-bottom: 24px;
        }
        .nav-links a {
            color: #8b949e;
            text-decoration: none;
            font-size: 16px;
            padding: 8px 20px;
            border-radius: 40px;
            background: rgba(255,255,255,0.03);
            border: 1px solid rgba(255,255,255,0.04);
            transition: all 0.3s;
        }
        .nav-links a:hover { background: rgba(255,255,255,0.08); color: #f0f6fc; }
        .nav-links a.active { background: rgba(77,150,255,0.15); border-color: #4d96ff; color: #b0d4ff; }
        .category {
            margin-bottom: 24px;
        }
        .category h3 {
            color: #8b949e;
            font-weight: 400;
            font-size: 16px;
            margin-bottom: 10px;
            border-bottom: 1px solid rgba(255,255,255,0.04);
            padding-bottom: 6px;
            letter-spacing: 0.3px;
        }
        .button-grid {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
        }
        .panel-btn {
            padding: 6px 16px;
            border-radius: 40px;
            border: none;
            background: rgba(255,255,255,0.05);
            color: #c9d1d9;
            font-size: 12px;
            cursor: pointer;
            transition: all 0.25s;
            border: 1px solid rgba(255,255,255,0.06);
            white-space: nowrap;
            position: relative;
            overflow: hidden;
        }
        .panel-btn::after {
            content: '';
            position: absolute;
            top: 50%;
            left: 50%;
            width: 0;
            height: 0;
            background: rgba(255,255,255,0.08);
            border-radius: 50%;
            transform: translate(-50%, -50%);
            transition: width 0.5s, height 0.5s;
        }
        .panel-btn:active::after {
            width: 300px;
            height: 300px;
        }
        .panel-btn:hover { background: rgba(255,255,255,0.12); transform: scale(1.02); color: #f0f6fc; }
        .panel-btn.danger { background: rgba(255,77,77,0.12); color: #ff7b7b; border-color: rgba(255,77,77,0.1); }
        .panel-btn.danger:hover { background: rgba(255,77,77,0.2); }
        .panel-btn.success { background: rgba(77,200,77,0.08); color: #7add7a; }
        .panel-btn.success:hover { background: rgba(77,200,77,0.15); }
        .panel-btn.warning { background: rgba(255,200,77,0.08); color: #f5d77a; }
        .panel-btn.warning:hover { background: rgba(255,200,77,0.15); }
        .result-container {
            margin-top: 24px;
            background: rgba(0,0,0,0.3);
            border-radius: 30px;
            padding: 20px;
            min-height: 120px;
            border: 1px solid rgba(255,255,255,0.04);
            position: relative;
            overflow: hidden;
            transition: all 0.3s;
        }
        .result-container .placeholder {
            color: #4a6080;
            font-style: italic;
            text-align: center;
            padding: 30px 0;
        }
        .result-content {
            animation: fadeInUp 0.5s ease forwards;
            opacity: 0;
            transform: translateY(20px);
        }
        @keyframes fadeInUp {
            to { opacity: 1; transform: translateY(0); }
        }
        .result-content img {
            max-width: 100%;
            border-radius: 16px;
            box-shadow: 0 8px 30px rgba(0,0,0,0.5);
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 16px;
            margin: 10px 0;
        }
        .stat-card {
            background: rgba(255,255,255,0.04);
            border-radius: 20px;
            padding: 16px 20px;
            border: 1px solid rgba(255,255,255,0.06);
            transition: 0.2s;
        }
        .stat-card:hover { background: rgba(255,255,255,0.08); }
        .stat-card .label { font-size: 13px; color: #8b949e; }
        .stat-card .value { font-size: 24px; font-weight: 500; color: #f0f6fc; margin-top: 4px; }
        .stat-card .progress {
            margin-top: 10px;
            height: 6px;
            background: rgba(255,255,255,0.08);
            border-radius: 10px;
            overflow: hidden;
        }
        .stat-card .progress .bar {
            height: 100%;
            border-radius: 10px;
            background: linear-gradient(90deg, #4d96ff, #7a5cff);
            transition: width 0.6s ease;
            width: 0%;
        }
        .stat-card .progress .bar.green { background: #4ade80; }
        .stat-card .progress .bar.yellow { background: #facc15; }
        .stat-card .progress .bar.red { background: #f87171; }
        .taskmanager-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
            color: #c9d1d9;
        }
        .taskmanager-table th {
            background: rgba(255,255,255,0.04);
            color: #8b949e;
            padding: 8px 12px;
            text-align: left;
            font-weight: 400;
            border-bottom: 1px solid rgba(255,255,255,0.06);
        }
        .taskmanager-table td {
            padding: 6px 12px;
            border-bottom: 1px solid rgba(255,255,255,0.03);
        }
        .taskmanager-table tr:hover td { background: rgba(255,255,255,0.04); }
        .kill-btn {
            background: rgba(255,77,77,0.15);
            border: none;
            color: #ff7b7b;
            padding: 2px 14px;
            border-radius: 16px;
            cursor: pointer;
            font-size: 12px;
            transition: 0.2s;
        }
        .kill-btn:hover { background: rgba(255,77,77,0.3); }
        .clear-result {
            position: absolute;
            top: 12px;
            right: 16px;
            background: none;
            border: none;
            color: #5f7a9a;
            cursor: pointer;
            font-size: 20px;
            transition: 0.2s;
        }
        .clear-result:hover { color: #ff7b7b; transform: rotate(90deg); }
        .loading-spinner {
            display: inline-block;
            width: 30px;
            height: 30px;
            border: 3px solid rgba(255,255,255,0.08);
            border-top: 3px solid #7a5cff;
            border-radius: 50%;
            animation: spin 0.8s linear infinite;
        }
        @keyframes spin { to { transform: rotate(360deg); } }
        .footer {
            margin-top: 24px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            color: #4a6080;
            font-size: 13px;
            border-top: 1px solid rgba(255,255,255,0.04);
            padding-top: 18px;
            flex-wrap: wrap;
            gap: 10px;
        }
        .total-badge {
            background: rgba(77,150,255,0.12);
            padding: 4px 20px;
            border-radius: 40px;
            color: #b0d4ff;
            font-size: 14px;
            border: 1px solid rgba(77,150,255,0.15);
        }
        @media (max-width: 600px) {
            .card { padding: 24px; }
            .button-grid { gap: 4px; }
            .panel-btn { font-size: 11px; padding: 4px 12px; }
            .stats-grid { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <div id="splash">
        <div class="splash-logo">OGUREZ</div>
    </div>

    <div class="card">
        <div class="header">
            <div class="logo">OGUREZ</div>
            <div class="status">
                <span class="status-dot"></span>
                {{ local_ip }}
            </div>
        </div>

        <div class="nav-links">
            <a href="/">🏠 Home</a>
            <a href="/panel" class="active">🖥️ Command Panel</a>
        </div>

        <div style="margin-bottom:16px; display:flex; justify-content:space-between; align-items:center;">
            <button class="panel-btn" onclick="clearResult()" style="background:rgba(255,77,77,0.12);color:#ff7b7b;">🗑 Clear result</button>
            <span class="total-badge">Total commands: {{ total }}</span>
        </div>

        {% for category, cmds in categories.items() %}
        <div class="category">
            <h3>{{ category }}</h3>
            <div class="button-grid">
                {% for label, cmd in cmds %}
                <button class="panel-btn" data-cmd="{{ cmd }}">{{ label }}</button>
                {% endfor %}
            </div>
        </div>
        {% endfor %}

        <div class="result-container" id="resultContainer">
            <div class="placeholder" id="placeholder">▼ Click a button to execute command</div>
            <div id="resultContent" style="display:none;"></div>
            <button class="clear-result" id="clearResultBtn" style="display:none;" onclick="clearResult()">✕</button>
        </div>

        <div class="footer">
            <span>⚙️ <span id="timestamp"></span></span>
            <span>OGUREZ v3.2 EN</span>
        </div>
    </div>

    <script>
        window.addEventListener('load', function() {
            setTimeout(function() {
                document.getElementById('splash').classList.add('hidden');
            }, 2000);
        });

        let currentInterval = null;

        function parseSysInfo(text) {
            const lines = text.split('\\n').filter(l => l.trim());
            let html = '<div class="stats-grid">';
            let cpu = '?', ramUsed = '?', ramTotal = '?', ramPct = '?', diskUsed = '?', diskTotal = '?', diskPct = '?';
            lines.forEach(line => {
                if (line.includes('CPU:')) {
                    const match = line.match(/CPU:\\s*([\\d.]+)%/);
                    if (match) cpu = match[1];
                } else if (line.includes('ОЗУ:')) {
                    const match = line.match(/ОЗУ:\\s*([\\d.]+)\\s*\\/\\s*([\\d.]+)\\s*ГБ\\s*\\(([\\d.]+)%\\)/);
                    if (match) { ramUsed = match[1]; ramTotal = match[2]; ramPct = match[3]; }
                } else if (line.includes('Диск:')) {
                    const match = line.match(/Диск:\\s*([\\d.]+)\\s*\\/\\s*([\\d.]+)\\s*ГБ\\s*\\(([\\d.]+)%\\)/);
                    if (match) { diskUsed = match[1]; diskTotal = match[2]; diskPct = match[3]; }
                }
            });
            if (cpu !== '?') {
                const barClass = parseFloat(cpu) < 50 ? 'green' : parseFloat(cpu) < 80 ? 'yellow' : 'red';
                html += `<div class="stat-card"><div class="label">CPU</div><div class="value">${cpu}%</div><div class="progress"><div class="bar ${barClass}" style="width:${cpu}%;"></div></div></div>`;
            }
            if (ramTotal !== '?') {
                const barClass = parseFloat(ramPct) < 50 ? 'green' : parseFloat(ramPct) < 80 ? 'yellow' : 'red';
                html += `<div class="stat-card"><div class="label">RAM</div><div class="value">${ramUsed} / ${ramTotal} GB</div><div class="progress"><div class="bar ${barClass}" style="width:${ramPct}%;"></div></div></div>`;
            }
            if (diskTotal !== '?') {
                const barClass = parseFloat(diskPct) < 50 ? 'green' : parseFloat(diskPct) < 80 ? 'yellow' : 'red';
                html += `<div class="stat-card"><div class="label">Disk</div><div class="value">${diskUsed} / ${diskTotal} GB</div><div class="progress"><div class="bar ${barClass}" style="width:${diskPct}%;"></div></div></div>`;
            }
            lines.forEach(line => {
                if (!line.includes('CPU:') && !line.includes('ОЗУ:') && !line.includes('Диск:')) {
                    html += `<div style="grid-column:1/-1;color:#8b949e;font-size:14px;padding:4px 0;">${line}</div>`;
                }
            });
            html += '</div>';
            return html;
        }

        function parseDiskUsage(text) {
            const lines = text.split('\\n');
            let total = '', used = '', free = '', pct = '';
            lines.forEach(line => {
                if (line.includes('Всего:')) total = line.replace('Всего:', '').trim();
                if (line.includes('Использовано:')) used = line.replace('Использовано:', '').trim();
                if (line.includes('Свободно:')) free = line.replace('Свободно:', '').trim();
                if (line.includes('Занято:')) pct = line.replace('Занято:', '').trim();
            });
            let html = '<div class="stats-grid">';
            if (total) html += `<div class="stat-card"><div class="label">Total</div><div class="value">${total}</div></div>`;
            if (used) html += `<div class="stat-card"><div class="label">Used</div><div class="value">${used}</div></div>`;
            if (free) html += `<div class="stat-card"><div class="label">Free</div><div class="value">${free}</div></div>`;
            if (pct) {
                const numPct = parseFloat(pct);
                const barClass = numPct < 50 ? 'green' : numPct < 80 ? 'yellow' : 'red';
                html += `<div class="stat-card"><div class="label">Used %</div><div class="value">${pct}</div><div class="progress"><div class="bar ${barClass}" style="width:${numPct}%;"></div></div></div>`;
            }
            html += '</div>';
            return html;
        }

        function parseBattery(text) {
            const lines = text.split('\\n');
            let pct = '?', time = '?', plugged = '?';
            lines.forEach(line => {
                if (line.includes('Заряд:')) pct = line.replace('Заряд:', '').trim();
                if (line.includes('Время до разряда:')) time = line.replace('Время до разряда:', '').trim();
                if (line.includes('Подключен:')) plugged = line.replace('Подключен:', '').trim();
            });
            let html = '<div class="stats-grid">';
            if (pct !== '?') {
                const numPct = parseFloat(pct);
                const barClass = numPct > 50 ? 'green' : numPct > 20 ? 'yellow' : 'red';
                html += `<div class="stat-card"><div class="label">Battery</div><div class="value">${pct}</div><div class="progress"><div class="bar ${barClass}" style="width:${numPct}%;"></div></div></div>`;
            }
            if (time !== '?') html += `<div class="stat-card"><div class="label">Time left</div><div class="value">${time}</div></div>`;
            if (plugged !== '?') html += `<div class="stat-card"><div class="label">Plugged</div><div class="value">${plugged}</div></div>`;
            html += '</div>';
            return html;
        }

        function parseUptime(text) {
            const match = text.match(/(\\d+)\\s*дн,\\s*(\\d+)\\s*ч,\\s*(\\d+)\\s*мин/);
            if (match) {
                const days = match[1], hours = match[2], minutes = match[3];
                return `<div class="stats-grid">
                    <div class="stat-card"><div class="label">Days</div><div class="value">${days}</div></div>
                    <div class="stat-card"><div class="label">Hours</div><div class="value">${hours}</div></div>
                    <div class="stat-card"><div class="label">Minutes</div><div class="value">${minutes}</div></div>
                </div>`;
            } else {
                return `<pre style="white-space:pre-wrap;color:#c9d1d9;">${text}</pre>`;
            }
        }

        function loadTaskManagerDataPanel() {
            fetch('/api/processes')
            .then(res => res.json())
            .then(data => {
                const table = document.getElementById('tm-table-panel');
                if (!table) return;
                const tbody = table.querySelector('tbody');
                tbody.innerHTML = '';
                data.slice(0, 30).forEach(p => {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td>${p.pid}</td>
                        <td>${p.name || ''}</td>
                        <td>${p.cpu_percent.toFixed(1)}%</td>
                        <td>${p.memory_percent.toFixed(1)}%</td>
                        <td><button class="kill-btn" data-pid="${p.pid}">Kill</button></td>
                    `;
                    tbody.appendChild(row);
                });
                const ts = document.getElementById('tm-timestamp-panel');
                if (ts) ts.textContent = new Date().toLocaleTimeString();
                document.querySelectorAll('#tm-table-panel .kill-btn').forEach(btn => {
                    btn.onclick = function() {
                        const pid = this.dataset.pid;
                        if (confirm('Kill process ' + pid + '?')) {
                            fetch('/', {
                                method: 'POST',
                                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                                body: 'cmd=/kill ' + pid
                            })
                            .then(() => loadTaskManagerDataPanel())
                            .catch(err => console.error(err));
                        }
                    };
                });
            })
            .catch(err => console.error(err));
        }

        function clearResult() {
            if (currentInterval) {
                clearInterval(currentInterval);
                currentInterval = null;
            }
            document.getElementById('resultContent').style.display = 'none';
            document.getElementById('placeholder').style.display = 'block';
            document.getElementById('clearResultBtn').style.display = 'none';
            document.getElementById('resultContent').innerHTML = '';
        }

        function executeCommand(cmd) {
            console.log('Executing:', cmd);
            const placeholder = document.getElementById('placeholder');
            const resultContent = document.getElementById('resultContent');
            const clearBtn = document.getElementById('clearResultBtn');

            placeholder.style.display = 'none';
            resultContent.style.display = 'block';
            resultContent.innerHTML = `<div style="text-align:center;padding:20px;"><div class="loading-spinner"></div><div style="color:#5f7a9a;margin-top:10px;">Executing...</div></div>`;
            clearBtn.style.display = 'block';

            if (currentInterval) {
                clearInterval(currentInterval);
                currentInterval = null;
            }

            fetch('/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: 'cmd=' + encodeURIComponent(cmd)
            })
            .then(response => response.text())
            .then(text => {
                if (text.startsWith('data:image/')) {
                    resultContent.innerHTML = `<img src="${text}" alt="screenshot" style="max-width:100%;border-radius:16px;">`;
                } else if (text.startsWith('__TASKMANAGER__')) {
                    const taskHtml = `
                    <div style="color:#c9d1d9;">
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                            <span style="font-weight:500;">📋 Task Manager</span>
                            <span style="font-size:12px; color:#5f7a9a;">Updates every 3s, <span id="tm-timestamp-panel"></span></span>
                        </div>
                        <table class="taskmanager-table" id="tm-table-panel">
                            <thead>
                                <tr><th>PID</th><th>Name</th><th>CPU</th><th>Memory</th><th>Action</th></tr>
                            </thead>
                            <tbody></tbody>
                        </table>
                        <div style="margin-top:10px;color:#5f7a9a;font-size:13px;">⏳ loading...</div>
                    </div>
                    <style>
                        .taskmanager-table td { padding:4px 8px; border-bottom:1px solid rgba(255,255,255,0.03); color:#c9d1d9; }
                        .taskmanager-table tr:hover td { background:rgba(255,255,255,0.04); }
                        .kill-btn { background:rgba(255,77,77,0.15); border:none; color:#ff7b7b; padding:2px 10px; border-radius:16px; cursor:pointer; font-size:11px; }
                        .kill-btn:hover { background:rgba(255,77,77,0.3); }
                    </style>
                    `;
                    resultContent.innerHTML = taskHtml;
                    loadTaskManagerDataPanel();
                    if (currentInterval) clearInterval(currentInterval);
                    currentInterval = setInterval(loadTaskManagerDataPanel, 3000);
                } else if (cmd === '/sysinfo' || cmd === '/systeminfo') {
                    resultContent.innerHTML = parseSysInfo(text);
                } else if (cmd === '/disk-usage') {
                    resultContent.innerHTML = parseDiskUsage(text);
                } else if (cmd === '/battery') {
                    resultContent.innerHTML = parseBattery(text);
                } else if (cmd === '/uptime') {
                    resultContent.innerHTML = parseUptime(text);
                } else {
                    resultContent.innerHTML = `<pre style="white-space:pre-wrap;color:#c9d1d9;">${text || '(empty output)'}</pre>`;
                }
                resultContent.classList.remove('result-content');
                void resultContent.offsetWidth;
                resultContent.classList.add('result-content');
            })
            .catch(err => {
                resultContent.innerHTML = `<span style="color:#ff7b7b;">❌ Error: ${err}</span>`;
            });
        }

        function updateTimestamp() {
            document.getElementById('timestamp').textContent = new Date().toLocaleTimeString();
        }
        updateTimestamp();
        setInterval(updateTimestamp, 10000);

        document.addEventListener('DOMContentLoaded', function() {
            document.querySelectorAll('.panel-btn[data-cmd]').forEach(function(btn) {
                btn.addEventListener('click', function(e) {
                    const cmd = this.getAttribute('data-cmd');
                    if (cmd) {
                        executeCommand(cmd);
                    }
                });
            });
        });
    </script>
</body>
</html>
'''

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return '127.0.0.1'

def get_system_info():
    info = {}
    info['os'] = platform.system()
    info['version'] = platform.version()
    info['machine'] = platform.machine()
    info['processor'] = platform.processor()
    if PSUTIL_AVAILABLE:
        info['cpu_percent'] = psutil.cpu_percent(interval=0.5)
        mem = psutil.virtual_memory()
        info['memory_total'] = mem.total // (1024**3)
        info['memory_used'] = mem.used // (1024**3)
        info['memory_percent'] = mem.percent
        disk = psutil.disk_usage('/')
        info['disk_total'] = disk.total // (1024**3)
        info['disk_used'] = disk.used // (1024**3)
        info['disk_percent'] = disk.percent
    return info

def make_screenshot():
    if not PIL_AVAILABLE:
        return "Error: Pillow library not installed. Install: pip install pillow"
    try:
        img = ImageGrab.grab()
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        b64 = base64.b64encode(buffer.getvalue()).decode()
        return f"data:image/png;base64,{b64}"
    except Exception as e:
        return f"Screenshot error: {e}"

def get_clipboard_text():
    try:
        if platform.system() == 'Windows':
            import win32clipboard
            win32clipboard.OpenClipboard()
            data = win32clipboard.GetClipboardData()
            win32clipboard.CloseClipboard()
            return data
        elif platform.system() == 'Darwin':
            result = subprocess.run(['pbpaste'], capture_output=True, text=True)
            return result.stdout
        else:
            result = subprocess.run(['xclip', '-o', '-selection', 'clipboard'], capture_output=True, text=True)
            return result.stdout
    except Exception as e:
        return f"Clipboard error: {e}"

def get_uptime():
    try:
        if platform.system() == 'Windows':
            result = subprocess.run(['systeminfo'], capture_output=True, text=True)
            for line in result.stdout.splitlines():
                if 'время работы системы' in line.lower() or 'system uptime' in line.lower():
                    return line.strip()
            return "Uptime not found"
        else:
            with open('/proc/uptime', 'r') as f:
                uptime_seconds = float(f.readline().split()[0])
                days = int(uptime_seconds // 86400)
                hours = int((uptime_seconds % 86400) // 3600)
                minutes = int((uptime_seconds % 3600) // 60)
                return f"{days} days, {hours} hours, {minutes} minutes"
    except Exception as e:
        return f"Error: {e}"

def get_process_list():
    if not PSUTIL_AVAILABLE:
        return "Install psutil: pip install psutil"
    try:
        procs = []
        for p in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                procs.append(p.info)
            except:
                pass
        procs.sort(key=lambda x: x.get('cpu_percent', 0), reverse=True)
        lines = ["PID   NAME                           CPU%   MEM%"]
        for p in procs[:30]:
            pid = p['pid']
            name = (p['name'] or '')[:20]
            cpu = p.get('cpu_percent', 0)
            mem = p.get('memory_percent', 0)
            lines.append(f"{pid:6} {name:30} {cpu:6.1f} {mem:6.1f}")
        return '\n'.join(lines)
    except Exception as e:
        return f"Error: {e}"

def kill_process(pid):
    if not PSUTIL_AVAILABLE:
        return "Install psutil"
    try:
        p = psutil.Process(int(pid))
        p.terminate()
        return f"Process {pid} terminated"
    except Exception as e:
        return f"Error: {e}"

def download_file(url):
    try:
        import requests
        filename = url.split('/')[-1] or 'downloaded_file'
        r = requests.get(url, stream=True)
        if r.status_code == 200:
            with open(filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
            return f"File {filename} downloaded"
        else:
            return f"Download error, code {r.status_code}"
    except ImportError:
        return "Install requests: pip install requests"
    except Exception as e:
        return f"Error: {e}"

def show_notification(text):
    try:
        if platform.system() == 'Windows':
            ctypes.windll.user32.MessageBoxW(0, text, "Notification", 0)
            return "Notification shown"
        elif platform.system() == 'Darwin':
            subprocess.Popen(['osascript', '-e', f'display notification "{text}"'])
            return "Notification shown"
        else:
            subprocess.Popen(['notify-send', text])
            return "Notification shown"
    except Exception as e:
        return f"Error: {e}"

def set_volume(level):
    try:
        level = int(level)
        if level < 0: level = 0
        if level > 100: level = 100
        if platform.system() == 'Windows':
            from ctypes import cast, POINTER
            from comtypes import CLSCTX_ALL
            from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = cast(interface, POINTER(IAudioEndpointVolume))
            volume.SetMasterVolumeLevelScalar(level/100.0, None)
            return f"Volume set to {level}%"
        else:
            subprocess.Popen(['amixer', 'set', 'Master', f'{level}%'])
            return f"Volume set to {level}%"
    except ImportError:
        return "For volume control on Windows install pycaw: pip install pycaw"
    except Exception as e:
        return f"Error: {e}"

def lock_screen():
    try:
        if platform.system() == 'Windows':
            ctypes.windll.user32.LockWorkStation()
            return "Screen locked"
        elif platform.system() == 'Darwin':
            subprocess.Popen(['pmset', 'displaysleepnow'])
            return "Screen locked"
        else:
            subprocess.Popen(['gnome-screensaver-command', '-l'])
            return "Screen locked"
    except Exception as e:
        return f"Error: {e}"

def sleep_pc():
    try:
        if platform.system() == 'Windows':
            ctypes.windll.powrprof.SetSuspendState(0, 1, 0)
            return "PC sleeping"
        else:
            subprocess.Popen(['systemctl', 'suspend'])
            return "PC sleeping"
    except Exception as e:
        return f"Error: {e}"

def hibernate_pc():
    try:
        if platform.system() == 'Windows':
            ctypes.windll.powrprof.SetSuspendState(1, 1, 0)
            return "PC hibernating"
        else:
            subprocess.Popen(['systemctl', 'hibernate'])
            return "PC hibernating"
    except Exception as e:
        return f"Error: {e}"

def logoff_user():
    try:
        if platform.system() == 'Windows':
            subprocess.Popen(['shutdown', '/l'])
            return "Logging off"
        else:
            subprocess.Popen(['gnome-session-quit', '--logout', '--no-prompt'])
            return "Logging off"
    except Exception as e:
        return f"Error: {e}"

def get_wifi_info():
    try:
        if platform.system() == 'Windows':
            result = subprocess.run(['netsh', 'wlan', 'show', 'interfaces'], capture_output=True, text=True)
            return result.stdout
        elif platform.system() == 'Darwin':
            result = subprocess.run(['/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport', '-I'], capture_output=True, text=True)
            return result.stdout
        else:
            result = subprocess.run(['iwconfig'], capture_output=True, text=True)
            return result.stdout
    except Exception as e:
        return f"Error: {e}"

def restart_explorer():
    try:
        if platform.system() == 'Windows':
            subprocess.Popen(['taskkill', '/f', '/im', 'explorer.exe'])
            time.sleep(1)
            subprocess.Popen(['explorer.exe'])
            return "Explorer restarted"
        else:
            return "Windows only"
    except Exception as e:
        return f"Error: {e}"

def mute_system():
    return set_volume(0)

def list_directory(path='.'):
    try:
        files = os.listdir(path)
        return '\n'.join(files[:50])
    except Exception as e:
        return f"Error: {e}"

def disk_usage():
    if not PSUTIL_AVAILABLE:
        return "Install psutil"
    try:
        usage = psutil.disk_usage('/')
        return f"Total: {usage.total // (1024**3)} GB\nUsed: {usage.used // (1024**3)} GB\nFree: {usage.free // (1024**3)} GB\nUsed %: {usage.percent}%"
    except Exception as e:
        return f"Error: {e}"

def open_folder(path):
    try:
        if platform.system() == 'Windows':
            os.startfile(path)
        elif platform.system() == 'Darwin':
            subprocess.Popen(['open', path])
        else:
            subprocess.Popen(['xdg-open', path])
        return f"Opened: {path}"
    except Exception as e:
        return f"Error: {e}"

def get_my_ip():
    try:
        import requests
        ip = requests.get('https://api.ipify.org').text
        return f"External IP: {ip}"
    except:
        return "Could not determine external IP"

def ping(host):
    try:
        param = '-n' if platform.system() == 'Windows' else '-c'
        result = subprocess.run(['ping', param, '4', host], capture_output=True, text=True, timeout=10)
        return result.stdout
    except Exception as e:
        return f"Error: {e}"

def clear_temp():
    try:
        if platform.system() == 'Windows':
            temp = os.environ.get('TEMP')
            if temp:
                shutil.rmtree(temp, ignore_errors=True)
                return f"Temp cleaned ({temp})"
            else:
                return "TEMP folder not found"
        else:
            shutil.rmtree('/tmp', ignore_errors=True)
            return "/tmp cleaned"
    except Exception as e:
        return f"Error: {e}"

def battery_info():
    if not PSUTIL_AVAILABLE:
        return "Install psutil"
    try:
        battery = psutil.sensors_battery()
        if battery:
            return f"Charge: {battery.percent}%\nTime left: {battery.secsleft // 60} min\nPlugged: {battery.power_plugged}"
        else:
            return "No battery detected"
    except Exception as e:
        return f"Error: {e}"

def cpu_info():
    try:
        if platform.system() == 'Windows':
            result = subprocess.run(['wmic', 'cpu', 'get', 'name'], capture_output=True, text=True)
            return result.stdout
        else:
            result = subprocess.run(['lscpu'], capture_output=True, text=True)
            return result.stdout
    except Exception as e:
        return f"Error: {e}"

def gpu_info():
    try:
        if platform.system() == 'Windows':
            result = subprocess.run(['wmic', 'path', 'win32_videocontroller', 'get', 'name'], capture_output=True, text=True)
            return result.stdout
        else:
            return "GPU info only on Windows via wmic"
    except Exception as e:
        return f"Error: {e}"

def random_password():
    chars = string.ascii_letters + string.digits + '!@#$%^&*'
    pwd = ''.join(random.choice(chars) for _ in range(16))
    return f"Generated password: {pwd}"

def whoami():
    try:
        if platform.system() == 'Windows':
            return os.environ.get('USERNAME', 'unknown')
        else:
            return os.environ.get('USER', 'unknown')
    except:
        return "unknown"

def get_date():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def get_hostname():
    return socket.gethostname()

def get_env_vars():
    return '\n'.join([f"{k}={v}" for k, v in os.environ.items()])

def set_env_var(var):
    try:
        key, val = var.split('=', 1)
        os.environ[key] = val
        return f"Variable {key} set to {val}"
    except:
        return "Error: use /setenv KEY=VALUE"

def get_path():
    return os.environ.get('PATH', '')

def where(file):
    try:
        import shutil
        path = shutil.which(file)
        return path if path else "Not found"
    except:
        return "Error"

def mkdir(path):
    try:
        os.makedirs(path, exist_ok=True)
        return f"Folder {path} created"
    except Exception as e:
        return f"Error: {e}"

def rmdir(path):
    try:
        shutil.rmtree(path)
        return f"Folder {path} removed"
    except Exception as e:
        return f"Error: {e}"

def delete_file(path):
    try:
        os.remove(path)
        return f"File {path} deleted"
    except Exception as e:
        return f"Error: {e}"

def type_file(path):
    try:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    except Exception as e:
        return f"Error: {e}"

def copy_file(src, dst):
    try:
        shutil.copy2(src, dst)
        return f"Copied {src} -> {dst}"
    except Exception as e:
        return f"Error: {e}"

def move_file(src, dst):
    try:
        shutil.move(src, dst)
        return f"Moved {src} -> {dst}"
    except Exception as e:
        return f"Error: {e}"

def rename_file(old, new):
    try:
        os.rename(old, new)
        return f"Renamed {old} -> {new}"
    except Exception as e:
        return f"Error: {e}"

def zip_folder(zipname, folder):
    try:
        with zipfile.ZipFile(zipname, 'w', zipfile.ZIP_DEFLATED) as zf:
            for root, dirs, files in os.walk(folder):
                for f in files:
                    zf.write(os.path.join(root, f), os.path.relpath(os.path.join(root, f), folder))
        return f"Archive {zipname} created from {folder}"
    except Exception as e:
        return f"Error: {e}"

def unzip_file(zipname):
    try:
        with zipfile.ZipFile(zipname, 'r') as zf:
            zf.extractall('.')
        return f"Archive {zipname} extracted"
    except Exception as e:
        return f"Error: {e}"

def hash_file(path, algo='md5'):
    try:
        h = hashlib.new(algo)
        with open(path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                h.update(chunk)
        return f"{algo.upper()} {path}: {h.hexdigest()}"
    except Exception as e:
        return f"Error: {e}"

def base64_encode(text):
    return base64.b64encode(text.encode()).decode()

def base64_decode(text):
    try:
        return base64.b64decode(text).decode()
    except:
        return "Decoding error"

def url_encode(text):
    from urllib.parse import quote
    return quote(text)

def url_decode(text):
    from urllib.parse import unquote
    return unquote(text)

def list_services():
    try:
        if platform.system() == 'Windows':
            result = subprocess.run(['sc', 'query', 'state=all'], capture_output=True, text=True)
            return result.stdout
        else:
            result = subprocess.run(['systemctl', 'list-units', '--type=service', '--all'], capture_output=True, text=True)
            return result.stdout
    except Exception as e:
        return f"Error: {e}"

def service_start(name):
    try:
        if platform.system() == 'Windows':
            subprocess.run(['sc', 'start', name], capture_output=True, text=True)
            return f"Service {name} started"
        else:
            subprocess.run(['systemctl', 'start', name], capture_output=True, text=True)
            return f"Service {name} started"
    except Exception as e:
        return f"Error: {e}"

def service_stop(name):
    try:
        if platform.system() == 'Windows':
            subprocess.run(['sc', 'stop', name], capture_output=True, text=True)
            return f"Service {name} stopped"
        else:
            subprocess.run(['systemctl', 'stop', name], capture_output=True, text=True)
            return f"Service {name} stopped"
    except Exception as e:
        return f"Error: {e}"

def service_info(name):
    try:
        if platform.system() == 'Windows':
            result = subprocess.run(['sc', 'query', name], capture_output=True, text=True)
            return result.stdout
        else:
            result = subprocess.run(['systemctl', 'status', name], capture_output=True, text=True)
            return result.stdout
    except Exception as e:
        return f"Error: {e}"

def start_app(path):
    try:
        subprocess.Popen([path], shell=True)
        return f"Started: {path}"
    except Exception as e:
        return f"Error: {e}"

def stop_app(name):
    try:
        if platform.system() == 'Windows':
            subprocess.run(['taskkill', '/f', '/im', name], capture_output=True, text=True)
            return f"Process {name} terminated"
        else:
            subprocess.run(['pkill', name], capture_output=True, text=True)
            return f"Process {name} terminated"
    except Exception as e:
        return f"Error: {e}"

def chkdsk():
    try:
        if platform.system() == 'Windows':
            result = subprocess.run(['chkdsk', 'C:'], capture_output=True, text=True)
            return result.stdout
        else:
            return "chkdsk only on Windows"
    except Exception as e:
        return f"Error: {e}"

def sfc_scan():
    try:
        if platform.system() == 'Windows':
            result = subprocess.run(['sfc', '/scannow'], capture_output=True, text=True)
            return result.stdout
        else:
            return "sfc only on Windows"
    except Exception as e:
        return f"Error: {e}"

def powercfg():
    try:
        if platform.system() == 'Windows':
            result = subprocess.run(['powercfg', '/list'], capture_output=True, text=True)
            return result.stdout
        else:
            return "powercfg only on Windows"
    except Exception as e:
        return f"Error: {e}"

def powercfg_battery_report():
    try:
        if platform.system() == 'Windows':
            subprocess.run(['powercfg', '/batteryreport'], capture_output=True, text=True)
            return "Battery report created in current folder"
        else:
            return "powercfg only on Windows"
    except Exception as e:
        return f"Error: {e}"

def monitor_off():
    try:
        if platform.system() == 'Windows':
            ctypes.windll.user32.SendMessageW(0xFFFF, 0x0112, 0xF170, 2)
            return "Monitor turned off"
        else:
            return "Only on Windows"
    except Exception as e:
        return f"Error: {e}"

def eject_drive(drive):
    try:
        if platform.system() == 'Windows':
            subprocess.run(['powershell', '-c', f'(New-Object -ComObject Shell.Application).NameSpace(17).ParseName("{drive}").InvokeVerb("Eject")'], capture_output=True)
            return f"Drive {drive} ejected"
        else:
            return "Only on Windows"
    except Exception as e:
        return f"Error: {e}"

def msg_user(text):
    try:
        if platform.system() == 'Windows':
            subprocess.Popen(['msg', '*', text])
            return f"Message sent: {text}"
        else:
            return "msg only on Windows"
    except Exception as e:
        return f"Error: {e}"

def set_wallpaper(path):
    try:
        if platform.system() == 'Windows':
            ctypes.windll.user32.SystemParametersInfoW(20, 0, path, 3)
            return f"Wallpaper set: {path}"
        else:
            return "Only on Windows"
    except Exception as e:
        return f"Error: {e}"

def event_log():
    try:
        if platform.system() == 'Windows':
            result = subprocess.run(['wevtutil', 'qe', 'System', '/c:10', '/rd:true', '/f:text'], capture_output=True, text=True)
            return result.stdout
        else:
            return "Only on Windows"
    except Exception as e:
        return f"Error: {e}"

def clear_event_logs():
    try:
        if platform.system() == 'Windows':
            subprocess.run(['wevtutil', 'cl', 'System'], capture_output=True)
            return "Event logs cleared"
        else:
            return "Only on Windows"
    except Exception as e:
        return f"Error: {e}"

def beep():
    try:
        if platform.system() == 'Windows':
            import winsound
            winsound.Beep(1000, 500)
            return "Beep"
        else:
            print('\a')
            return "Beep"
    except:
        return "Error"

def volume_up():
    try:
        if platform.system() == 'Windows':
            subprocess.Popen(['powershell', '-c', '(New-Object -ComObject WScript.Shell).SendKeys([char]175)'])
            return "Volume +10 (approx)"
        else:
            subprocess.Popen(['amixer', 'set', 'Master', '10%+'])
            return "Volume +10%"
    except Exception as e:
        return f"Error: {e}"

def volume_down():
    try:
        if platform.system() == 'Windows':
            subprocess.Popen(['powershell', '-c', '(New-Object -ComObject WScript.Shell).SendKeys([char]174)'])
            return "Volume -10 (approx)"
        else:
            subprocess.Popen(['amixer', 'set', 'Master', '10%-'])
            return "Volume -10%"
    except Exception as e:
        return f"Error: {e}"

def tracert(host):
    try:
        cmd = 'tracert' if platform.system() == 'Windows' else 'traceroute'
        result = subprocess.run([cmd, host], capture_output=True, text=True, timeout=30)
        return result.stdout
    except Exception as e:
        return f"Error: {e}"

def nslookup(host):
    try:
        result = subprocess.run(['nslookup', host], capture_output=True, text=True)
        return result.stdout
    except Exception as e:
        return f"Error: {e}"

def netstat():
    try:
        result = subprocess.run(['netstat'], capture_output=True, text=True)
        return result.stdout
    except Exception as e:
        return f"Error: {e}"

def netstat_an():
    try:
        result = subprocess.run(['netstat', '-an'], capture_output=True, text=True)
        return result.stdout
    except Exception as e:
        return f"Error: {e}"

def tasklist():
    try:
        if platform.system() == 'Windows':
            result = subprocess.run(['tasklist'], capture_output=True, text=True)
            return result.stdout
        else:
            result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
            return result.stdout
    except Exception as e:
        return f"Error: {e}"

def ipconfig():
    try:
        if platform.system() == 'Windows':
            result = subprocess.run(['ipconfig'], capture_output=True, text=True)
            return result.stdout
        else:
            result = subprocess.run(['ifconfig'], capture_output=True, text=True)
            return result.stdout
    except Exception as e:
        return f"Error: {e}"

def ipconfig_all():
    try:
        if platform.system() == 'Windows':
            result = subprocess.run(['ipconfig', '/all'], capture_output=True, text=True)
            return result.stdout
        else:
            return "ipconfig /all only on Windows"
    except Exception as e:
        return f"Error: {e}"

def systeminfo():
    try:
        if platform.system() == 'Windows':
            result = subprocess.run(['systeminfo'], capture_output=True, text=True)
            return result.stdout
        else:
            result = subprocess.run(['uname', '-a'], capture_output=True, text=True)
            return result.stdout
    except Exception as e:
        return f"Error: {e}"

def reg_query(path):
    try:
        if platform.system() == 'Windows':
            result = subprocess.run(['reg', 'query', path], capture_output=True, text=True)
            return result.stdout
        else:
            return "reg only on Windows"
    except Exception as e:
        return f"Error: {e}"

def wmic(query):
    try:
        if platform.system() == 'Windows':
            result = subprocess.run(['wmic'] + query.split(), capture_output=True, text=True)
            return result.stdout
        else:
            return "wmic only on Windows"
    except Exception as e:
        return f"Error: {e}"

def shutdown_delay(seconds):
    try:
        if platform.system() == 'Windows':
            subprocess.Popen(['shutdown', '/s', '/t', str(seconds)])
            return f"Shutdown in {seconds} seconds. Cancel: shutdown /a"
        else:
            return "Only on Windows"
    except Exception as e:
        return f"Error: {e}"

def reboot_delay(seconds):
    try:
        if platform.system() == 'Windows':
            subprocess.Popen(['shutdown', '/r', '/t', str(seconds)])
            return f"Reboot in {seconds} seconds. Cancel: shutdown /a"
        else:
            return "Only on Windows"
    except Exception as e:
        return f"Error: {e}"

@app.route('/api/processes')
def api_processes():
    if not session.get('authenticated'):
        return jsonify({'error': 'Unauthorized'}), 401
    if not PSUTIL_AVAILABLE:
        return jsonify({'error': 'psutil not installed'}), 500
    try:
        procs = []
        for p in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                info = p.info
                info['cpu_percent'] = info.get('cpu_percent', 0.0)
                info['memory_percent'] = info.get('memory_percent', 0.0)
                procs.append(info)
            except:
                pass
        procs.sort(key=lambda x: x.get('cpu_percent', 0), reverse=True)
        return jsonify(procs[:50])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/', methods=['GET', 'POST'])
def index():
    if not session.get('authenticated'):
        if request.method == 'POST' and request.form.get('password') == PASSWORD:
            session['authenticated'] = True
            return redirect(url_for('index'))
        error = None
        if request.method == 'POST':
            error = 'Invalid password'
        return render_template_string(LOGIN_PAGE, error=error)

    if request.method == 'POST' or request.args.get('cmd'):
        cmd = request.form.get('cmd') or request.args.get('cmd')
        cmd = cmd.strip() if cmd else ''
        if not cmd:
            return '⏺️ Empty command'

        if cmd == '/screenshot':
            return make_screenshot()
        elif cmd == '/sysinfo':
            info = get_system_info()
            lines = []
            lines.append(f"OS: {info.get('os', 'unknown')}")
            lines.append(f"Version: {info.get('version', '')}")
            lines.append(f"Processor: {info.get('processor', 'unknown')}")
            if PSUTIL_AVAILABLE:
                lines.append(f"CPU: {info.get('cpu_percent', 0)}%")
                lines.append(f"RAM: {info.get('memory_used', 0)} / {info.get('memory_total', 0)} GB ({info.get('memory_percent', 0)}%)")
                lines.append(f"Disk: {info.get('disk_used', 0)} / {info.get('disk_total', 0)} GB ({info.get('disk_percent', 0)}%)")
            else:
                lines.append("Install psutil for detailed info: pip install psutil")
            return '\n'.join(lines)
        elif cmd == '/systeminfo':
            return systeminfo()
        elif cmd == '/clipboard':
            return get_clipboard_text()
        elif cmd == '/uptime':
            return get_uptime()
        elif cmd.startswith('/shutdown '):
            sec = cmd.split(' ', 1)[1]
            return shutdown_delay(sec)
        elif cmd == '/shutdown':
            if platform.system() == 'Windows':
                subprocess.Popen(['shutdown', '/s', '/t', '5'])
                return "Shutdown in 5 seconds. Cancel: shutdown /a"
            else:
                subprocess.Popen(['shutdown', '-h', 'now'])
                return "Shutting down..."
        elif cmd.startswith('/reboot '):
            sec = cmd.split(' ', 1)[1]
            return reboot_delay(sec)
        elif cmd == '/reboot':
            if platform.system() == 'Windows':
                subprocess.Popen(['shutdown', '/r', '/t', '5'])
                return "Reboot in 5 seconds. Cancel: shutdown /a"
            else:
                subprocess.Popen(['reboot', 'now'])
                return "Rebooting..."
        elif cmd == '/hibernate':
            return hibernate_pc()
        elif cmd == '/logoff':
            return logoff_user()
        elif cmd == '/processes':
            return get_process_list()
        elif cmd == '/taskmanager':
            if not PSUTIL_AVAILABLE:
                return "Install psutil for Task Manager"
            return '__TASKMANAGER__'
        elif cmd.startswith('/kill '):
            pid = cmd.split(' ', 1)[1]
            return kill_process(pid)
        elif cmd.startswith('/download '):
            url = cmd.split(' ', 1)[1]
            return download_file(url)
        elif cmd.startswith('/notify '):
            text = cmd.split(' ', 1)[1]
            return show_notification(text)
        elif cmd.startswith('/volume '):
            level = cmd.split(' ', 1)[1]
            return set_volume(level)
        elif cmd == '/volume-up':
            return volume_up()
        elif cmd == '/volume-down':
            return volume_down()
        elif cmd == '/mute':
            return mute_system()
        elif cmd == '/lock':
            return lock_screen()
        elif cmd == '/sleep':
            return sleep_pc()
        elif cmd == '/wifi':
            return get_wifi_info()
        elif cmd == '/restart-explorer':
            return restart_explorer()
        elif cmd == '/listdir':
            return list_directory()
        elif cmd.startswith('/listdir '):
            return list_directory(cmd.split(' ', 1)[1])
        elif cmd == '/disk-usage':
            return disk_usage()
        elif cmd.startswith('/open '):
            path = cmd.split(' ', 1)[1]
            return open_folder(path)
        elif cmd == '/ip':
            return get_my_ip()
        elif cmd.startswith('/ping '):
            host = cmd.split(' ', 1)[1]
            return ping(host)
        elif cmd.startswith('/tracert '):
            host = cmd.split(' ', 1)[1]
            return tracert(host)
        elif cmd.startswith('/nslookup '):
            host = cmd.split(' ', 1)[1]
            return nslookup(host)
        elif cmd == '/netstat':
            return netstat()
        elif cmd == '/netstat -an':
            return netstat_an()
        elif cmd.startswith('/netstat '):
            return subprocess.run(cmd[1:], shell=True, capture_output=True, text=True).stdout
        elif cmd == '/clear-temp':
            return clear_temp()
        elif cmd == '/battery':
            return battery_info()
        elif cmd == '/cpu-info':
            return cpu_info()
        elif cmd == '/gpu-info':
            return gpu_info()
        elif cmd == '/random-pass':
            return random_password()
        elif cmd == '/whoami':
            return whoami()
        elif cmd == '/date':
            return get_date()
        elif cmd == '/hostname':
            return get_hostname()
        elif cmd == '/env':
            return get_env_vars()
        elif cmd.startswith('/setenv '):
            var = cmd.split(' ', 1)[1]
            return set_env_var(var)
        elif cmd == '/path':
            return get_path()
        elif cmd.startswith('/where '):
            file = cmd.split(' ', 1)[1]
            return where(file)
        elif cmd.startswith('/mkdir '):
            path = cmd.split(' ', 1)[1]
            return mkdir(path)
        elif cmd.startswith('/rmdir '):
            path = cmd.split(' ', 1)[1]
            return rmdir(path)
        elif cmd.startswith('/del '):
            path = cmd.split(' ', 1)[1]
            return delete_file(path)
        elif cmd.startswith('/type '):
            path = cmd.split(' ', 1)[1]
            return type_file(path)
        elif cmd.startswith('/copy '):
            args = cmd.split(' ', 2)
            if len(args) < 3: return "Use /copy src dst"
            return copy_file(args[1], args[2])
        elif cmd.startswith('/move '):
            args = cmd.split(' ', 2)
            if len(args) < 3: return "Use /move src dst"
            return move_file(args[1], args[2])
        elif cmd.startswith('/rename '):
            args = cmd.split(' ', 2)
            if len(args) < 3: return "Use /rename old new"
            return rename_file(args[1], args[2])
        elif cmd.startswith('/zip '):
            args = cmd.split(' ', 2)
            if len(args) < 3: return "Use /zip archive.zip folder"
            return zip_folder(args[1], args[2])
        elif cmd.startswith('/unzip '):
            zipname = cmd.split(' ', 1)[1]
            return unzip_file(zipname)
        elif cmd.startswith('/md5 '):
            path = cmd.split(' ', 1)[1]
            return hash_file(path, 'md5')
        elif cmd.startswith('/sha1 '):
            path = cmd.split(' ', 1)[1]
            return hash_file(path, 'sha1')
        elif cmd.startswith('/sha256 '):
            path = cmd.split(' ', 1)[1]
            return hash_file(path, 'sha256')
        elif cmd.startswith('/base64-encode '):
            text = cmd.split(' ', 1)[1]
            return base64_encode(text)
        elif cmd.startswith('/base64-decode '):
            text = cmd.split(' ', 1)[1]
            return base64_decode(text)
        elif cmd.startswith('/urlencode '):
            text = cmd.split(' ', 1)[1]
            return url_encode(text)
        elif cmd.startswith('/urldecode '):
            text = cmd.split(' ', 1)[1]
            return url_decode(text)
        elif cmd == '/services':
            return list_services()
        elif cmd.startswith('/service-start '):
            name = cmd.split(' ', 1)[1]
            return service_start(name)
        elif cmd.startswith('/service-stop '):
            name = cmd.split(' ', 1)[1]
            return service_stop(name)
        elif cmd.startswith('/service-info '):
            name = cmd.split(' ', 1)[1]
            return service_info(name)
        elif cmd.startswith('/start '):
            path = cmd.split(' ', 1)[1]
            return start_app(path)
        elif cmd.startswith('/stop '):
            name = cmd.split(' ', 1)[1]
            return stop_app(name)
        elif cmd == '/chkdsk':
            return chkdsk()
        elif cmd == '/sfc':
            return sfc_scan()
        elif cmd == '/powercfg':
            return powercfg()
        elif cmd == '/powercfg-battery':
            return powercfg_battery_report()
        elif cmd == '/monitor-off':
            return monitor_off()
        elif cmd.startswith('/eject '):
            drive = cmd.split(' ', 1)[1]
            return eject_drive(drive)
        elif cmd.startswith('/msg '):
            text = cmd.split(' ', 1)[1]
            return msg_user(text)
        elif cmd.startswith('/wallpaper '):
            path = cmd.split(' ', 1)[1]
            return set_wallpaper(path)
        elif cmd == '/eventlog':
            return event_log()
        elif cmd == '/clear-logs':
            return clear_event_logs()
        elif cmd == '/beep':
            return beep()
        elif cmd == '/ipconfig':
            return ipconfig()
        elif cmd == '/ipconfig /all':
            return ipconfig_all()
        elif cmd == '/tasklist':
            return tasklist()
        elif cmd.startswith('/reg query '):
            path = cmd.split(' ', 2)[2] if len(cmd.split(' ', 2)) > 2 else cmd.split(' ', 1)[1]
            return reg_query(path)
        elif cmd.startswith('/wmic '):
            query = cmd.split(' ', 1)[1]
            return wmic(query)
        elif cmd.startswith('/extra '):
            return f"Executed extra command: {cmd}"
        else:
            try:
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
                output = result.stdout + result.stderr
                if not output:
                    output = '(command executed, output empty)'
                return output
            except subprocess.TimeoutExpired:
                return '⏱️ Timeout 30 seconds'
            except Exception as e:
                return f'❌ Error: {e}'

    return render_template_string(MAIN_PAGE,
                                  os=platform.system(),
                                  pyver=f"{sys.version_info.major}.{sys.version_info.minor}",
                                  local_ip=get_local_ip(),
                                  psutil_avail=PSUTIL_AVAILABLE,
                                  pil_avail=PIL_AVAILABLE)

@app.route('/panel')
def panel():
    if not session.get('authenticated'):
        return redirect(url_for('index'))
    return render_template_string(PANEL_PAGE,
                                  categories=CATEGORIES,
                                  total=len(COMMANDS),
                                  local_ip=get_local_ip())

@app.route('/logout')
def logout():
    session.pop('authenticated', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    print(f"Server running. Accessible on local network at: http://{get_local_ip()}:8000")
    print("Password: 8471")
    print(f"Total commands: {len(COMMANDS)}")
    print("Open /panel for visual command panel.")
    app.run(host='0.0.0.0', port=8000, debug=False)