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
import webbrowser
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
from flask import Flask, send_from_directory, jsonify
from dotenv import load_dotenv

# Import our API routes blueprint
try:
    from desktop_trading.api_routes import api as api_blueprint
except ImportError:
    logger.error("Failed to import API routes. Make sure the solana_api.py module exists.")
    api_blueprint = None

# Load environment variables
load_dotenv()

# Set up API keys from environment variables
os.environ['SOLANA_RPC_URL'] = os.environ.get('SOLANA_RPC_URL', 'https://mainnet.helius-rpc.com/?api-key=c55c146c-71ef-41b9-a574-cb08f359c00c')
os.environ['OPENAI_API_KEY'] = os.environ.get('OPENAI_API_KEY', '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')
os.environ['OPENROUTER_API_KEY'] = os.environ.get('OPENROUTER_API_KEY', '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')
os.environ['OPENROUTER_MODEL'] = os.environ.get('OPENROUTER_MODEL', 'qwen/qwen2.5-vl-72b-instruct:free')


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
    """Verify environment variables and return environment status"""
    env_status = {}
    
    # Check Solana RPC URL
    rpc_url = os.environ.get('SOLANA_RPC_URL', '')
    env_status['helius_configured'] = 'helius-rpc.com' in rpc_url
    
    # Check OpenAI API key
    openai_key = os.environ.get('OPENAI_API_KEY', '')
    env_status['openai_configured'] = len(openai_key) > 20
    
    # Check OpenRouter API key
    openrouter_key = os.environ.get('OPENROUTER_API_KEY', '')
    env_status['openrouter_configured'] = len(openrouter_key) > 20
    
    # Check Scrapy API key
    scrapy_key = os.environ.get('SCRAPY_API_KEY', '')
    env_status['scrapy_configured'] = len(scrapy_key) > 5
    
    # Log warnings for missing components
    if not env_status['helius_configured']:
        logger.warning("SOLANA_RPC_URL not set with Helius endpoint")
    
    if not env_status['openai_configured']:
        logger.warning("OPENAI_API_KEY not properly configured")
    
    if not env_status['openrouter_configured']:
        logger.warning("OPENROUTER_API_KEY not properly configured")
        
    if not env_status['scrapy_configured']:
        logger.warning("SCRAPY_API_KEY not set - browser automation disabled")
    
    # Return True if at least Solana RPC and either OpenAI or OpenRouter are configured
    return env_status['helius_configured'] and (env_status['openai_configured'] or env_status['openrouter_configured']), env_status


def find_available_port(start_port=5000, max_port=5050):
    """Find an available port in the given range"""
    for port in range(start_port, max_port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(('localhost', port)) != 0:
                return port
    raise RuntimeError(f"No available port found in range {start_port}-{max_port}")


def create_flask_app(scrapybara_stream_url=None):
    """Create and configure Flask app for serving dashboard files
    
    Args:
        scrapybara_stream_url: Optional URL for Scrapybara stream to embed in dashboard
        
    Returns:
        Tuple of (Flask app, dashboard directory)
    """
    # Get dashboard directory
    dashboard_dir = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "desktop_trading"
    )
    
    # Create Flask app
    app = Flask(__name__, static_folder='desktop_trading', template_folder='desktop_trading')

    # Register API blueprint if available
    if api_blueprint is not None:
        app.register_blueprint(api_blueprint, url_prefix='/api')
        logger.info("API routes registered successfully")
    else:
        logger.warning("API blueprint not available. API endpoints will not be accessible.")

    # Route for the main dashboard
    @app.route('/')
    def index():
        # If we have a Scrapybara stream URL, inject it into the dashboard
        if scrapybara_stream_url:
            # Read dashboard HTML
            dashboard_path = os.path.join(dashboard_dir, 'trading_dashboard.html')
            with open(dashboard_path, 'r') as f:
                html_content = f.read()
                
            # Create a stream viewer component
            stream_viewer = f"""
            <div id="stream-viewer" style="margin-top: 20px; border: 1px solid #9945FF; border-radius: 10px; overflow: hidden;">
                <h2 style="background-color: #9945FF; color: white; margin: 0; padding: 10px;">Live Trading Agent View</h2>
                <iframe src="{scrapybara_stream_url}" style="width: 100%; height: 500px; border: none;"></iframe>
            </div>
            """
            
            # Inject viewer before closing body tag
            modified_html = html_content.replace('</body>', f'{stream_viewer}\n</body>')
            
            # Return the modified HTML
            from flask import Response
            return Response(modified_html, mimetype='text/html')
        
        # Otherwise return the normal dashboard
        return send_from_directory('desktop_trading', 'trading_dashboard.html')

    # Static files route
    @app.route('/<path:path>')
    def static_files(path):
        return send_from_directory('desktop_trading', path)

    # Status endpoint for checking API health
    @app.route('/status')
    def status():
        # Check if Helius RPC is configured
        rpc_url = os.environ.get('SOLANA_RPC_URL', '')
        helius_configured = 'helius-rpc.com' in rpc_url
        
        # Check if OpenAI API is configured
        openai_api_key = os.environ.get('OPENAI_API_KEY', '')
        openai_configured = len(openai_api_key) > 20
        
        # Get OpenRouter status
        openrouter_api_key = os.environ.get('OPENROUTER_API_KEY', '')
        openrouter_configured = len(openrouter_api_key) > 20
        
        return jsonify({
            'status': 'running',
            'helius_rpc_configured': helius_configured,
            'openai_configured': openai_configured,
            'openrouter_configured': openrouter_configured
        })
    
    return app, dashboard_dir


def start_flask_server(port, scrapybara_stream_url=None):
    """Start Flask server in a separate thread"""
    app, dashboard_dir = create_flask_app(scrapybara_stream_url)
    app.run(port=port, debug=False, use_reloader=False, host='0.0.0.0')


async def setup_scrapybara():
    """Set up Scrapybara instance and return stream URL"""
    try:
        from desktop_trading.integrations import ScrapybaraIntegration
        
        # Check for API key
        api_key = os.environ.get('SCRAPY_API_KEY')
        if not api_key:
            logger.error("SCRAPY_API_KEY not set - cannot initialize Scrapybara")
            return None
            
        # Initialize Scrapybara integration
        scrapybara = ScrapybaraIntegration(api_key=api_key)
        
        # Start instance and get stream URL
        instance_info = await scrapybara.start_instance(instance_type="browser", timeout_hours=1)
        stream_url = instance_info.get("stream_url")
        
        if not stream_url:
            logger.error("Failed to get Scrapybara stream URL")
            return None
            
        # Set up browser
        await scrapybara.setup_browser()
        
        logger.info(f"Scrapybara instance started with stream URL: {stream_url}")
        return stream_url
        
    except Exception as e:
        logger.error(f"Error setting up Scrapybara: {e}")
        return None

def launch_dashboard(debug=False, port=None, use_scrapybara=False, browser_only=False, fullscreen=False):
    """Launch the trading dashboard in a webview window
    
    Args:
        debug: Enable debug mode
        port: Port for Flask server
        use_scrapybara: Enable Scrapybara integration
        browser_only: Open in browser instead of webview window
        fullscreen: Launch in fullscreen mode
    """
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
        
    # Set up Scrapybara if requested
    scrapybara_stream_url = None
    if use_scrapybara:
        # Run asyncio loop to set up Scrapybara
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            scrapybara_stream_url = loop.run_until_complete(setup_scrapybara())
            if scrapybara_stream_url:
                logger.info(f"Scrapybara stream URL: {scrapybara_stream_url}")
                
                # Open stream URL in browser for direct viewing
                if browser_only:
                    webbrowser.open(scrapybara_stream_url)
        finally:
            loop.close()
    
    # Start Flask server in a separate thread
    logger.info(f"Starting Flask server on port {port}")
    flask_thread = threading.Thread(target=start_flask_server, args=(port, scrapybara_stream_url))
    flask_thread.daemon = True
    flask_thread.start()
    
    # Allow Flask server to start
    import time
    time.sleep(1)
    
    # Open in browser if requested
    if browser_only:
        webbrowser.open(f"http://localhost:{port}")
        logger.info(f"Opened dashboard in browser at http://localhost:{port}")
        
        # Keep main thread running
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Server stopped by user")
        return
    
    # Create webview window pointing to Flask server
    logger.info("Opening webview window")
    webview.create_window(
        title="Solana Trading Dashboard",
        url=f"http://localhost:{port}",
        width=1200,
        height=800,
        min_size=(800, 600),
        fullscreen=fullscreen
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
    parser.add_argument('--scrapybara', action='store_true', help='Enable Scrapybara browser automation and streaming')
    parser.add_argument('--browser-only', action='store_true', help='Open in browser instead of webview window')
    parser.add_argument('--stream-only', action='store_true', help='Open only the Scrapybara stream in browser')
    args = parser.parse_args()
    
    # Verify environment variables
    verified, env_status = verify_environment()
    if not verified:
        logger.error("Required environment variables missing")
        sys.exit(1)
        
    # Check for Scrapybara integration availability
    if args.scrapybara and not env_status['scrapy_configured']:
        logger.error("SCRAPY_API_KEY not set but --scrapybara option requested")
        logger.info("Either set SCRAPY_API_KEY environment variable or disable --scrapybara option")
        sys.exit(1)
        
    # Special case - stream only mode
    if args.stream_only:
        if not args.scrapybara:
            logger.error("--stream-only requires --scrapybara")
            sys.exit(1)
            
        # Set up scrapybara and open just the stream
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            stream_url = loop.run_until_complete(setup_scrapybara())
            if stream_url:
                logger.info(f"Opening Scrapybara stream in browser: {stream_url}")
                webbrowser.open(stream_url)
                
                # Keep main thread alive
                try:
                    while True:
                        import time
                        time.sleep(1)
                except KeyboardInterrupt:
                    logger.info("Stream viewer stopped by user")
            else:
                logger.error("Failed to get Scrapybara stream URL")
                sys.exit(1)
        finally:
            loop.close()
        return
    
    logger.info("Launching Solana Trading Dashboard...")
    launch_dashboard(
        debug=args.debug, 
        port=args.port,
        use_scrapybara=args.scrapybara,
        browser_only=args.browser_only,
        fullscreen=args.fullscreen
    )


if __name__ == "__main__":
    main()
