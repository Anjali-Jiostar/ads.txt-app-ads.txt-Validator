#!/usr/bin/env python3
"""
Local proxy server for ads-txt-validator.
Run:  python3 server.py
Open: http://localhost:8080
"""
import http.server
import json
import os
import ssl
import subprocess
import urllib.request

PORT = int(os.environ.get('PORT', '8080'))
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HTML = os.path.join(BASE_DIR, 'ads-txt-validator.html')
TARGET = 'https://www.hotstar.com/ads.txt'
SSL_CTX = ssl.create_default_context()
BOOTSTRAP_TOKEN = 'window.__BOOTSTRAP_ADS_TXT__ = null;'
BOOTSTRAP_ERROR_TOKEN = 'window.__BOOTSTRAP_ADS_TXT_ERROR__ = "";'


def fetch_remote_text(url: str) -> str:
    errors = []

    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36',
            'Accept': 'text/plain,text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'identity',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
        })
        with urllib.request.urlopen(req, timeout=20, context=SSL_CTX) as response:
            return response.read().decode('utf-8', 'replace')
    except Exception as exc:
        errors.append(f'urllib: {exc}')

    try:
        proc = subprocess.run(
            ['curl', '-L', '--silent', '--show-error', '--max-time', '20', url],
            capture_output=True,
            text=True,
            check=True,
        )
        return proc.stdout
    except Exception as exc:
        errors.append(f'curl: {exc}')

    raise RuntimeError(' | '.join(errors))


class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def do_GET(self):
        if self.path in ('/', '/index.html'):
            with open(HTML, 'r', encoding='utf-8') as file:
                body = file.read()

            try:
                ads_text = fetch_remote_text(TARGET)
                body = body.replace(
                    BOOTSTRAP_TOKEN,
                    f'window.__BOOTSTRAP_ADS_TXT__ = {json.dumps(ads_text)};'
                )
            except Exception as exc:
                body = body.replace(
                    BOOTSTRAP_ERROR_TOKEN,
                    f'window.__BOOTSTRAP_ADS_TXT_ERROR__ = {json.dumps(str(exc))};'
                )

            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Cache-Control', 'no-store')
            self.end_headers()
            self.wfile.write(body.encode('utf-8'))
            return

        if self.path.startswith('/hotstar-ads.txt'):
            try:
                body = fetch_remote_text(TARGET).encode('utf-8')
                self.send_response(200)
                self.send_header('Content-Type', 'text/plain; charset=utf-8')
                self.send_header('Cache-Control', 'no-store')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(body)
            except Exception as exc:
                self.send_error(502, str(exc))
            return

        self.send_error(404)


if __name__ == '__main__':
    server = http.server.ThreadingHTTPServer(('127.0.0.1', PORT), Handler)
    print(f'\n  Server running -> http://localhost:{PORT}')
    print('  Open that URL in your browser, not the HTML file directly.')
    print('  Press Ctrl+C to stop.\n')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('Server stopped.')
