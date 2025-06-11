"""
Solana Theme for E2B Trading Desktop
Implements Solana color palette and UI design elements
"""

# Solana color palette
SOLANA_PURPLE = "#9945FF"
SOLANA_GREEN = "#14F195"
SOLANA_DARK = "#121212"
SOLANA_LIGHT = "#FFFFFF"

# Additional UI colors derived from the main palette
SOLANA_PURPLE_LIGHT = "#B57FFF"
SOLANA_PURPLE_DARK = "#7A37CC"
SOLANA_GREEN_LIGHT = "#66F7BE"
SOLANA_GREEN_DARK = "#10C077"
SOLANA_GRAY = "#5F5F5F"
SOLANA_LIGHT_GRAY = "#E0E0E0"

# UI Component styling
BUTTON_STYLE = f"""
    background-color: {SOLANA_PURPLE};
    color: {SOLANA_LIGHT};
    border: none;
    border-radius: 4px;
    padding: 8px 16px;
    font-weight: bold;
    cursor: pointer;
    transition: background-color 0.3s;
"""

BUTTON_HOVER_STYLE = f"background-color: {SOLANA_PURPLE_LIGHT};"
BUTTON_ACTIVE_STYLE = f"background-color: {SOLANA_PURPLE_DARK};"

ACTION_BUTTON_STYLE = f"""
    background-color: {SOLANA_GREEN};
    color: {SOLANA_DARK};
    border: none;
    border-radius: 4px;
    padding: 8px 16px;
    font-weight: bold;
    cursor: pointer;
    transition: background-color 0.3s;
"""

ACTION_BUTTON_HOVER_STYLE = f"background-color: {SOLANA_GREEN_LIGHT};"
ACTION_BUTTON_ACTIVE_STYLE = f"background-color: {SOLANA_GREEN_DARK};"

INPUT_STYLE = f"""
    background-color: {SOLANA_DARK};
    color: {SOLANA_LIGHT};
    border: 1px solid {SOLANA_PURPLE};
    border-radius: 4px;
    padding: 8px;
    outline: none;
    transition: border-color 0.3s;
"""

INPUT_FOCUS_STYLE = f"border-color: {SOLANA_GREEN};"

# Trading indicators styling
BUY_COLOR = SOLANA_GREEN
SELL_COLOR = "#FF6B4A"  # Complementary to Solana green
HOLD_COLOR = SOLANA_PURPLE
POSITIVE_CHANGE = SOLANA_GREEN
NEGATIVE_CHANGE = "#FF6B4A"

# Dashboard styling
DASHBOARD_STYLE = f"""
    body {{
        font-family: 'Inter', 'Roboto', sans-serif;
        background-color: {SOLANA_DARK};
        color: {SOLANA_LIGHT};
        margin: 0;
        padding: 0;
    }}
    
    .header {{
        background-color: {SOLANA_PURPLE};
        color: {SOLANA_LIGHT};
        padding: 16px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }}
    
    .sidebar {{
        background-color: {SOLANA_DARK};
        border-right: 1px solid {SOLANA_GRAY};
        width: 250px;
        height: 100vh;
        position: fixed;
        left: 0;
        top: 0;
        padding-top: 60px;
    }}
    
    .sidebar-item {{
        padding: 12px 16px;
        cursor: pointer;
        transition: background-color 0.3s;
    }}
    
    .sidebar-item:hover {{
        background-color: rgba(153, 69, 255, 0.1);
    }}
    
    .sidebar-item.active {{
        background-color: rgba(153, 69, 255, 0.2);
        border-left: 4px solid {SOLANA_PURPLE};
    }}
    
    .content {{
        margin-left: 250px;
        padding: 16px;
    }}
    
    .card {{
        background-color: #202020;
        border-radius: 8px;
        border-top: 4px solid {SOLANA_PURPLE};
        padding: 16px;
        margin-bottom: 16px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }}
    
    .card.green-accent {{
        border-top: 4px solid {SOLANA_GREEN};
    }}
    
    .agent {{
        border: 1px solid #333;
        border-radius: 8px;
        padding: 12px;
        margin-bottom: 12px;
    }}
    
    .buy {{
        color: {BUY_COLOR};
    }}
    
    .sell {{
        color: {SELL_COLOR};
    }}
    
    .hold {{
        color: {HOLD_COLOR};
    }}
    
    .chart-container {{
        background-color: #1A1A1A;
        border-radius: 8px;
        padding: 16px;
    }}
    
    .data-table {{
        width: 100%;
        border-collapse: collapse;
    }}
    
    .data-table th {{
        background-color: #333;
        padding: 12px;
        text-align: left;
    }}
    
    .data-table td {{
        padding: 12px;
        border-bottom: 1px solid #444;
    }}
    
    .progress-bar {{
        background-color: #333;
        border-radius: 4px;
        height: 8px;
        overflow: hidden;
    }}
    
    .progress-bar-fill {{
        background-color: {SOLANA_PURPLE};
        height: 100%;
        transition: width 0.3s ease;
    }}
    
    .progress-bar-fill.green {{
        background-color: {SOLANA_GREEN};
    }}
"""

# Trading desktop background with Solana branding
DESKTOP_BACKGROUND = f"""
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
    
    <!-- Solana-inspired patterns -->
    <circle cx="960" cy="540" r="300" fill="none" stroke="{SOLANA_PURPLE}" stroke-width="2" opacity="0.1" />
    <circle cx="960" cy="540" r="450" fill="none" stroke="{SOLANA_PURPLE}" stroke-width="2" opacity="0.07" />
    <circle cx="960" cy="540" r="600" fill="none" stroke="{SOLANA_PURPLE}" stroke-width="2" opacity="0.04" />
    
    <!-- Green accents -->
    <circle cx="300" cy="200" r="100" fill="{SOLANA_GREEN}" opacity="0.05" />
    <circle cx="1600" cy="800" r="150" fill="{SOLANA_PURPLE}" opacity="0.05" />
    
    <!-- Grid lines -->
    <g opacity="0.05">
        <line x1="0" y1="270" x2="1920" y2="270" stroke="{SOLANA_LIGHT}" stroke-width="1" />
        <line x1="0" y1="540" x2="1920" y2="540" stroke="{SOLANA_LIGHT}" stroke-width="1" />
        <line x1="0" y1="810" x2="1920" y2="810" stroke="{SOLANA_LIGHT}" stroke-width="1" />
        <line x1="480" y1="0" x2="480" y2="1080" stroke="{SOLANA_LIGHT}" stroke-width="1" />
        <line x1="960" y1="0" x2="960" y2="1080" stroke="{SOLANA_LIGHT}" stroke-width="1" />
        <line x1="1440" y1="0" x2="1440" y2="1080" stroke="{SOLANA_LIGHT}" stroke-width="1" />
    </g>
    
    <!-- Solana logo hint -->
    <g transform="translate(1750, 1000) scale(0.5)">
        <path d="M30,10 L10,50 L30,90 L160,90 L180,50 L160,10 Z" fill="none" stroke="{SOLANA_PURPLE}" stroke-width="3" opacity="0.2" />
    </g>
</svg>
"""

def get_html_template(title="Solana Multi-Agent Trading Desktop"):
    """
    Returns an HTML template with Solana styling
    """
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{title}</title>
        <style>
            {DASHBOARD_STYLE}
        </style>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    </head>
    <body>
        <div class="header">
            <h1>{title}</h1>
        </div>
        
        <div class="sidebar">
            <div class="sidebar-item active">Dashboard</div>
            <div class="sidebar-item">Market Overview</div>
            <div class="sidebar-item">Trading Agents</div>
            <div class="sidebar-item">Portfolio</div>
            <div class="sidebar-item">Settings</div>
        </div>
        
        <div class="content">
            <div id="main-content"></div>
        </div>
        
        <script>
            // JavaScript for the dashboard functionality would go here
        </script>
    </body>
    </html>
    """

def apply_solana_desktop_theme(sandbox):
    """
    Applies Solana theme to the E2B desktop environment
    
    Args:
        sandbox: E2B desktop sandbox instance
    """
    try:
        # Create background SVG
        with open("/tmp/solana_background.svg", "w") as f:
            f.write(DESKTOP_BACKGROUND)
        
        # Set as desktop background (implementation depends on sandbox capabilities)
        # Example for Linux-based desktop:
        sandbox.run([
            "gsettings", "set", "org.gnome.desktop.background", 
            "picture-uri", "file:///tmp/solana_background.svg"
        ])
        
        return True
    except Exception as e:
        print(f"Error applying Solana theme: {e}")
        return False

def create_solana_dashboard(sandbox):
    """
    Creates a Solana-themed dashboard in the browser
    
    Args:
        sandbox: E2B desktop sandbox instance
    """
    try:
        # Create dashboard HTML
        dashboard_html = get_html_template("Solana Trading Dashboard")
        
        # Add agent-specific content
        agent_content = f"""
        <div class="card">
            <h2>Multi-Agent Analysis</h2>
            <div class="agent">
                <h3>Warren Buffett</h3>
                <p>Recommendation: <span class="hold">HOLD</span></p>
                <p>Looking for long-term value in quality projects</p>
                <div class="progress-bar">
                    <div class="progress-bar-fill" style="width: 65%;"></div>
                </div>
            </div>
            <div class="agent">
                <h3>Cathie Wood</h3>
                <p>Recommendation: <span class="buy">BUY</span></p>
                <p>Strong innovation potential with exponential growth</p>
                <div class="progress-bar">
                    <div class="progress-bar-fill green" style="width: 80%;"></div>
                </div>
            </div>
        </div>
        
        <div class="card green-accent">
            <h2>Market Overview</h2>
            <div class="chart-container">
                [Chart Placeholder]
            </div>
        </div>
        
        <div class="card">
            <h2>Active Positions</h2>
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Token</th>
                        <th>Position</th>
                        <th>Entry Price</th>
                        <th>Current Price</th>
                        <th>P/L</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>SOL</td>
                        <td>2.5</td>
                        <td>$150.00</td>
                        <td>$159.37</td>
                        <td class="buy">+6.25%</td>
                    </tr>
                    <tr>
                        <td>JUP</td>
                        <td>100</td>
                        <td>$1.20</td>
                        <td>$1.35</td>
                        <td class="buy">+12.5%</td>
                    </tr>
                </tbody>
            </table>
        </div>
        """
        
        # Insert into template and save
        dashboard_html = dashboard_html.replace('<div id="main-content"></div>', agent_content)
        
        with open("/tmp/solana_dashboard.html", "w") as f:
            f.write(dashboard_html)
        
        # Open dashboard in browser
        sandbox.launch('google-chrome', ['file:///tmp/solana_dashboard.html'])
        
        return True
    except Exception as e:
        print(f"Error creating Solana dashboard: {e}")
        return False
