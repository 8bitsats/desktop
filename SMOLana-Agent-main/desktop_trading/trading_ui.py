"""
Trading UI module for Scrapybara integration
Provides UI components and utilities for trading dashboard
"""

import os
import logging
from typing import Dict, List, Optional, Any

# Configure logging
logger = logging.getLogger(__name__)

# Singleton instance
_ui_instance = None

def get_ui() -> 'TradingUI':
    """Get or create the TradingUI singleton instance
    
    Returns:
        TradingUI instance
    """
    global _ui_instance
    if _ui_instance is None:
        _ui_instance = TradingUI()
    return _ui_instance

class TradingUI:
    """Manages UI components for trading dashboard"""
    
    def __init__(self):
        """Initialize trading UI components"""
        logger.info("Initializing Trading UI components")
        self.components = {}
        
    def get_stream_container_html(self, stream_url: Optional[str] = None) -> str:
        """Generate HTML for stream container
        
        Args:
            stream_url: URL for Scrapybara stream
            
        Returns:
            HTML string for stream container
        """
        if not stream_url:
            return """
            <div id="no-stream" style="margin-top: 20px; text-align: center; padding: 20px; border: 1px dashed #ccc; border-radius: 10px;">
                <h3>No Live Stream Available</h3>
                <p>Start Scrapybara integration to view live trading activity.</p>
                <button id="start-scrapybara" class="solana-button">Start Scrapybara</button>
            </div>
            """
        
        # Return stream container with active URL
        return f"""
        <div id="stream-viewer" class="dashboard-panel" style="margin-top: 20px; border: 1px solid #9945FF; border-radius: 10px; overflow: hidden;">
            <h2 style="background-color: #9945FF; color: white; margin: 0; padding: 10px; display: flex; justify-content: space-between;">
                <span>Live Trading Agent View</span>
                <span class="stream-status">🟢 Connected</span>
            </h2>
            <iframe src="{stream_url}" style="width: 100%; height: 500px; border: none;"></iframe>
        </div>
        """
    
    def get_agent_control_panel_html(self) -> str:
        """Generate HTML for agent control panel
        
        Returns:
            HTML string for agent control panel
        """
        return """
        <div id="agent-control-panel" class="dashboard-panel" style="margin-top: 20px; border: 1px solid #14F195; border-radius: 10px; overflow: hidden;">
            <h2 style="background-color: #14F195; color: white; margin: 0; padding: 10px;">Agent Control</h2>
            <div style="padding: 15px;">
                <div style="display: flex; gap: 10px; margin-bottom: 15px;">
                    <button id="agent-start" class="solana-button">Start Agent</button>
                    <button id="agent-pause" class="solana-button">Pause</button>
                    <button id="agent-stop" class="solana-button">Stop</button>
                </div>
                <div>
                    <textarea id="agent-command" placeholder="Enter command for agent..." rows="3" style="width: 100%; padding: 10px; border-radius: 5px; border: 1px solid #ccc; margin-bottom: 10px;"></textarea>
                    <button id="agent-send-command" class="solana-button primary">Send Command</button>
                </div>
                <div id="agent-status" style="margin-top: 15px; padding: 10px; background-color: #f5f5f5; border-radius: 5px;">
                    Status: <span id="agent-status-value">Idle</span>
                </div>
            </div>
        </div>
        """
        
    def get_trade_history_html(self) -> str:
        """Generate HTML for trade history panel
        
        Returns:
            HTML string for trade history panel
        """
        return """
        <div id="trade-history" class="dashboard-panel" style="margin-top: 20px; border: 1px solid #E42575; border-radius: 10px; overflow: hidden;">
            <h2 style="background-color: #E42575; color: white; margin: 0; padding: 10px;">Trading History</h2>
            <div style="padding: 15px; max-height: 300px; overflow-y: auto;">
                <table style="width: 100%; border-collapse: collapse;">
                    <thead>
                        <tr>
                            <th style="text-align: left; padding: 8px; border-bottom: 1px solid #ddd;">Time</th>
                            <th style="text-align: left; padding: 8px; border-bottom: 1px solid #ddd;">Action</th>
                            <th style="text-align: left; padding: 8px; border-bottom: 1px solid #ddd;">Token</th>
                            <th style="text-align: right; padding: 8px; border-bottom: 1px solid #ddd;">Amount</th>
                            <th style="text-align: right; padding: 8px; border-bottom: 1px solid #ddd;">Status</th>
                        </tr>
                    </thead>
                    <tbody id="trade-history-body">
                        <tr>
                            <td colspan="5" style="text-align: center; padding: 20px;">No trades yet</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
        """
