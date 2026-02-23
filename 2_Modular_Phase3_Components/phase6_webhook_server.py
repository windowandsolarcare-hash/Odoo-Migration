"""
Phase 6 Webhook Server: when an invoice is marked paid in Odoo, call this URL
to automatically sync payment to Workiz and mark the job Done.

Run this on a machine that can reach Odoo and Workiz (same box where you run
the other scripts, or a small VPS). Expose it with ngrok or a real URL so Odoo
(or Zapier) can POST to it.

  python phase6_webhook_server.py                    # Listen on 0.0.0.0:8765
  python phase6_webhook_server.py --port 8766        # Custom port
  set PHASE6_WEBHOOK_TOKEN=your-secret               # Optional: require header X-Webhook-Token

POST /sync-invoice (or /phase6):
  Content-Type: application/json
  Body: { "invoice_id": 123 }   (Odoo account.move id)

Response: 200 + JSON { "success": true, "invoice_id": 123, "job_uuid": "...", ... }
  or 400/500 + JSON { "success": false, "error": "..." }
"""

import argparse
import json
import os
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from phase6_payment_sync_to_workiz import run as phase6_run

DEFAULT_PORT = 8765
WEBHOOK_TOKEN = os.environ.get("PHASE6_WEBHOOK_TOKEN", "")
PROCESSED_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "phase6_webhook_processed.json")


def load_processed():
    if not os.path.exists(PROCESSED_FILE):
        return set()
    try:
        with open(PROCESSED_FILE, "r", encoding="utf-8") as f:
            return set(json.load(f))
    except Exception:
        return set()


def save_processed(ids_set):
    with open(PROCESSED_FILE, "w", encoding="utf-8") as f:
        json.dump(sorted(ids_set), f, indent=0)


class Phase6Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path not in ("/sync-invoice", "/phase6"):
            self._send(404, {"success": False, "error": "Not found. Use POST /sync-invoice or /phase6"})
            return
        if WEBHOOK_TOKEN:
            token = self.headers.get("X-Webhook-Token", "")
            if token != WEBHOOK_TOKEN:
                self._send(401, {"success": False, "error": "Invalid or missing X-Webhook-Token"})
                return
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length) if content_length else b""
        try:
            data = json.loads(body.decode("utf-8")) if body else {}
        except Exception as e:
            self._send(400, {"success": False, "error": f"Invalid JSON: {e}"})
            return
        raw = data.get("invoice_id")
        if raw is None:
            self._send(400, {"success": False, "error": "Missing invoice_id in JSON body"})
            return
        try:
            invoice_id = int(raw)
        except (TypeError, ValueError):
            self._send(400, {"success": False, "error": "invoice_id must be an integer"})
            return
        processed = load_processed()
        if invoice_id in processed:
            self._send(200, {"success": True, "invoice_id": invoice_id, "skipped": "already_processed"})
            return
        try:
            result = phase6_run(invoice_id)
        except Exception as e:
            self._send(500, {"success": False, "error": str(e)})
            return
        if result.get("success"):
            processed.add(invoice_id)
            save_processed(processed)
        status = 200 if result.get("success") else 400
        self._send(status, result)

    def do_GET(self):
        if self.path in ("/", "/health"):
            self._send(200, {"status": "ok", "message": "POST /sync-invoice with {\"invoice_id\": <id>}"})
            return
        self._send(404, {"success": False, "error": "Not found"})

    def _send(self, status, data):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode("utf-8"))

    def log_message(self, format, *args):
        print(f"[Phase6 Webhook] {args[0]}")


def main():
    ap = argparse.ArgumentParser(description="Phase 6 webhook server: POST invoice_id to sync paid invoice to Workiz")
    ap.add_argument("--port", type=int, default=DEFAULT_PORT, help=f"Port to listen on (default {DEFAULT_PORT})")
    ap.add_argument("--host", default="0.0.0.0", help="Host to bind (default 0.0.0.0)")
    args = ap.parse_args()
    server = HTTPServer((args.host, args.port), Phase6Handler)
    print(f"Phase 6 webhook server listening on http://{args.host}:{args.port}")
    print("  POST /sync-invoice with JSON {\"invoice_id\": <id>} to run Phase 6 for that invoice.")
    if WEBHOOK_TOKEN:
        print("  X-Webhook-Token required (set PHASE6_WEBHOOK_TOKEN).")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down.")
        server.shutdown()


if __name__ == "__main__":
    main()
