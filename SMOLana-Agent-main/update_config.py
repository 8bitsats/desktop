#!/usr/bin/env python3
"""
Script to update the existing config.json file with new Scrapybara integration settings
"""

import json
import os
import sys
from pathlib import Path

# Config file path
CONFIG_PATH = Path(__file__).parent / "config.json"
TEMPLATE_PATH = Path(__file__).parent / "config.template.json"

def update_config():
    """Update the config.json file with new settings"""
    
    print(f"Updating configuration at: {CONFIG_PATH}")
    
    # Load existing config
    try:
        with open(CONFIG_PATH, 'r') as f:
            config = json.load(f)
            print("✅ Loaded existing config.json")
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"❌ Error loading config: {e}")
        print("Creating a new config file...")
        config = {}

    # Load template for new settings
    try:
        with open(TEMPLATE_PATH, 'r') as f:
            template = json.load(f)
            print("✅ Loaded template configuration")
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"❌ Error loading template: {e}")
        sys.exit(1)
    
    # Preserve existing API keys
    api_keys = config.get('api_keys', {})
    
    # Update config with template values, preserving existing API keys
    for key, value in template.items():
        if key == 'api_keys':
            # For API keys, merge rather than replace
            if 'api_keys' not in config:
                config['api_keys'] = {}
            for api_key, api_value in value.items():
                # Only use template value if key doesn't exist in original config
                if api_key not in config['api_keys'] or not config['api_keys'][api_key]:
                    config['api_keys'][api_key] = api_value
        else:
            # For other top-level keys, use template value if not present
            if key not in config:
                config[key] = value
    
    # Add new sections if they don't exist
    for section in ['scrapybara', 'solana', 'ui', 'trading']:
        if section not in config:
            config[section] = template[section]
    
    # Always add desktop_streaming flag
    config['desktop_streaming'] = True
    
    # Write updated config back to file
    try:
        with open(CONFIG_PATH, 'w') as f:
            json.dump(config, f, indent=2)
            print("✅ Successfully updated config.json with new settings")
    except Exception as e:
        print(f"❌ Error writing config: {e}")
        sys.exit(1)
        
    print("\nConfig update complete! Your existing API keys have been preserved.")
    print("The following sections have been added or updated:")
    print("- scrapybara: Browser automation and streaming settings")
    print("- solana: Blockchain connection and wallet settings")
    print("- ui: Dashboard appearance and behavior settings")
    print("- trading: Transaction parameters and controls")

if __name__ == "__main__":
    update_config()
