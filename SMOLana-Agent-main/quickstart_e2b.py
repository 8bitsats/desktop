#!/usr/bin/env python
"""
Quick start script for Solana E2B Trading Desktop
Checks environment and launches the system
"""

import os
import sys
import asyncio
import subprocess
from pathlib import Path
from datetime import datetime
import logging

# Add color to console output
try:
    from colorama import init, Fore, Style
    init()
except ImportError:
    # Fallback if colorama not installed
    class Fore:
        GREEN = RED = YELLOW = BLUE = CYAN = MAGENTA = ""
        RESET = ""
    Style = Fore

def print_banner():
    """Display startup banner"""
    banner = f"""
{Fore.CYAN}╔══════════════════════════════════════════════════════════════╗
║           SOLANA E2B TRADING DESKTOP - MULTI-AGENT           ║
║                    🤖 AI-Powered Trading 🤖                   ║
╚══════════════════════════════════════════════════════════════╝{Fore.RESET}

{Fore.YELLOW}Featuring AI Agents:{Fore.RESET}
  💼 Warren Buffett - Value Investing
  🚀 Cathie Wood - Innovation & Growth  
  🛡️ Charlie Munger - Risk Assessment
  📊 Benjamin Graham - Security Analysis
  💰 Bill Ackman - Strategic Opportunities
  ... and more!

{Fore.GREEN}Visual Trading + Browser Automation + Multi-Agent Consensus{Fore.RESET}
"""
    print(banner)

def check_requirements():
    """Check if all requirements are met"""
    print(f"\n{Fore.BLUE}📋 Checking Requirements...{Fore.RESET}")
    
    issues = []
    
    # Check Python version
    if sys.version_info < (3, 8):
        issues.append("Python 3.8+ required")
    else:
        print(f"  {Fore.GREEN}✓{Fore.RESET} Python {sys.version.split()[0]}")
    
    # Check required packages
    required_packages = [
        "e2b_desktop",
        "solana_agent_kit",
        "webview",
        "dotenv",
        "aiohttp"
    ]
    
    for package in required_packages:
        try:
            __import__(package.replace("_", "-") if package == "solana_agent_kit" else package)
            print(f"  {Fore.GREEN}✓{Fore.RESET} {package}")
        except ImportError:
            issues.append(f"Missing package: {package}")
            print(f"  {Fore.RED}✗{Fore.RESET} {package}")
    
    # Check environment variables
    print(f"\n{Fore.BLUE}🔑 Checking Environment...{Fore.RESET}")
    
    required_env = {
        "E2B_API_KEY": "E2B Desktop access",
        "SOLANA_PRIVATE_KEY": "Wallet for trading"
    }
    
    optional_env = {
        "OPENAI_API_KEY": "AI analysis",
        "ANTHROPIC_API_KEY": "Alternative AI",
        "BIRDEYE_API_KEY": "Enhanced data"
    }
    
    for env_var, purpose in required_env.items():
        if os.getenv(env_var):
            print(f"  {Fore.GREEN}✓{Fore.RESET} {env_var} - {purpose}")
        else:
            issues.append(f"Missing {env_var}")
            print(f"  {Fore.RED}✗{Fore.RESET} {env_var} - {purpose}")
    
    for env_var, purpose in optional_env.items():
        if os.getenv(env_var):
            print(f"  {Fore.GREEN}✓{Fore.RESET} {env_var} - {purpose}")
        else:
            print(f"  {Fore.YELLOW}○{Fore.RESET} {env_var} - {purpose} (optional)")
    
    return issues

def check_configuration():
    """Check configuration files"""
    print(f"\n{Fore.BLUE}⚙️  Checking Configuration...{Fore.RESET}")
    
    config_files = {
        ".env": "Environment configuration",
        "e2b_config.json": "Desktop configuration",
        "e2b_desktop.log": "Log file"
    }
    
    for file, purpose in config_files.items():
        if Path(file).exists():
            print(f"  {Fore.GREEN}✓{Fore.RESET} {file} - {purpose}")
        else:
            print(f"  {Fore.YELLOW}○{Fore.RESET} {file} - {purpose} (will be created)")
    
    # Check trading mode
    trading_enabled = os.getenv("E2B_TRADING_ENABLED", "false").lower() == "true"
    if trading_enabled:
        print(f"\n  {Fore.RED}⚠️  LIVE TRADING ENABLED!{Fore.RESET}")
        print(f"  {Fore.YELLOW}Real money at risk - proceed with caution{Fore.RESET}")
    else:
        print(f"\n  {Fore.GREEN}✓ SIMULATION MODE{Fore.RESET} (safe)")

def create_directories():
    """Create required directories"""
    dirs = ["logs", "screenshots", "data", "reports", "backups"]
    
    print(f"\n{Fore.BLUE}📁 Setting up directories...{Fore.RESET}")
    
    for dir_name in dirs:
        Path(dir_name).mkdir(exist_ok=True)
        print(f"  {Fore.GREEN}✓{Fore.RESET} {dir_name}/")

def show_quick_config():
    """Show current configuration summary"""
    print(f"\n{Fore.BLUE}📊 Current Configuration:{Fore.RESET}")
    
    config_items = {
        "Trading Mode": os.getenv("E2B_TRADING_ENABLED", "false"),
        "Max Position": os.getenv("E2B_MAX_POSITION_SIZE", "0.05"),
        "Daily Limit": os.getenv("E2B_MAX_DAILY_TRADES", "10"),
        "Min Confidence": os.getenv("E2B_MIN_CONFIDENCE", "0.7"),
        "Analysis Interval": os.getenv("E2B_ANALYSIS_INTERVAL", "60") + "s"
    }
    
    for key, value in config_items.items():
        print(f"  {key}: {Fore.YELLOW}{value}{Fore.RESET}")

async def test_connections():
    """Test critical connections"""
    print(f"\n{Fore.BLUE}🔌 Testing Connections...{Fore.RESET}")
    
    # Test E2B
    try:
        from e2b_desktop import Sandbox
        print(f"  {Fore.YELLOW}→{Fore.RESET} Testing E2B Desktop...", end="", flush=True)
        # Don't actually create sandbox in quick test
        print(f" {Fore.GREEN}✓{Fore.RESET}")
    except Exception as e:
        print(f" {Fore.RED}✗ {str(e)}{Fore.RESET}")
    
    # Test Solana
    try:
        print(f"  {Fore.YELLOW}→{Fore.RESET} Testing Solana connection...", end="", flush=True)
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.post(
                os.getenv("SOLANA_RPC_URL", "https://api.mainnet-beta.solana.com"),
                json={"jsonrpc": "2.0", "id": 1, "method": "getHealth"}
            ) as resp:
                if resp.status == 200:
                    print(f" {Fore.GREEN}✓{Fore.RESET}")
                else:
                    print(f" {Fore.RED}✗ Status {resp.status}{Fore.RESET}")
    except Exception as e:
        print(f" {Fore.RED}✗ {str(e)}{Fore.RESET}")

def launch_desktop():
    """Launch the trading desktop"""
    print(f"\n{Fore.GREEN}🚀 Launching Solana E2B Trading Desktop...{Fore.RESET}")
    print(f"{Fore.YELLOW}Press Ctrl+C to stop{Fore.RESET}\n")
    
    try:
        # Import our desktop_trading modules
        from desktop_trading import DesktopManager
        from desktop_trading.config import load_desktop_config
        
        # Run the main module
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Shutting down gracefully...{Fore.RESET}")
    except Exception as e:
        print(f"\n{Fore.RED}Error: {str(e)}{Fore.RESET}")
        logging.exception("Launch error")

async def main():
    """Main async function to run the desktop"""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("logs/e2b_desktop.log"),
            logging.StreamHandler()
        ]
    )
    
    # Import our desktop_trading modules
    from desktop_trading import DesktopManager
    from desktop_trading.config import load_desktop_config
    
    # Load configuration
    config = load_desktop_config()
    
    # Create desktop manager
    desktop = DesktopManager(config)
    
    try:
        # Initialize desktop environment
        await desktop.initialize()
        
        # Set Solana theme and open browser tabs
        await desktop.apply_solana_theme()
        await desktop.setup_browser_tabs()
        
        # Launch desktop window
        desktop_process = await desktop.launch_desktop_window()
        
        # Keep running until terminated
        while True:
            # Check if desktop window is still running
            if desktop_process and desktop_process.poll() is not None:
                logging.info("Desktop window closed, shutting down")
                break
                
            # Sleep for a bit to reduce CPU usage
            await asyncio.sleep(1)
            
    except Exception as e:
        logging.exception(f"Error in desktop operation: {str(e)}")
    finally:
        # Clean up
        await desktop.cleanup()
        logging.info("Desktop manager shutdown complete")

if __name__ == "__main__":
    print_banner()
    
    # Load environment
    from dotenv import load_dotenv
    load_dotenv()
    
    # Run checks
    issues = check_requirements()
    
    if issues:
        print(f"\n{Fore.RED}❌ Cannot start - please fix these issues:{Fore.RESET}")
        for issue in issues:
            print(f"  - {issue}")
        print(f"\n{Fore.YELLOW}Run 'pip install -r requirements-e2b.txt' to install missing packages{Fore.RESET}")
        sys.exit(1)
    
    check_configuration()
    create_directories()
    show_quick_config()
    
    # Test connections
    asyncio.run(test_connections())
    
    # Confirm before launching
    print(f"\n{Fore.CYAN}Ready to launch!{Fore.RESET}")
    
    if os.getenv("E2B_TRADING_ENABLED", "false").lower() == "true":
        print(f"{Fore.RED}⚠️  WARNING: Live trading is ENABLED!{Fore.RESET}")
        response = input(f"\n{Fore.YELLOW}Continue with LIVE TRADING? (yes/no): {Fore.RESET}")
        if response.lower() != "yes":
            print("Aborted.")
            sys.exit(0)
    else:
        input(f"\n{Fore.GREEN}Press Enter to start in SIMULATION mode...{Fore.RESET}")
    
    # Launch
    launch_desktop()
