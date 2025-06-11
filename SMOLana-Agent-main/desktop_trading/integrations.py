"""
Integrations module for the Solana Trading Desktop Environment
Provides adapters for Scrapybara API and enhanced browser automation
"""

import os
import base64
import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
import json

# Internal imports
from .desktop_manager import DesktopManager
from .config import TradingDesktopConfig

# Optional imports for Scrapybara integration
try:
    from scrapybara import Scrapybara
    from scrapybara.tools import BashTool, ComputerTool, EditTool, BrowserTool
    from scrapybara.anthropic import Anthropic
    from scrapybara.openai import OpenAI
    from scrapybara.prompts import UBUNTU_SYSTEM_PROMPT, BROWSER_SYSTEM_PROMPT
    SCRAPYBARA_AVAILABLE = True
except ImportError:
    SCRAPYBARA_AVAILABLE = False

# Configure logging
logger = logging.getLogger(__name__)


class ScrapybaraIntegration:
    """Integration with Scrapybara API for remote browser and desktop automation"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize Scrapybara integration with API key

        Args:
            api_key: Scrapybara API key, defaults to SCRAPY_API_KEY environment variable
        
        Raises:
            ImportError: If Scrapybara package is not installed
            ValueError: If API key is not provided and not in environment
        """
        if not SCRAPYBARA_AVAILABLE:
            raise ImportError(
                "Scrapybara package is not installed. "
                "Please install it with: pip install scrapybara"
            )
            
        self.api_key = api_key or os.environ.get("SCRAPY_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Scrapybara API key not found. Please provide an API key or set SCRAPY_API_KEY env var."
            )
        
        # Initialize Scrapybara client
        self.client = Scrapybara(api_key=self.api_key)
        self.instance = None
        self.browser_cdp_url = None
        self.stream_url = None
        self.auth_state_id = None
        
        # Store imported modules for later use
        self.modules = {
            "Anthropic": Anthropic,
            "BashTool": BashTool,
            "ComputerTool": ComputerTool,
            "EditTool": EditTool,
            "BrowserTool": BrowserTool,
            "UBUNTU_SYSTEM_PROMPT": UBUNTU_SYSTEM_PROMPT,
            "BROWSER_SYSTEM_PROMPT": BROWSER_SYSTEM_PROMPT
        }
    
    async def start_instance(self, instance_type: str = "ubuntu", timeout_hours: int = 1) -> Dict:
        """Start a Scrapybara instance.
        
        Args:
            instance_type: Type of instance ("ubuntu", "browser", "windows")
            timeout_hours: Instance timeout in hours
            
        Returns:
            Dict with instance info
        """
        logger.info(f"Starting {instance_type} instance with {timeout_hours}hr timeout")
        
        if instance_type == "ubuntu":
            self.instance = self.client.start_ubuntu(timeout_hours=timeout_hours)
        elif instance_type == "browser":
            self.instance = self.client.start_browser(timeout_hours=timeout_hours)
        elif instance_type == "windows":
            self.instance = self.client.start_windows(timeout_hours=timeout_hours)
        else:
            raise ValueError(f"Unknown instance type: {instance_type}")
        
        # Get stream URL for viewer
        self.stream_url = self.instance.get_stream_url().stream_url
        
        return {
            "instance_id": self.instance.id,
            "instance_type": instance_type,
            "stream_url": self.stream_url
        }
    
    async def setup_browser(self, auth_state_id: Optional[str] = None) -> str:
        """Set up browser in Scrapybara instance

        Args:
            auth_state_id: Optional auth state ID to authenticate browser session
            
        Returns:
            CDP URL for browser connection
        """
        if not self.instance:
            raise ValueError("Instance not started. Call start_instance first.")
        
        # Apply authentication if provided
        if auth_state_id:
            logger.info(f"Applying auth state: {auth_state_id}")
            self.instance.authenticate(auth_state_id=auth_state_id)
            self.auth_state_id = auth_state_id
            
        # Start browser and get CDP URL
        self.browser_cdp_url = self.instance.browser.start().cdp_url
        logger.info(f"Browser started with CDP URL: {self.browser_cdp_url}")
        return self.browser_cdp_url
    
    async def take_screenshot(self) -> str:
        """Take screenshot of current instance

        Returns:
            Base64-encoded PNG image
        """
        if not self.instance:
            raise ValueError("Instance not started. Call start_instance first.")
        
        screenshot = self.instance.screenshot()
        return screenshot.base_64_image
    
    async def run_action(self, action_type: str, **kwargs) -> Dict:
        """Run an action on the Scrapybara instance

        Args:
            action_type: Type of action (bash, computer, browser, edit)
            **kwargs: Action-specific parameters

        Returns:
            Dict containing action result
        """
        if not self.instance:
            raise ValueError("Instance not started. Call start_instance first.")
        
        if action_type == "bash":
            command = kwargs.get("command")
            if not command:
                raise ValueError("Command required for bash action")
            result = self.instance.bash(command=command)
            return {"stdout": result.output, "stderr": result.error, "exit_code": 0 if not result.error else 1}
        
        elif action_type == "computer":
            computer_action = kwargs.get("action")
            if not computer_action:
                raise ValueError("Computer action required")
            
            if computer_action == "move_mouse":
                coordinates = kwargs.get("coordinates", [0, 0])
                self.instance.computer(action="move_mouse", coordinates=coordinates)
                return {"success": True, "action": "move_mouse", "coordinates": coordinates}
            
            elif computer_action == "click_mouse":
                button = kwargs.get("button", "left")
                self.instance.computer(action="click_mouse", button=button)
                return {"success": True, "action": "click_mouse", "button": button}
            
            elif computer_action == "type_text":
                text = kwargs.get("text", "")
                self.instance.computer(action="type_text", text=text)
                return {"success": True, "action": "type_text", "text": text}

            elif computer_action == "take_screenshot":
                screenshot = self.instance.screenshot()
                return {"success": True, "action": "screenshot", "image": screenshot.base64_image}
            
            else:
                raise ValueError(f"Unknown computer action: {computer_action}")
        
        elif action_type == "browser":
            # Ensure browser is started
            if not self.browser_cdp_url:
                await self.setup_browser()
                
            browser_action = kwargs.get("action")
            if not browser_action:
                raise ValueError("Browser action required")
                
            # Create browser tool
            browser_tool = BrowserTool(self.instance)
            
            # Execute the action using BrowserTool
            result = browser_tool(command=browser_action, **{k: v for k, v in kwargs.items() if k != 'action'})
            return {"success": True, "action": browser_action, "result": result}
        
        elif action_type == "edit":
            # File operations
            edit_action = kwargs.get("action", "view")
            path = kwargs.get("path")
            
            if not path:
                raise ValueError("Path required for edit action")
                
            edit_tool = EditTool(self.instance)
            result = edit_tool(command=edit_action, **{k: v for k, v in kwargs.items() if k != 'action'})
            return {"success": True, "action": edit_action, "result": result}
            
        else:
            raise ValueError(f"Unknown action type: {action_type}")
    
    async def save_auth_state(self, name: str = "default") -> str:
        """Save browser authentication state
        
        Args:
            name: Name for the auth state
            
        Returns:
            Auth state ID
        """
        if not self.instance:
            raise ValueError("Instance not started. Call start_instance first.")
        if not self.browser_cdp_url:
            raise ValueError("Browser not started. Call setup_browser first.")
            
        logger.info(f"Saving auth state with name: {name}")
        auth_response = self.instance.save_auth(name=name)
        self.auth_state_id = auth_response.auth_state_id
        return self.auth_state_id
        
    async def run_agent(self, prompt: str, tools: List[str] = None, system: str = None) -> Dict:
        """Run an AI agent with access to specified tools
        
        Args:
            prompt: User instruction for the agent
            tools: List of tool names to enable ("bash", "computer", "edit", "browser")
            system: System prompt for the agent
            
        Returns:
            Dict with agent response and steps
        """
        if not self.instance:
            raise ValueError("Instance not started. Call start_instance first.")
            
        if not tools:
            tools = ["computer", "browser"]
            
        if not system:
            system = BROWSER_SYSTEM_PROMPT
            
        # Prepare tool instances
        agent_tools = []
        for tool_name in tools:
            if tool_name == "bash":
                agent_tools.append(BashTool(self.instance))
            elif tool_name == "computer":
                agent_tools.append(ComputerTool(self.instance))
            elif tool_name == "edit":
                agent_tools.append(EditTool(self.instance))
            elif tool_name == "browser":
                # Make sure browser is started
                if not self.browser_cdp_url:
                    await self.setup_browser()
                agent_tools.append(BrowserTool(self.instance))
                
        # Run agent action with tools
        logger.info(f"Running agent with prompt: {prompt[:50]}...")
        response = self.client.act(
            model=Anthropic(),
            tools=agent_tools,
            system=system,
            prompt=prompt,
            on_step=lambda step: logger.info(f"Agent step: {step.text[:100]}...")
        )
        
        return {
            "text": response.text,
            "steps": [step.text for step in response.steps]
        }
    
    async def stop_instance(self) -> None:
        """Stop Scrapybara instance and clean up resources"""
        if self.instance:
            try:
                self.instance.stop()
                logger.info("Scrapybara instance stopped successfully")
            except Exception as e:
                logger.error(f"Error stopping Scrapybara instance: {e}")
        
        self.instance = None
        self.browser_cdp_url = None
        self.stream_url = None
        self.auth_state_id = None


class DashboardViewer:
    """Manages the trading dashboard HTML and viewer components"""
    
    def __init__(self, config: Optional[TradingDesktopConfig] = None):
        """Initialize dashboard viewer
        
        Args:
            config: Trading desktop configuration
        """
        self.config = config or TradingDesktopConfig()
        self.dashboard_path = Path(__file__).parent / "trading_dashboard.html"
        self.streaming_enabled = False
        self.stream_url = None
    
    def get_dashboard_html(self) -> str:
        """Get dashboard HTML content
        
        Returns:
            HTML content as string
        """
        if not self.dashboard_path.exists():
            raise FileNotFoundError(f"Dashboard HTML not found at {self.dashboard_path}")
        
        with open(self.dashboard_path, "r") as f:
            return f.read()
    
    def inject_stream_url(self, html: str, stream_url: str) -> str:
        """Inject stream URL into dashboard HTML
        
        Args:
            html: Original HTML content
            stream_url: URL to stream from Scrapybara
            
        Returns:
            Modified HTML with stream viewer
        """
        # Create a simple iframe viewer component
        stream_viewer = f"""
        <div id="stream-viewer" style="margin-top: 20px; border: 1px solid #9945FF; border-radius: 10px; overflow: hidden;">
            <h2 style="background-color: #9945FF; color: white; margin: 0; padding: 10px;">Live Trading Stream</h2>
            <iframe src="{stream_url}" style="width: 100%; height: 500px; border: none;"></iframe>
        </div>
        """
        
        # Insert the viewer before the closing body tag
        return html.replace('</body>', f'{stream_viewer}\n</body>')

    async def launch_with_desktop_manager(
        self, 
        desktop_manager: DesktopManager, 
        stream_url: Optional[str] = None
    ) -> None:
        """Launch dashboard with desktop manager
        
        Args:
            desktop_manager: Initialized desktop manager
            stream_url: Optional stream URL to include in viewer
        """
        html_content = self.get_dashboard_html()
        
        # If stream URL provided, inject the viewer
        if stream_url:
            self.stream_url = stream_url
            self.streaming_enabled = True
            html_content = self.inject_stream_url(html_content, stream_url)
        
        # Create temp HTML file with the content
        temp_html_path = Path(desktop_manager.local_temp_dir) / "trading_dashboard_with_stream.html"
        with open(temp_html_path, "w") as f:
            f.write(html_content)
        
        # Load in desktop manager's browser
        await desktop_manager.load_html_file(temp_html_path)
        logger.info(f"Trading dashboard launched with desktop manager")


async def setup_trading_environment(
    config: TradingDesktopConfig, 
    use_scrapybara: bool = False,
    launch_browser: bool = True
) -> Dict:
    """Set up and launch the complete trading environment
    
    Args:
        config: Trading desktop configuration
        use_scrapybara: Whether to integrate with Scrapybara
        
    Returns:
        Dict containing setup information and handles
    """
    desktop_manager = DesktopManager(config)
    dashboard_viewer = DashboardViewer(config)
    
    scrapybara_integration = None
    stream_url = None
    
    # Start the desktop environment
    await desktop_manager.initialize()
    
    # Set up Scrapybara if enabled
    if use_scrapybara and SCRAPYBARA_AVAILABLE:
        try:
            api_key = os.environ.get("SCRAPY_API_KEY")
            if not api_key:
                logger.warning("SCRAPY_API_KEY not set - Scrapybara integration disabled")
            else:
                scrapybara_integration = ScrapybaraIntegration(api_key=api_key)
                instance_info = await scrapybara_integration.start_instance()
                stream_url = instance_info.get("stream_url")
                logger.info(f"Scrapybara integration active - stream URL: {stream_url}")
                
                # Launch browser if requested
                if launch_browser:
                    cdp_url = await scrapybara_integration.setup_browser()
                    logger.info(f"Browser launched with CDP URL: {cdp_url}")
        except Exception as e:
            logger.error(f"Error setting up Scrapybara integration: {e}")
    
    # Launch dashboard with optional stream
    await dashboard_viewer.launch_with_desktop_manager(desktop_manager, stream_url)
    
    return {
        "desktop_manager": desktop_manager,
        "dashboard_viewer": dashboard_viewer,
        "scrapybara_integration": scrapybara_integration,
        "stream_url": stream_url
    }


async def cleanup_environment(
    handles: Dict[str, Any]
) -> None:
    """Clean up and close all environment resources
    
    Args:
        handles: Dict containing environment handles from setup_trading_environment
    """
    # Stop Scrapybara instance if active
    scrapybara_integration = handles.get("scrapybara_integration")
    if scrapybara_integration:
        await scrapybara_integration.stop_instance()
    
    # Close E2B desktop manager
    desktop_manager = handles.get("desktop_manager")
    if desktop_manager:
        await desktop_manager.cleanup()
