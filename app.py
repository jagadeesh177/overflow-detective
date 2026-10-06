"""
Overflow Detective: Web Server
Provides an HTTP interface for the Computer Organization & Architecture
signed number representation and overflow detection simulator.
Author: Easala Jagadeesh (GitHub: @jagadeesh177)

Usage:
    python app.py
    python app.py --port 8001
"""

import sys
import os
import json
import argparse
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

# Ensure local imports and file paths resolve relative to this script directory
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)
os.chdir(CURRENT_DIR)

import main  # Core simulation logic

VALID_BIT_SIZES = (4, 8, 16, 32)


def get_query_int(query, param_name, default=0):
    """Safely extract an integer parameter from query dictionary."""
    val = query.get(param_name, [str(default)])[0]
    return int(val)


def get_bit_width(query):
    """Extract and validate the bit width parameter."""
    bits = int(query.get("bits", ["8"])[0])
    if bits not in VALID_BIT_SIZES:
        raise ValueError(f"Bit width must be one of {VALID_BIT_SIZES}.")
    return bits


class OverflowRequestHandler(BaseHTTPRequestHandler):
    """HTTP request handler for the interactive web dashboard and REST endpoints."""

    def send_response_data(self, data, content_type="application/json", status=200):
        body = data if isinstance(data, bytes) else json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed_url = urlparse(self.path)
        query = parse_qs(parsed_url.query)

        try:
            # Serve the main dashboard page
            if parsed_url.path in ("/", "/index.html"):
                html_path = os.path.join(CURRENT_DIR, "index.html")
                with open(html_path, "rb") as html_file:
                    return self.send_response_data(
                        html_file.read(), content_type="text/html; charset=utf-8"
                    )

            # Endpoint 1: Number Base & Signed Representation Conversion
            if parsed_url.path == "/convert":
                n = get_query_int(query, "n", default=0)
                bits = get_bit_width(query)
                low, high = main.signed_range(bits)

                payload = {
                    "number": n,
                    "bits": bits,
                    "binary": main.to_base(abs(n), 2),
                    "octal": main.to_base(abs(n), 8),
                    "hex": main.to_base(abs(n), 16),
                    "negative": n < 0,
                    "low": low,
                    "high": high,
                    "fits": low <= n <= high,
                    "sign_magnitude": main.sign_magnitude(n, bits),
                    "ones_complement": main.ones_complement(n, bits),
                    "twos_complement": main.twos_complement(n, bits),
                    "bits_needed": main.bits_needed(n),
                }
                return self.send_response_data(payload)

            # Endpoint 2: Bit-Level Addition & Overflow Check
            if parsed_url.path == "/add":
                a = get_query_int(query, "a", default=0)
                b = get_query_int(query, "b", default=0)
                bits = get_bit_width(query)
                result = main.add_and_check(a, b, bits)
                return self.send_response_data(result)

            # Endpoint 3: Real-World Bug Case Studies
            if parsed_url.path == "/bugs":
                return self.send_response_data(main.REAL_BUGS)

            # Route not found
            self.send_response_data({"error": "Resource not found."}, status=404)

        except ValueError as err:
            self.send_response_data({"error": str(err)}, status=400)
        except Exception as err:
            self.send_response_data({"error": f"Internal server error: {err}"}, status=500)

    def log_message(self, format, *args):
        # Suppress routine request logging to maintain clean terminal output
        pass


def run_server(port=8001):
    server_address = ("127.0.0.1", port)
    httpd = HTTPServer(server_address, OverflowRequestHandler)
    print("=" * 64)
    print("Overflow Detective: Web Server Active")
    print(f"Local URL: http://localhost:{port}")
    print("Serving interactive dashboard. Press Ctrl+C to stop.")
    print("=" * 64)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer terminated by user.")
        httpd.server_close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Start Overflow Detective Web Server.")
    parser.add_argument("--port", type=int, default=8001, help="Port to listen on (default: 8001)")
    cli_args = parser.parse_args()
    run_server(port=cli_args.port)
