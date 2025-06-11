#!/usr/bin/env python3
"""
Solana Trading Desktop Unified Launcher
Integrates all components: E2B Desktop, Scrapybara, Model Replay, Gradio UI, and Evaluation tools
"""

import os
import sys
import asyncio
import logging
import argparse
from pathlib import Path
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s [%(name)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("solana_unified_launcher")

# Load environment variables
load_dotenv()

# Add the project root to Python path to allow imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Import internal modules
try:
    from desktop_trading.integrations import ScrapybaraIntegration, DashboardViewer, setup_trading_environment, cleanup_environment
    
    # Create config class for now
    class TradingDesktopConfig:
        def __init__(self):
            self.trading = {
                'enabled': False,
                'max_position_size': 0.1
            }
            self.integrations = {}
            self.gradio = {}
            self.agent = {
                'system_prompt': 'You are a Solana trading assistant.',
                'name': 'SolanaTrader'
            }
            
    # Simplified unified manager function
    async def run_unified_desktop(config=None, **kwargs):
        logger.info("Setting up simplified trading environment")
        env_handles = await setup_trading_environment(
            config=config,
            use_scrapybara=kwargs.get('enable_scrapybara', False)
        )
        return env_handles
        
except ImportError as e:
    logger.error(f"Failed to import required modules: {e}")
    logger.error("Make sure you're in the correct directory and have installed dependencies.")
    sys.exit(1)


def print_banner():
    """Print Solana Trading Desktop banner"""
    solana_purple = "\033[95m"
    solana_green = "\033[92m"
    reset_color = "\033[0m"
    bold = "\033[1m"
    
    print(f"\n{solana_purple}{bold}{'=' * 70}{reset_color}")
    print(f"{solana_purple}{bold}  ____   ___  _        _    _   _    _    {reset_color}{solana_green}{bold}_____  ____      _    ____ ___ _   _  ____ {reset_color}")
    print(f"{solana_purple}{bold} / ___| / _ \| |      / \  | \ | |  / \  {reset_color}{solana_green}{bold}|_   _|/ ___|    / \  |  _ \_ _| \ | |/ ___|{reset_color}")
    print(f"{solana_purple}{bold} \___ \| | | | |     / _ \ |  \| | / _ \   {reset_color}{solana_green}{bold} | |  \___ \   / _ \ | | | | ||  \| | |  _ {reset_color}")
    print(f"{solana_purple}{bold}  ___) | |_| | |___ / ___ \| |\  |/ ___ \  {reset_color}{solana_green}{bold} | |   ___) | / ___ \| |_| | || |\  | |_| |{reset_color}")
    print(f"{solana_purple}{bold} |____/ \___/|_____/_/   \_\_| \_/_/   \_\ {reset_color}{solana_green}{bold} |_|  |____/ /_/   \_\____/___|_| \_|\____|{reset_color}")
    print(f"{solana_purple}{bold}{'=' * 70}{reset_color}")
    print(f"{solana_purple}{bold}               UNIFIED TRADING DESKTOP ENVIRONMENT{reset_color}")
    print(f"{solana_purple}{bold}{'=' * 70}{reset_color}\n")


def verify_environment():
    """Verify environment variables and required dependencies"""
    # Check for E2B API key
    if not os.environ.get("E2B_API_KEY"):
        logger.error("E2B_API_KEY environment variable not found")
        logger.error("Get your API key from https://e2b.dev and add it to your .env file")
        return False
    
    # Check for Solana private key
    if not os.environ.get("SOLANA_PRIVATE_KEY"):
        logger.warning("SOLANA_PRIVATE_KEY environment variable not found")
        logger.warning("Trading functionality will be limited to simulation mode only")
    
    # Check for optional Scrapybara API key
    if not os.environ.get("SCRAPY_API_KEY"):
        logger.warning("SCRAPY_API_KEY environment variable not found")
        logger.warning("Scrapybara integration will be disabled")
    
    try:
        import e2b_desktop
        logger.info("✓ E2B Desktop SDK found")
    except ImportError:
        logger.error("E2B Desktop SDK not found. Install it with: pip install e2b_desktop")
        return False
    
    try:
        import smolagents
        logger.info("✓ SmolaAgents SDK found")
    except ImportError:
        logger.warning("SmolaAgents SDK not found. Agent functionality will be limited.")
    
    try:
        import gradio
        logger.info("✓ Gradio UI library found")
    except ImportError:
        logger.warning("Gradio UI library not found. UI features will be limited.")
    
    return True


async def main():
    """Main entry point for the unified launcher script"""
    print_banner()
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Launch Solana Unified Trading Desktop Environment")
    parser.add_argument("--scrapybara", action="store_true", help="Enable Scrapybara integration")
    parser.add_argument("--live-trading", action="store_true", help="Enable live trading (USE WITH CAUTION)")
    parser.add_argument("--max-position-size", type=float, default=0.1, help="Maximum position size in SOL")
    parser.add_argument("--gradio-ui", action="store_true", help="Enable Gradio web UI")
    parser.add_argument("--model-replay", action="store_true", help="Use model replay for testing")
    parser.add_argument("--eval-server", action="store_true", help="Start evaluation server")
    parser.add_argument("--eval-port", type=int, default=5000, help="Evaluation server port")
    parser.add_argument("--replay-log", type=str, help="Path to model replay log folder")
    args = parser.parse_args()
    
    if not verify_environment():
        logger.error("Environment verification failed. Please fix the issues and try again.")
        return
    
    # Configure trading desktop
    config = TradingDesktopConfig()
    
    # Update config from command-line arguments
    config.trading.enabled = args.live_trading
    config.trading.max_position_size = args.max_position_size
    config.integrations = {
        "use_scrapybara": args.scrapybara
    }
    config.gradio = {
        "server_port": 7860,
        "server_name": "127.0.0.1",
        "share": False
    }
    
    # Safety check for live trading
    if config.trading.enabled:
        logger.warning("⚠️  LIVE TRADING MODE ENABLED - REAL FUNDS AT RISK ⚠️")
        confirmation = input("Type 'CONFIRM' to enable live trading or anything else to use simulation mode: ")
        if confirmation.strip().upper() != "CONFIRM":
            logger.info("Switching to simulation mode")
            config.trading.enabled = False
    
    # Log configuration
    logger.info(f"Trading enabled: {config.trading.enabled}")
    logger.info(f"Max position size: {config.trading.max_position_size} SOL")
    logger.info(f"Scrapybara integration: {args.scrapybara}")
    logger.info(f"Gradio UI: {args.gradio_ui}")
    logger.info(f"Model replay: {args.model_replay}")
    logger.info(f"Evaluation server: {args.eval_server}")
    
    try:
        logger.info("Setting up simplified trading environment...")
        env_handles = await run_unified_desktop(
            config=config,
            enable_scrapybara=args.scrapybara
        )
        
        # Log success
        logger.info("Trading desktop environment launched successfully!")
        
        # Keep the script running
        logger.info("Press Ctrl+C to exit")
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            logger.info("Shutting down...")
    except Exception as e:
        logger.error(f"Error during setup: {e}")
    finally:
        # Clean up resources
        if 'env_handles' in locals():
            await cleanup_environment(env_handles)


if __name__ == "__main__":
    asyncio.run(main())
