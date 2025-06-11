# SMOLana Trading Dashboard Launcher Guide

This guide explains how to use the SMOLana Trading Dashboard launcher with the new Scrapybara integration features.

## Prerequisites

Before using the launcher, ensure you have the following environment variables set:

```bash
# Required for full functionality
export SOLANA_RPC_URL="https://api.helius-rpc.com/?api-key=your-helius-key"  # Solana RPC URL (preferably Helius)
export OPENAI_API_KEY="your-openai-key"        # For AI assistance features
export OPENROUTER_API_KEY="your-openrouter-key"  # Alternative AI provider

# Optional for browser automation features
export SCRAPY_API_KEY="your-scrapybara-key"    # For Scrapybara integration
```

## Basic Usage

To launch the SMOLana Trading Dashboard with default settings:

```bash
python simple_launcher.py
```

This will start a Flask server and open a webview window with the trading dashboard.

## Command Line Options

The launcher supports several command line options:

### `--debug`

Enables debug mode for the webview and provides more detailed logging:

```bash
python simple_launcher.py --debug
```

### `--port PORT`

Specifies a custom port for the Flask server (default is an available port starting from 5000):

```bash
python simple_launcher.py --port 5050
```

### `--fullscreen`

Launches the trading dashboard in fullscreen mode:

```bash
python simple_launcher.py --fullscreen
```

### `--browser-only`

Opens the trading dashboard in your default web browser instead of a webview window:

```bash
python simple_launcher.py --browser-only
```

This is useful if you prefer your browser over the embedded webview.

## Scrapybara Integration Options

The following options are available when you have a valid Scrapybara API key set in the `SCRAPY_API_KEY` environment variable:

### `--scrapybara`

Enables Scrapybara browser automation and streaming integration:

```bash
python simple_launcher.py --scrapybara
```

This starts a Scrapybara browser instance and embeds the live stream in the trading dashboard.

### `--stream-only`

Opens only the Scrapybara stream in your browser:

```bash
python simple_launcher.py --scrapybara --stream-only
```

This is useful for monitoring the trading agent's actions in a full browser window.

## Combined Examples

You can combine multiple options for custom configurations:

```bash
# Launch in browser with Scrapybara integration
python simple_launcher.py --browser-only --scrapybara

# Launch in fullscreen with Scrapybara integration
python simple_launcher.py --fullscreen --scrapybara

# Launch with a custom port and debug mode
python simple_launcher.py --port 8080 --debug
```

## Troubleshooting

Common issues and solutions:

1. **Missing environment variables**:
   - Ensure all required environment variables are set properly
   - For Scrapybara features, make sure `SCRAPY_API_KEY` is valid and set

2. **Port already in use**:
   - Use the `--port` option to specify a different port
   - Check if another instance of the launcher is already running

3. **Scrapybara stream not showing**:
   - Confirm your `SCRAPY_API_KEY` is valid and not expired
   - Check the console logs for any connection errors
   - Ensure you have a stable internet connection

4. **Dashboard not loading**:
   - Check that Flask server started correctly
   - Look for any JavaScript console errors in the browser
   - Verify that the trading dashboard HTML files exist
