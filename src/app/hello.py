import os
from wsgiref.simple_server import make_server

HTML_CONTENT = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Slot Machine Simulator - Hello World</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg-start: #0a0e17;
      --bg-end: #121b2d;
      --card-bg: rgba(255, 255, 255, 0.05);
      --card-border: rgba(255, 255, 255, 0.12);
      --accent-start: #6366f1;
      --accent-end: #a855f7;
      --text-primary: #f8fafc;
      --text-secondary: #94a3b8;
      --success: #10b981;
    }

    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }

    body {
      font-family: 'Outfit', sans-serif;
      min-height: 100vh;
      background: radial-gradient(circle at 50% 20%, #1e1e38 0%, var(--bg-start) 60%, #05070a 100%);
      color: var(--text-primary);
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 24px;
    }

    .card {
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      backdrop-filter: blur(16px);
      -webkit-backdrop-filter: blur(16px);
      border-radius: 24px;
      padding: 48px 40px;
      max-width: 520px;
      width: 100%;
      text-align: center;
      box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5), 0 0 40px rgba(99, 102, 241, 0.15);
      animation: fadeIn 0.8s ease-out;
    }

    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(16px); }
      to { opacity: 1; transform: translateY(0); }
    }

    .badge {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 6px 14px;
      border-radius: 9999px;
      background: rgba(16, 185, 129, 0.15);
      border: 1px solid rgba(16, 185, 129, 0.3);
      color: #34d399;
      font-size: 0.875rem;
      font-weight: 600;
      margin-bottom: 24px;
    }

    .badge-dot {
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: var(--success);
      box-shadow: 0 0 10px var(--success);
      animation: pulse 2s infinite;
    }

    @keyframes pulse {
      0%, 100% { opacity: 1; transform: scale(1); }
      50% { opacity: 0.5; transform: scale(0.85); }
    }

    h1 {
      font-size: 2.75rem;
      font-weight: 700;
      letter-spacing: -0.02em;
      margin-bottom: 12px;
      background: linear-gradient(135deg, #ffffff 30%, #a5b4fc 70%, #c084fc 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }

    p {
      color: var(--text-secondary);
      font-size: 1.05rem;
      line-height: 1.6;
      margin-bottom: 28px;
    }

    .info-box {
      background: rgba(0, 0, 0, 0.3);
      border-radius: 12px;
      padding: 14px 18px;
      margin-bottom: 28px;
      font-family: 'JetBrains Mono', monospace;
      font-size: 0.875rem;
      color: #cbd5e1;
      display: flex;
      justify-content: space-between;
      align-items: center;
      border: 1px solid rgba(255, 255, 255, 0.05);
    }

    .btn {
      background: linear-gradient(135deg, var(--accent-start), var(--accent-end));
      color: white;
      border: none;
      padding: 14px 32px;
      border-radius: 12px;
      font-size: 1rem;
      font-weight: 600;
      font-family: inherit;
      cursor: pointer;
      transition: transform 0.2s, box-shadow 0.2s, background 0.3s;
      box-shadow: 0 10px 20px -5px rgba(99, 102, 241, 0.4);
    }

    .btn:hover {
      transform: translateY(-2px);
      box-shadow: 0 14px 24px -5px rgba(99, 102, 241, 0.6);
    }

    .btn:active {
      transform: translateY(0);
    }

    .footer {
      margin-top: 24px;
      font-size: 0.825rem;
      color: #64748b;
    }
  </style>
</head>
<body>
  <main class="card">
    <div class="badge">
      <span class="badge-dot"></span>
      Render.com Deployment Test
    </div>
    <h1>Hello World!</h1>
    <p>Your Python web service is up and running successfully.</p>
    <div class="info-box">
      <span>Service Target:</span>
      <span>Render.com Cloud Host</span>
    </div>
    <button class="btn" id="ok-btn" onclick="handleClick()">OK & Let's Go 🎰</button>
    <p class="footer" id="status-msg">Slot Machine Simulator Project</p>
  </main>
  <script>
    function handleClick() {
      const btn = document.getElementById('ok-btn');
      const msg = document.getElementById('status-msg');
      btn.textContent = 'Connection Verified! ✨';
      btn.style.background = 'linear-gradient(135deg, #059669, #10b981)';
      msg.textContent = 'Web server connection confirmed. Ready for the next milestone!';
      msg.style.color = '#34d399';
    }
  </script>
</body>
</html>
"""


def app(environ, start_response):
    """WSGI application callable for gunicorn, waitress, or standard WSGI servers."""
    response_body = HTML_CONTENT.encode("utf-8")
    status = "200 OK"
    headers = [
        ("Content-Type", "text/html; charset=utf-8"),
        ("Content-Length", str(len(response_body))),
    ]
    start_response(status, headers)
    return [response_body]


def main():
    # Render.com provides the port dynamically in the PORT environment variable
    port = int(os.environ.get("PORT", 8000))
    host = "0.0.0.0"

    print(f"✨ Server running on http://localhost:{port} (host: {host})")
    print("Press Ctrl+C to stop.")

    with make_server(host, port, app) as httpd:
        httpd.serve_forever()


if __name__ == "__main__":
    main()
