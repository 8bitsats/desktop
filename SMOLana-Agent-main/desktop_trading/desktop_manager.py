"""
Desktop Manager for Solana Trading Desktop
Handles the E2B desktop sandbox environment and UI
"""

import asyncio
import logging
import os
import threading
import time
from typing import Dict, Optional, Any, Tuple
from multiprocessing import Process, Queue
import json
import webview

from e2b_desktop import Sandbox
from .config import TradingDesktopConfig, DesktopTheme

logger = logging.getLogger(__name__)

# SVG templates for desktop backgrounds
SOLANA_DARK_BACKGROUND = """
<svg width="1920" height="1080" xmlns="http://www.w3.org/2000/svg">
    <defs>
        <linearGradient id="solanaGradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stop-color="#121212" />
            <stop offset="50%" stop-color="#232323" />
            <stop offset="100%" stop-color="#121212" />
        </linearGradient>
        <filter id="noise" x="0%" y="0%" width="100%" height="100%">
            <feTurbulence type="fractalNoise" baseFrequency="0.01" numOctaves="3" result="noise" />
            <feColorMatrix type="matrix" values="1 0 0 0 0 0 1 0 0 0 0 0 1 0 0 0 0 0 0.05 0" />
        </filter>
    </defs>
    <rect width="1920" height="1080" fill="url(#solanaGradient)" />
    <rect width="1920" height="1080" filter="url(#noise)" opacity="1" />
    
    <!-- Solana-inspired patterns with purple (#9945FF) -->
    <circle cx="960" cy="540" r="300" fill="none" stroke="#9945FF" stroke-width="2" opacity="0.1" />
    <circle cx="960" cy="540" r="450" fill="none" stroke="#9945FF" stroke-width="2" opacity="0.07" />
    <circle cx="960" cy="540" r="600" fill="none" stroke="#9945FF" stroke-width="2" opacity="0.04" />
    
    <!-- Green accents with Solana green (#14F195) -->
    <circle cx="300" cy="200" r="100" fill="#14F195" opacity="0.05" />
    <circle cx="1600" cy="800" r="150" fill="#9945FF" opacity="0.05" />
    
    <!-- Grid lines -->
    <g opacity="0.05">
        <line x1="0" y1="270" x2="1920" y2="270" stroke="#FFFFFF" stroke-width="1" />
        <line x1="0" y1="540" x2="1920" y2="540" stroke="#FFFFFF" stroke-width="1" />
        <line x1="0" y1="810" x2="1920" y2="810" stroke="#FFFFFF" stroke-width="1" />
        <line x1="480" y1="0" x2="480" y2="1080" stroke="#FFFFFF" stroke-width="1" />
        <line x1="960" y1="0" x2="960" y2="1080" stroke="#FFFFFF" stroke-width="1" />
        <line x1="1440" y1="0" x2="1440" y2="1080" stroke="#FFFFFF" stroke-width="1" />
    </g>
    
    <!-- Solana logo hint -->
    <g transform="translate(1750, 1000) scale(0.5)">
        <path d="M30,10 L10,50 L30,90 L160,90 L180,50 L160,10 Z" fill="none" stroke="#9945FF" stroke-width="3" opacity="0.2" />
    </g>
</svg>
"""

SOLANA_LIGHT_BACKGROUND = """
<svg width="1920" height="1080" xmlns="http://www.w3.org/2000/svg">
    <defs>
        <linearGradient id="solanaGradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stop-color="#F8F8F8" />
            <stop offset="50%" stop-color="#FFFFFF" />
            <stop offset="100%" stop-color="#F8F8F8" />
        </linearGradient>
        <filter id="noise" x="0%" y="0%" width="100%" height="100%">
            <feTurbulence type="fractalNoise" baseFrequency="0.01" numOctaves="3" result="noise" />
            <feColorMatrix type="matrix" values="1 0 0 0 0 0 1 0 0 0 0 0 1 0 0 0 0 0 0.03 0" />
        </filter>
    </defs>
    <rect width="1920" height="1080" fill="url(#solanaGradient)" />
    <rect width="1920" height="1080" filter="url(#noise)" opacity="1" />
    
    <!-- Solana-inspired patterns with Solana purple (#9945FF) -->
    <circle cx="960" cy="540" r="300" fill="none" stroke="#9945FF" stroke-width="2" opacity="0.1" />
    <circle cx="960" cy="540" r="450" fill="none" stroke="#9945FF" stroke-width="2" opacity="0.07" />
    <circle cx="960" cy="540" r="600" fill="none" stroke="#9945FF" stroke-width="2" opacity="0.04" />
    
    <!-- Green accents with Solana green (#14F195) -->
    <circle cx="300" cy="200" r="100" fill="#14F195" opacity="0.05" />
    <circle cx="1600" cy="800" r="150" fill="#9945FF" opacity="0.05" />
    
    <!-- Grid lines -->
    <g opacity="0.05">
        <line x1="0" y1="270" x2="1920" y2="270" stroke="#333333" stroke-width="1" />
        <line x1="0" y1="540" x2="1920" y2="540" stroke="#333333" stroke-width="1" />
        <line x1="0" y1="810" x2="1920" y2="810" stroke="#333333" stroke-width="1" />
        <line x1="480" y1="0" x2="480" y2="1080" stroke="#333333" stroke-width="1" />
        <line x1="960" y1="0" x2="960" y2="1080" stroke="#333333" stroke-width="1" />
        <line x1="1440" y1="0" x2="1440" y2="1080" stroke="#333333" stroke-width="1" />
    </g>
    
    <!-- Solana logo hint -->
    <g transform="translate(1750, 1000) scale(0.5)">
        <path d="M30,10 L10,50 L30,90 L160,90 L180,50 L160,10 Z" fill="none" stroke="#9945FF" stroke-width="3" opacity="0.2" />
    </g>
</svg>
"""


class DesktopManager:
    """
    Manages the E2B desktop sandbox environment for Solana trading
    """
    
    def __init__(self, config: TradingDesktopConfig):
        self.config = config
        self.sandbox: Optional[Sandbox] = None
        self.stream_url: Optional[str] = None
        self.width: int = config.desktop.width
        self.height: int = config.desktop.height
        self.desktop_process = None
        self.command_queue = None
        self.browser_tabs: Dict[str, str] = {}
        self.clipboard_data = {}
        
    async def initialize(self) -> bool:
        """Initialize the desktop sandbox"""
        try:
            logger.info("Initializing E2B desktop sandbox...")
            
            # Create and configure sandbox
            self.sandbox = Sandbox()
            
            # Get screen size
            self.width, self.height = self.sandbox.get_screen_size()
            logger.info(f"Desktop size: {self.width}x{self.height}")
            
            # Start desktop stream
            self.sandbox.stream.start(require_auth=self.config.desktop.auth_required)
            auth_key = self.sandbox.stream.get_auth_key()
            self.stream_url = self.sandbox.stream.get_url(auth_key=auth_key)
            logger.info(f"Stream URL: {self.stream_url}")
            
            # Apply desktop theme
            await self.apply_theme()
            
            return True
            
        except Exception as e:
            logger.error(f"Desktop initialization error: {e}")
            return False
    
    async def apply_theme(self):
        """Apply the selected theme to the desktop environment"""
        try:
            # Select background based on theme
            if self.config.desktop.theme == DesktopTheme.SOLANA_DARK:
                background = SOLANA_DARK_BACKGROUND
            elif self.config.desktop.theme == DesktopTheme.SOLANA_LIGHT:
                background = SOLANA_LIGHT_BACKGROUND
            else:
                # Use custom background URL if provided
                if self.config.desktop.background_url:
                    logger.info(f"Using custom background from {self.config.desktop.background_url}")
                    return
                else:
                    # Default to dark theme
                    background = SOLANA_DARK_BACKGROUND
            
            # Create and apply SVG background
            with open("/tmp/solana_background.svg", "w") as f:
                f.write(background)
            
            # Set as desktop background (implementation depends on sandbox OS)
            try:
                # Try GNOME desktop first (common in Linux sandboxes)
                self.sandbox.run([
                    "gsettings", "set", "org.gnome.desktop.background", 
                    "picture-uri", "file:///tmp/solana_background.svg"
                ])
            except Exception:
                try:
                    # Try setting wallpaper in a more universal way with feh
                    self.sandbox.run(["feh", "--bg-scale", "/tmp/solana_background.svg"])
                except Exception as e:
                    logger.warning(f"Could not set wallpaper: {e}")
            
            logger.info(f"Applied {self.config.desktop.theme.value} theme")
            
        except Exception as e:
            logger.error(f"Error applying theme: {e}")
    
    async def setup_browser(self) -> bool:
        """Set up browser with Solana trading tabs"""
        try:
            # Launch Chrome
            self.sandbox.launch('google-chrome')
            await asyncio.sleep(3)
            
            # Define trading websites
            websites = {
                "solscan": "https://solscan.io",
                "jupiter": "https://jup.ag",
                "birdeye": "https://birdeye.so",
                "dexscreener": "https://dexscreener.com/solana",
                "pump_fun": "https://pump.fun"
            }
            
            # Open tabs
            for idx, (name, url) in enumerate(websites.items()):
                if idx > 0:
                    self.sandbox.press(['ctrl', 't'])
                    await asyncio.sleep(0.5)
                
                self.sandbox.press(['ctrl', 'l'])
                self.sandbox.write(url)
                self.sandbox.press('enter')
                await asyncio.sleep(2)
                
                self.browser_tabs[name] = url
                logger.info(f"Opened tab: {name} - {url}")
            
            # Go back to first tab
            self.sandbox.press(['ctrl', '1'])
            
            return True
            
        except Exception as e:
            logger.error(f"Browser setup error: {e}")
            return False
    
    def switch_to_tab(self, tab_name: str):
        """Switch to a specific browser tab"""
        if tab_name in self.browser_tabs:
            tab_index = list(self.browser_tabs.keys()).index(tab_name) + 1
            self.sandbox.press(['ctrl', str(tab_index)])
            logger.info(f"Switched to tab: {tab_name}")
            return True
        else:
            logger.warning(f"Tab {tab_name} not found")
            return False
    
    def set_clipboard_data(self, key: str, value: Any):
        """Store data in virtual clipboard for sharing with UI"""
        self.clipboard_data[key] = value
        
        # Also set to actual clipboard as JSON for desktop interaction
        try:
            clipboard_json = json.dumps({key: value})
            self.sandbox.clipboard.write(clipboard_json)
            return True
        except Exception as e:
            logger.error(f"Error setting clipboard: {e}")
            return False
    
    def get_clipboard_data(self, key: str) -> Any:
        """Get data from virtual clipboard"""
        return self.clipboard_data.get(key)
    
    def start_desktop_window(self) -> Queue:
        """Start the desktop window with WebView in a separate process"""
        command_queue = Queue()
        
        def create_window(stream_url, width, height, command_queue):
            """Create and run the desktop window"""
            def check_queue():
                while True:
                    if not command_queue.empty():
                        command = command_queue.get()
                        if command == 'close':
                            window.destroy()
                            break
                    time.sleep(1)
            
            # Create WebView window with Solana trading desktop title
            window = webview.create_window(
                "Solana Trading Desktop",
                stream_url,
                width=width,
                height=height + 30  # Account for window frame
            )
            
            t = threading.Thread(target=check_queue)
            t.daemon = True
            t.start()
            
            webview.start()
        
        # Start window in separate process
        self.desktop_process = Process(
            target=create_window,
            args=(self.stream_url, self.width, self.height, command_queue)
        )
        self.desktop_process.start()
        self.command_queue = command_queue
        
        logger.info("Desktop window started")
        return command_queue
    
    async def cleanup(self):
        """Clean up resources"""
        logger.info("Cleaning up desktop resources...")
        
        if self.sandbox:
            try:
                self.sandbox.stream.stop()
                self.sandbox.kill()
            except Exception as e:
                logger.error(f"Error cleaning up sandbox: {e}")
        
        if self.desktop_process and self.desktop_process.is_alive():
            try:
                if self.command_queue:
                    self.command_queue.put('close')
                
                # Wait briefly for graceful shutdown
                await asyncio.sleep(1)
                
                # Force terminate if still running
                if self.desktop_process.is_alive():
                    self.desktop_process.terminate()
                    self.desktop_process.join(timeout=2)
            except Exception as e:
                logger.error(f"Error terminating desktop process: {e}")
        
        logger.info("Desktop cleanup complete")
