#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
NINA SERVER
Simple HTTP server to serve Nina PDA consumer interface
═══════════════════════════════════════════════════════════════════════════════
"""

import http.server
import socketserver
import os
import webbrowser
from pathlib import Path

PORT = 8080
DIRECTORY = Path(__file__).parent / "consumer"


class NinaHandler(http.server.SimpleHTTPRequestHandler):
    """Handler that serves files from the consumer directory."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DIRECTORY), **kwargs)
    
    def log_message(self, format, *args):
        """Custom log format."""
        print(f"[NINA] {self.address_string()} - {format % args}")


def main():
    """Start the Nina server."""
    print(r"""
    ═══════════════════════════════════════════════════════════════════════════
    
    ███╗   ██╗██╗███╗   ██╗ █████╗ 
    ████╗  ██║██║████╗  ██║██╔══██╗
    ██╔██╗ ██║██║██╔██╗ ██║███████║
    ██║╚██╗██║██║██║╚██╗██║██╔══██║
    ██║ ╚████║██║██║ ╚████║██║  ██║
    ╚═╝  ╚═══╝╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝
                                    
    Newton-Inspired Network Assistant
    Contemporary Apple Newton MessagePad Reimagined
    
    ═══════════════════════════════════════════════════════════════════════════
    """)
    
    print(f"📂 Serving from: {DIRECTORY}")
    print(f"🌐 Server URL: http://localhost:{PORT}")
    print(f"⏹  Press Ctrl+C to stop\n")
    
    with socketserver.TCPServer(("", PORT), NinaHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n[NINA] Server stopped.")


if __name__ == "__main__":
    main()
