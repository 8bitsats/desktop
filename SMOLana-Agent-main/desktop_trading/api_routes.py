"""
API routes for the Solana trading dashboard.
These endpoints connect the frontend dashboard to the Solana blockchain.
"""

import os
import json
import logging
import asyncio
from typing import Dict, List, Optional, Any
from flask import Blueprint, jsonify, request, current_app
from .solana_api import SolanaAPI
import openai
import aiohttp

# Set up logging
logger = logging.getLogger(__name__)

# Create Blueprint for API routes
api = Blueprint('api', __name__)

# Initialize global Solana API client
solana_client = SolanaAPI()

# Set up OpenAI client for AI agent recommendations
openai.api_key = os.environ.get("OPENAI_API_KEY", "")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
OPENROUTER_MODEL = os.environ.get("OPENROUTER_MODEL", "qwen/qwen2.5-vl-72b-instruct:free")

# Helper function to run async functions in Flask routes
def run_async(coro):
    """Run an async coroutine and return its result."""
    return asyncio.run(coro)

@api.route('/market-data', methods=['GET'])
def get_market_data():
    """Get current market data for popular tokens."""
    try:
        data = run_async(solana_client.get_market_data())
        return jsonify(data)
    except Exception as e:
        logger.error(f"Error fetching market data: {e}")
        return jsonify({"error": str(e)}), 500

@api.route('/connect-wallet', methods=['POST'])
def connect_wallet():
    """Connect wallet with private key."""
    try:
        data = request.json
        private_key = data.get('privateKey')
        success = solana_client.connect_wallet(private_key)
        if success:
            return jsonify({"success": True, "message": "Wallet connected successfully"})
        else:
            return jsonify({"success": False, "message": "Failed to connect wallet"}), 400
    except Exception as e:
        logger.error(f"Error connecting wallet: {e}")
        return jsonify({"error": str(e)}), 500

@api.route('/disconnect-wallet', methods=['POST'])
def disconnect_wallet():
    """Disconnect wallet and clear sensitive data."""
    try:
        solana_client.disconnect_wallet()
        return jsonify({"success": True, "message": "Wallet disconnected"})
    except Exception as e:
        logger.error(f"Error disconnecting wallet: {e}")
        return jsonify({"error": str(e)}), 500

@api.route('/wallet-balance', methods=['GET'])
def get_wallet_balance():
    """Get wallet SOL balance."""
    try:
        data = run_async(solana_client.get_wallet_balance())
        return jsonify(data)
    except Exception as e:
        logger.error(f"Error getting wallet balance: {e}")
        return jsonify({"error": str(e)}), 500

@api.route('/portfolio-data', methods=['GET'])
def get_portfolio():
    """Get complete portfolio data."""
    try:
        data = run_async(solana_client.get_portfolio_data())
        return jsonify(data)
    except Exception as e:
        logger.error(f"Error getting portfolio data: {e}")
        return jsonify({"error": str(e)}), 500

@api.route('/token-price', methods=['GET'])
def get_token_price():
    """Get price for a specific token."""
    try:
        token = request.args.get('token', 'SOL')
        token_address = solana_client._get_token_address(token)
        if not token_address:
            return jsonify({"error": f"Unknown token: {token}"}), 400
        
        price = run_async(solana_client.get_token_price(token_address))
        return jsonify({"token": token, "price": price})
    except Exception as e:
        logger.error(f"Error getting token price: {e}")
        return jsonify({"error": str(e)}), 500

@api.route('/execute-trade', methods=['POST'])
def execute_trade():
    """Execute token swap/trade."""
    try:
        data = request.json
        input_token = data.get('inputToken')
        output_token = data.get('outputToken')
        amount = float(data.get('amount', 0))
        slippage = int(data.get('slippage', 100))  # default 1%
        
        if not input_token or not output_token or amount <= 0:
            return jsonify({"error": "Missing required parameters"}), 400
            
        result = run_async(solana_client.execute_swap(input_token, output_token, amount, slippage))
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error executing trade: {e}")
        return jsonify({"error": str(e)}), 500

@api.route('/get-quote', methods=['POST'])
def get_swap_quote():
    """Get quote for token swap."""
    try:
        data = request.json
        input_token = data.get('inputToken')
        output_token = data.get('outputToken')
        amount = float(data.get('amount', 0))
        slippage = int(data.get('slippage', 100))  # default 1%
        
        if not input_token or not output_token or amount <= 0:
            return jsonify({"error": "Missing required parameters"}), 400
            
        result = run_async(solana_client.get_swap_quote(input_token, output_token, amount, slippage))
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error getting swap quote: {e}")
        return jsonify({"error": str(e)}), 500

async def get_ai_agent_recommendation(market_data, portfolio_data=None):
    """Get trading recommendations from AI agent."""
    try:
        system_prompt = """You are a crypto trading assistant focused on Solana tokens. 
        Analyze the provided market data and portfolio to give actionable trade recommendations.
        Your recommendations should include:
        1. Which token to buy or sell
        2. A brief reasoning with market analysis
        3. A confidence level (Low, Medium, High)
        4. Target price or percentage gain
        Make your advice specific, concise and actionable."""
        
        # Construct message for AI recommendation
        market_context = json.dumps(market_data, indent=2)
        portfolio_context = json.dumps(portfolio_data, indent=2) if portfolio_data else "No portfolio data available"
        
        user_message = f"""Please analyze this market data and provide trading recommendations:
        
        MARKET DATA:
        {market_context}
        
        PORTFOLIO DATA:
        {portfolio_context}
        
        Provide 2-3 specific trading recommendations with token, action (buy/sell), reasoning, confidence level, and target."""
        
        # Try OpenAI first
        try:
            if openai.api_key:
                response = await openai.ChatCompletion.acreate(
                    model="gpt-4",  # or appropriate model
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_message}
                    ]
                )
                return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
        
        # Fallback to OpenRouter
        try:
            if OPENROUTER_API_KEY:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        "https://openrouter.ai/api/v1/chat/completions",
                        headers={
                            "Content-Type": "application/json",
                            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                            "HTTP-Referer": "solana-trading-dashboard",
                            "X-Title": "Solana Trading Dashboard"
                        },
                        json={
                            "model": OPENROUTER_MODEL,
                            "messages": [
                                {"role": "system", "content": system_prompt},
                                {"role": "user", "content": user_message}
                            ]
                        }
                    ) as response:
                        if response.status == 200:
                            result = await response.json()
                            return result["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"OpenRouter API error: {e}")
            
        # Fallback response if both APIs fail
        return """
        Recommendation 1:
        - Token: SOL
        - Action: Buy
        - Reasoning: Recent market momentum and platform growth
        - Confidence: Medium
        - Target: +10% within 7 days
        
        Recommendation 2:
        - Token: BONK
        - Action: Hold
        - Reasoning: Consolidating after recent gains, potential for volatility
        - Confidence: Low
        - Target: Monitor for breakout above resistance
        """
    except Exception as e:
        logger.error(f"Error generating AI recommendation: {e}")
        return str(e)

@api.route('/ai-recommendations', methods=['GET'])
def get_ai_recommendations():
    """Get AI-powered trading recommendations."""
    try:
        # Get current market data
        market_data = run_async(solana_client.get_market_data())
        
        # Get portfolio data if wallet is connected
        if solana_client.wallet_connected:
            portfolio_data = run_async(solana_client.get_portfolio_data())
        else:
            portfolio_data = None
            
        # Get AI recommendations
        recommendations = run_async(get_ai_agent_recommendation(market_data, portfolio_data))
        
        # Parse into structured format
        # For now we'll just return the raw text and parse it in the frontend
        return jsonify({
            "recommendations": recommendations,
            "timestamp": "now",  # Use proper timestamp in production
        })
    except Exception as e:
        logger.error(f"Error getting AI recommendations: {e}")
        return jsonify({"error": str(e)}), 500

@api.route('/recent-trades', methods=['GET'])
def get_recent_trades():
    """Get recent trades (placeholder for now)."""
    # In a real application, this would fetch from transaction history
    recent_trades = [
        {
            "pair": "SOL/USDC",
            "type": "BUY",
            "price": 215.78,
            "amount": 2.5,
            "time": "13:45:22"
        },
        {
            "pair": "BONK/USDC",
            "type": "SELL",
            "price": 0.00000245,
            "amount": 1000000,
            "time": "13:30:15"
        },
        {
            "pair": "JUP/USDC",
            "type": "BUY",
            "price": 1.73,
            "amount": 100,
            "time": "12:55:30"
        }
    ]
    return jsonify(recent_trades)
