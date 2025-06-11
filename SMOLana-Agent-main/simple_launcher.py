#!/usr/bin/env python3
"""
Simple Solana Trading Dashboard Launcher
Displays the trading dashboard in a webview window with a Flask server
"""

import os
import sys
import argparse
import asyncio
import logging
import threading
import socket
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s [%(name)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("solana_launcher")

# Check for required packages
required_packages = {
    'webview': 'pywebview',
    'flask': 'Flask'
}

missing_packages = []
for module_name, package_name in required_packages.items():
    try:
        __import__(module_name)
    except ImportError:
        missing_packages.append(f"{package_name}")
        
if missing_packages:
    logger.error(f"Missing packages: {', '.join(missing_packages)}")
    logger.error(f"Install with: pip install {' '.join(missing_packages)}")
    sys.exit(1)

# Import after checks
import webview
from flask import Flask, send_from_directory


def print_banner():
    """Print Solana Trading Desktop banner"""
    print("\n" + "=" * 70)
    print("  ____   ___  _        _    _   _    _     _____  ____      _    ____ ___ _   _  ____ ")
    print(" / ___| / _ \\| |      / \\  | \\ | |  / \\   |_   _|/ ___|    / \\  |  _ \\_ _| \\ | |/ ___|")
    print(" \\___ \\| | | | |     / _ \\ |  \\| | / _ \\    | |  \\___ \\   / _ \\ | | | | ||  \\| | |  _ ")
    print("  ___) | |_| | |___ / ___ \\| |\\  |/ ___ \\   | |   ___) | / ___ \\| |_| | || |\\  | |_| |")
    print(" |____/ \\___/|_____/_/   \\_\\_| \\_/_/   \\_\\  |_|  |____/ /_/   \\_\\____/___|_| \\_|\\____|")
    print("=" * 70)
    print("               SOLANA TRADING DASHBOARD")
    print("=" * 70 + "\n")


def verify_environment():
    """Verify environment variables"""
    # For demo purposes, skip actual environment check
    logger.warning("Environment check bypassed for demonstration")
    logger.warning("In a production setup, you would need to set:")
    logger.warning("  - E2B_API_KEY for E2B desktop environment")
    logger.warning("  - SOLANA_PRIVATE_KEY for trading capabilities")
    logger.warning("  - SCRAPY_API_KEY for browser automation (optional)")
    
    return True


def find_available_port(start_port=5000, max_port=5050):
    """Find an available port in the given range"""
    for port in range(start_port, max_port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(('localhost', port)) != 0:
                return port
    raise RuntimeError(f"No available port found in range {start_port}-{max_port}")


def create_flask_app():
    """Create and configure Flask app for serving dashboard files"""
    # Get dashboard directory
    dashboard_dir = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "desktop_trading"
    )
    
    app = Flask(__name__)
    
    # Route for serving the main dashboard
    @app.route('/')
    def index():
        return send_from_directory(dashboard_dir, 'trading_dashboard.html')
    
    # Route for serving static files (like JS and CSS)
    @app.route('/<path:filename>')
    def serve_static(filename):
        return send_from_directory(dashboard_dir, filename)
    
    return app, dashboard_dir


def start_flask_server(port):
    """Start Flask server in a separate thread"""
    app, dashboard_dir = create_flask_app()
    app.run(port=port, debug=False, use_reloader=False)


def launch_dashboard(debug=False, port=None):
    """Launch the trading dashboard in a webview window"""
    dashboard_dir = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 
        "desktop_trading"
    )
    
    dashboard_path = os.path.join(dashboard_dir, "trading_dashboard.html")
    if not os.path.exists(dashboard_path):
        logger.error(f"Trading dashboard not found at {dashboard_path}")
        return
    
    # Find available port if not specified
    if port is None:
        port = find_available_port()
    
    # Start Flask server in a separate thread
    logger.info(f"Starting Flask server on port {port}")
    flask_thread = threading.Thread(target=start_flask_server, args=(port,))
    flask_thread.daemon = True
    flask_thread.start()
    
    # Allow Flask server to start
    import time
    time.sleep(1)
    
    # Create webview window pointing to Flask server
    logger.info("Opening webview window")
    webview.create_window(
        title="Solana Trading Dashboard",
        url=f"http://localhost:{port}",
        width=1200,
        height=800,
        min_size=(800, 600)
    )
    
    # Start the webview event loop
    webview.start(debug=debug)


def main():
    """Main entry point"""
    print_banner()
    
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Launch Solana Trading Dashboard")
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--port', type=int, help='Specify port for the Flask server')
    parser.add_argument('--fullscreen', action='store_true', help='Launch in fullscreen mode')
    args = parser.parse_args()
    
    if not verify_environment():
        sys.exit(1)
    
    logger.info("Launching Solana Trading Dashboard...")
    launch_dashboard(debug=args.debug, port=args.port)


if __name__ == "__main__":
    main()
