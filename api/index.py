"""
Vercel Serverless Function entry point for Overflow Detective.

Handles HTTP requests on Vercel:
- /convert: Positional number system conversions and signed integer encodings.
- /add: Bit-by-bit full-adder addition and overflow detection.
- /bugs: Historical engineering integer overflow case studies.
- /: Serves the interactive index.html dashboard.
"""

import json
import os
import sys
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

# Ensure project root is in sys.path so main.py can be imported
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import main

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


class handler(BaseHTTPRequestHandler):
    """Vercel serverless request handler."""

    def send_response_data(self, data, content_type="application/json; charset=utf-8", status=200):
        body = data if isinstance(data, bytes) else json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        query = parse_qs(parsed.query)
        endpoint = query.get("endpoint", [""])[0]
        path = parsed.path.rstrip("/")

        try:
            # Endpoint 1: Number Base & Signed Representation Conversion
            if endpoint == "convert" or path.endswith("/convert"):
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
            if endpoint == "add" or path.endswith("/add"):
                a = get_query_int(query, "a", default=0)
                b = get_query_int(query, "b", default=0)
                bits = get_bit_width(query)
                result = main.add_and_check(a, b, bits)
                return self.send_response_data(result)

            # Endpoint 3: Real-World Bug Case Studies
            if endpoint == "bugs" or path.endswith("/bugs"):
                return self.send_response_data(main.REAL_BUGS)

            # Report PDF serving fallback
            if path.endswith("4_COA_Report_Easala_Jagadeesh.pdf") or endpoint == "report":
                pdf_path = os.path.join(ROOT_DIR, "4_COA_Report_Easala_Jagadeesh.pdf")
                if os.path.exists(pdf_path):
                    with open(pdf_path, "rb") as f:
                        return self.send_response_data(f.read(), "application/pdf")

            # Root path fallback
            if path in ("", "/", "/index", "/index.html", "/api"):
                html_path = os.path.join(ROOT_DIR, "index.html")
                if os.path.exists(html_path):
                    with open(html_path, "rb") as f:
                        return self.send_response_data(f.read(), "text/html; charset=utf-8")

            self.send_error(404, "Endpoint not found")

        except ValueError as err:
            self.send_response_data({"error": str(err)}, status=400)
        except Exception as err:
            self.send_response_data({"error": f"Internal server error: {err}"}, status=500)

    def log_message(self, format_str, *args):
        # Keep serverless logs clean
        sys.stderr.write(f"[{self.log_date_time_string()}] {format_str % args}\n")
