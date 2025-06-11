"""
Unified Integration Module for Solana Trading Desktop
Combines model replay, evaluation tools, Gradio interface, and desktop agents
"""

import os
import sys
import json
import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Tuple
from threading import Thread

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s [%(name)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("solana_trading_unified")

# Try imports, gracefully handle missing dependencies
try:
    import gradio as gr
    from gradio_modal import Modal
    GRADIO_AVAILABLE = True
except ImportError:
    logger.warning("Gradio not found. UI features will be limited.")
    GRADIO_AVAILABLE = False

try:
    from e2b_desktop import Sandbox
    E2B_AVAILABLE = True
except ImportError:
    logger.warning("E2B Desktop not found. Desktop sandbox features will be limited.")
    E2B_AVAILABLE = False

try:
    from smolagents import CodeAgent, InferenceClientModel
    from smolagents.agent_types import AgentImage, AgentText
    SMOLAGENTS_AVAILABLE = True
except ImportError:
    logger.warning("SmolaAgents not found. Agent features will be limited.")
    SMOLAGENTS_AVAILABLE = False

# Internal imports
from .config import TradingDesktopConfig
from .desktop_manager import DesktopManager
from .integrations import ScrapybaraIntegration, DashboardViewer, setup_trading_environment

# Import replay, styling, evaluation components
from .model_replay import FakeModelReplayLog
from .scripts_and_styling import (
    SANDBOX_HTML_TEMPLATE,
    SANDBOX_CSS_TEMPLATE, 
    FOOTER_HTML,
    CUSTOM_JS
)

# Conditional imports based on availability
if SMOLAGENTS_AVAILABLE:
    from .e2bqwen import E2BVisionAgent, get_agent_summary_erase_images
    from .gradio_script import stream_to_gradio, pull_messages_from_step


class UnifiedDesktopManager:
    """
    Unified manager for Solana Trading Desktop that combines:
    - E2B Desktop integration
    - Agent evaluation tools
    - Replay capabilities
    - Gradio UI (optional)
    - Scrapybara integration
    """
    
    def __init__(
        self, 
        config: Optional[TradingDesktopConfig] = None,
        enable_gradio: bool = False,
        enable_model_replay: bool = False,
        replay_log_folder: Optional[str] = None,
    ):
        """Initialize the unified desktop manager
        
        Args:
            config: Trading desktop configuration
            enable_gradio: Whether to enable Gradio UI
            enable_model_replay: Whether to use model replay for testing
            replay_log_folder: Folder containing model replay logs
        """
        self.config = config or TradingDesktopConfig()
        self.enable_gradio = enable_gradio and GRADIO_AVAILABLE
        self.enable_model_replay = enable_model_replay and SMOLAGENTS_AVAILABLE
        self.replay_log_folder = replay_log_folder
        
        # Components
        self.desktop_manager = None
        self.dashboard_viewer = None
        self.scrapybara_integration = None
        self.gradio_app = None
        self.model = None
        self.agent = None
        self.flask_server = None
        
        # State
        self.running = False
        self.environment_handles = {}
    
    async def initialize(self) -> None:
        """Initialize all components based on configuration"""
        logger.info("Initializing Unified Desktop Manager")
        
        # Set up basic trading environment
        self.environment_handles = await setup_trading_environment(
            config=self.config,
            use_scrapybara=self.config.integrations.get("use_scrapybara", False)
        )
        
        self.desktop_manager = self.environment_handles.get("desktop_manager")
        self.dashboard_viewer = self.environment_handles.get("dashboard_viewer")
        self.scrapybara_integration = self.environment_handles.get("scrapybara_integration")
        
        # Configure model if needed
        if self.enable_model_replay and SMOLAGENTS_AVAILABLE:
            self.model = FakeModelReplayLog(log_folder=self.replay_log_folder or "default_log")
            logger.info(f"Model replay enabled using log folder: {self.replay_log_folder}")
        elif SMOLAGENTS_AVAILABLE:
            # Use the default model from smolagents
            self.model = InferenceClientModel()
            logger.info("Using InferenceClientModel for agent")
        
        # Create agent if possible
        if SMOLAGENTS_AVAILABLE and E2B_AVAILABLE and self.desktop_manager:
            # Create E2B desktop agent
            if hasattr(self.desktop_manager, 'sandbox') and self.desktop_manager.sandbox:
                self.agent = E2BVisionAgent(
                    model=self.model,
                    sandbox=self.desktop_manager.sandbox,
                    llm_system_prompt_template=self.config.agent.system_prompt,
                    name=self.config.agent.name
                )
                logger.info(f"Created E2B vision agent: {self.config.agent.name}")
        
        # Start Gradio UI if enabled
        if self.enable_gradio:
            await self.start_gradio_ui()
    
    async def start_gradio_ui(self) -> None:
        """Start Gradio UI in a separate thread"""
        if not GRADIO_AVAILABLE:
            logger.error("Gradio not available. Cannot start UI.")
            return
        
        # Create Gradio UI
        with gr.Blocks(css=SANDBOX_CSS_TEMPLATE.replace("<<WIDTH>>", str(800)).replace("<<HEIGHT>>", str(600))) as app:
            # Apply theme
            app = apply_theme(app)
            
            with gr.Row():
                with gr.Column():
                    gr.Markdown(f"# Solana Trading Desktop - Agent Control")
                    
                    # Task input
                    with gr.Group():
                        task_input = gr.Textbox(
                            label="Trading Task",
                            placeholder="Enter a task for the agent to perform...",
                            lines=3,
                        )
                        
                        gr.Examples(
                            examples=[
                                "Check the current SOL price on Birdeye",
                                "Create a market analysis dashboard for SOL/USDC",
                                "Show me the performance of my portfolio",
                                "Set up a price alert for SOL at $200",
                            ],
                            inputs=task_input,
                        )
                    
                    # Action buttons
                    with gr.Row():
                        run_btn = gr.Button("Run Agent", variant="primary")
                        stop_btn = gr.Button("Stop Agent", variant="stop")
                        refresh_btn = gr.Button("Refresh View")
                    
                    # Status indicator
                    status = gr.Markdown("Status: Ready")
                
                # Desktop view
                with gr.Column():
                    sandbox_html = gr.HTML(
                        SANDBOX_HTML_TEMPLATE.format(
                            stream_url="about:blank",
                            status_class="status-view-only",
                            status_text="Loading..."
                        )
                    )
            
            # Agent chat output
            chat_output = gr.Chatbot(label="Agent Activity")
            
            # Connect buttons to functions
            def on_run(task):
                if not self.agent:
                    return "ERROR: Agent not initialized"
                # Start agent task in background
                return f"Starting task: {task}"
            
            run_btn.click(on_run, inputs=[task_input], outputs=[status])
            
            # Footer
            gr.HTML(FOOTER_HTML)
        
        # Save Gradio app
        self.gradio_app = app
        
        # Start in background thread
        def start_gradio():
            self.gradio_app.launch(
                share=self.config.gradio.get("share", False),
                server_name=self.config.gradio.get("server_name", "127.0.0.1"),
                server_port=self.config.gradio.get("server_port", 7860),
                favicon_path=self.config.gradio.get("favicon_path", None),
            )
        
        Thread(target=start_gradio, daemon=True).start()
        logger.info(f"Gradio UI started on port {self.config.gradio.get('server_port', 7860)}")
    
    async def start_eval_server(self, eval_path: str = "./eval_results", port: int = 5000) -> None:
        """Start evaluation server for viewing agent results
        
        Args:
            eval_path: Path to evaluation results
            port: Server port
        """
        from .show_eval import app as flask_app
        
        # Configure Flask app
        flask_app.config["EVAL_PATH"] = eval_path
        
        # Start Flask server in background thread
        def start_flask():
            flask_app.run(host="127.0.0.1", port=port, debug=False)
        
        Thread(target=start_flask, daemon=True).start()
        self.flask_server = flask_app
        logger.info(f"Evaluation server started on http://127.0.0.1:{port}")
    
    async def run_agent_task(self, task: str) -> Dict:
        """Run a task with the agent
        
        Args:
            task: Task description
            
        Returns:
            Dict with task results
        """
        if not self.agent:
            raise ValueError("Agent not initialized")
        
        # Run the agent
        try:
            result = await asyncio.to_thread(self.agent.run, task)
            return {
                "success": True,
                "task": task,
                "result": result,
                "steps": self.agent.memory.steps if hasattr(self.agent, "memory") else []
            }
        except Exception as e:
            logger.error(f"Error running agent task: {e}")
            return {
                "success": False,
                "task": task,
                "error": str(e)
            }
    
    async def cleanup(self) -> None:
        """Clean up all resources"""
        # Clean up environment handles
        if self.environment_handles:
            await cleanup_environment(self.environment_handles)
        
        # Clean up Gradio app
        if self.gradio_app and hasattr(self.gradio_app, "close"):
            try:
                self.gradio_app.close()
                logger.info("Gradio app closed")
            except:
                pass
        
        # Clean up Flask server
        if self.flask_server and hasattr(self.flask_server, "config"):
            try:
                func = request.environ.get('werkzeug.server.shutdown')
                if func is not None:
                    func()
                logger.info("Flask server shutdown")
            except:
                pass


# Utility function to apply styling to Gradio app
def apply_theme(app):
    """Apply Solana theme to Gradio app"""
    if not GRADIO_AVAILABLE:
        return app
        
    # Apply Solana color theme
    app.theme = gr.themes.Base(
        primary_hue="indigo",
        secondary_hue="green",
        neutral_hue="gray",
        text_size=gr.themes.sizes.text_md,
    ).set(
        body_background_fill="#121212",
        body_background_fill_dark="#121212",
        body_text_color="#f9fafb",
        body_text_color_dark="#f9fafb",
        button_primary_background_fill="#9945FF",
        button_primary_background_fill_dark="#9945FF",
        button_primary_text_color="#ffffff",
        button_primary_text_color_dark="#ffffff",
        button_secondary_background_fill="#14F195",
        button_secondary_background_fill_dark="#14F195",
        button_secondary_text_color="#000000",
        button_secondary_text_color_dark="#000000",
    )
    
    return app


# Main function to run unified desktop
async def run_unified_desktop(config: Optional[TradingDesktopConfig] = None, **kwargs) -> UnifiedDesktopManager:
    """Run unified desktop with all integrations
    
    Args:
        config: Trading desktop configuration
        **kwargs: Additional configuration options
        
    Returns:
        UnifiedDesktopManager instance
    """
    # Create and initialize manager
    manager = UnifiedDesktopManager(
        config=config,
        enable_gradio=kwargs.get("enable_gradio", False),
        enable_model_replay=kwargs.get("enable_model_replay", False),
        replay_log_folder=kwargs.get("replay_log_folder", None),
    )
    
    # Initialize components
    await manager.initialize()
    
    # Start eval server if enabled
    if kwargs.get("start_eval_server", False):
        await manager.start_eval_server(
            eval_path=kwargs.get("eval_path", "./eval_results"),
            port=kwargs.get("eval_port", 5000),
        )
    
    return manager
