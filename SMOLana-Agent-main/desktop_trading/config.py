"""
Configuration for Solana Trading Desktop
"""

import os
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from enum import Enum

# Solana color palette
SOLANA_PURPLE = "#9945FF"
SOLANA_GREEN = "#14F195"
SOLANA_DARK = "#121212"
SOLANA_LIGHT = "#FFFFFF"


class DesktopTheme(Enum):
    """Available desktop themes"""
    SOLANA_DARK = "solana_dark"
    SOLANA_LIGHT = "solana_light"
    CUSTOM = "custom"


@dataclass
class DesktopConfig:
    """Desktop environment configuration"""
    theme: DesktopTheme = DesktopTheme.SOLANA_DARK
    width: int = 1920
    height: int = 1080
    background_url: Optional[str] = None
    custom_css: Optional[str] = None
    auth_required: bool = True
    auto_start_browser: bool = True


@dataclass
class TradingConfig:
    """Trading functionality configuration"""
    trading_enabled: bool = False
    max_trade_amount: float = 0.05
    max_daily_trades: int = 5
    stop_loss_percentage: float = 0.1
    take_profit_percentage: float = 0.25
    favorite_tokens: List[str] = field(default_factory=lambda: ["SOL", "JUP", "RAY", "BONK"])


@dataclass
class AgentConfig:
    """Agent system configuration"""
    multi_agent_enabled: bool = True
    consensus_threshold: float = 0.6
    ai_model: str = "gpt-4o"
    agent_count: int = 3
    agent_personalities: List[str] = field(default_factory=lambda: [
        "value_investor",
        "innovation_analyst", 
        "risk_assessor"
    ])


@dataclass
class TradingDesktopConfig:
    """Main configuration for Solana Trading Desktop"""
    desktop: DesktopConfig = field(default_factory=DesktopConfig)
    trading: TradingConfig = field(default_factory=TradingConfig)
    agent: AgentConfig = field(default_factory=AgentConfig)
    rpc_url: str = "https://api.mainnet-beta.solana.com"
    
    @classmethod
    def from_env(cls) -> 'TradingDesktopConfig':
        """Load configuration from environment variables"""
        config = cls()
        
        # Trading settings
        config.trading.trading_enabled = os.getenv("TRADING_ENABLED", "false").lower() == "true"
        if max_amount := os.getenv("MAX_TRADE_AMOUNT"):
            config.trading.max_trade_amount = float(max_amount)
        if max_trades := os.getenv("MAX_DAILY_TRADES"):
            config.trading.max_daily_trades = int(max_trades)
            
        # RPC URL
        if rpc_url := os.getenv("SOLANA_RPC_URL"):
            config.rpc_url = rpc_url
            
        # Agent settings
        if os.getenv("MULTI_AGENT_ENABLED", "true").lower() != "true":
            config.agent.multi_agent_enabled = False
            
        # Desktop settings
        if os.getenv("DESKTOP_THEME") == "light":
            config.desktop.theme = DesktopTheme.SOLANA_LIGHT
        
        return config
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary"""
        return {
            "desktop": {
                "theme": self.desktop.theme.value,
                "width": self.desktop.width,
                "height": self.desktop.height,
                "auth_required": self.desktop.auth_required,
                "auto_start_browser": self.desktop.auto_start_browser
            },
            "trading": {
                "trading_enabled": self.trading.trading_enabled,
                "max_trade_amount": self.trading.max_trade_amount,
                "max_daily_trades": self.trading.max_daily_trades,
                "stop_loss_percentage": self.trading.stop_loss_percentage,
                "take_profit_percentage": self.trading.take_profit_percentage,
                "favorite_tokens": self.trading.favorite_tokens
            },
            "agent": {
                "multi_agent_enabled": self.agent.multi_agent_enabled,
                "consensus_threshold": self.agent.consensus_threshold,
                "ai_model": self.agent.ai_model,
                "agent_count": self.agent.agent_count,
                "agent_personalities": self.agent.agent_personalities
            },
            "rpc_url": self.rpc_url
        }
