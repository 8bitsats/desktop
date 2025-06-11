#!/usr/bin/env python3
"""
Solana Trading Desktop Launcher Script
Integrates E2B Desktop with Scrapybara and launches the trading dashboard UI
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
logger = logging.getLogger("solana_desktop_launcher")

# Load environment variables
load_dotenv()

# Import internal modules
try:
    from desktop_trading.config import TradingDesktopConfig
    from desktop_trading.integrations import setup_trading_environment, cleanup_environment
except ImportError:
    logger.error("Failed to import required modules. Make sure you're in the correct directory.")
    logger.error("Install required dependencies with: pip install -r requirements.txt")
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
    print(f"{solana_purple}{bold}                      TRADING DESKTOP ENVIRONMENT{reset_color}")
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
    
    return True


async def main():
    """Main entry point for the launcher script"""
    print_banner()
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Launch Solana Trading Desktop Environment")
    parser.add_argument("--scrapybara", action="store_true", help="Enable Scrapybara integration")
    parser.add_argument("--live-trading", action="store_true", help="Enable live trading (USE WITH CAUTION)")
    parser.add_argument("--max-position-size", type=float, default=0.1, help="Maximum position size in SOL")
    args = parser.parse_args()
    
    if not verify_environment():
        logger.error("Environment verification failed. Please fix the issues and try again.")
        return
    
    # Configure trading desktop
    config = TradingDesktopConfig()
    
    # Update config from command-line arguments
    config.trading.enabled = args.live_trading
    config.trading.max_position_size = args.max_position_size
    
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
    
    try:
        logger.info("Setting up trading environment...")
        environment = await setup_trading_environment(config, use_scrapybara=args.scrapybara)
        desktop_manager = environment["desktop_manager"]
        
        # Log success and provide stream URL if available
        logger.info("Trading desktop launched successfully!")
        if environment.get("stream_url"):
            logger.info(f"Stream URL: {environment['stream_url']}")
        
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
        if 'environment' in locals():
            await cleanup_environment(environment)


if __name__ == "__main__":
    asyncio.run(main())
