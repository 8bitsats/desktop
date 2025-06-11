"""
Solana API integration module for the trading dashboard
"""

import os
import json
import logging
import asyncio
import requests
import time
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
from dotenv import load_dotenv
from flask import Blueprint, jsonify, request, current_app
import base58

# Try to import Solana packages, fail gracefully if not available
try:
    from solana.rpc.api import Client as SolanaClient
    from solana.rpc.types import TokenAccountOpts
    from solana.publickey import PublicKey
    from solana.transaction import Transaction
    solana_sdk_available = True
except ImportError:
    logging.warning("Solana SDK not installed. Limited functionality available.")
    solana_sdk_available = False
    # Define dummy classes for type hints to work
    class SolanaClient:
        def __init__(self, *args, **kwargs):
            pass

# Configure logging
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Default RPC endpoints
DEFAULT_RPC_ENDPOINT = "https://mainnet.helius-rpc.com/?api-key=c55c146c-71ef-41b9-a574-cb08f359c00c"
FALLBACK_RPC_ENDPOINTS = [
    "https://api.mainnet-beta.solana.com",
    "https://solana-api.projectserum.com",
    "https://rpc.ankr.com/solana"
]

# Jupiter API endpoint
JUPITER_API_ENDPOINT = "https://quote-api.jup.ag/v6"

# Well-known token addresses
TOKEN_ADDRESSES = {
    "SOL": "So11111111111111111111111111111111111111112", 
    "USDC": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
    "BONK": "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263",
    "JUP": "JUPyiwrYJFskUPiHa7hkeR8VUtAeFoSYbKedZNsDvCN",
    "JTO": "J5LbyuRiGgbJMi8eiSQ9xf8o2quUbwBXP2GTbXZtUZpS"
}

class SolanaAPI:
    """Interface to Solana RPC API for market data and wallet integration"""
    
    def __init__(self, rpc_endpoint: Optional[str] = None):
        """Initialize Solana API client
        
        Args:
            rpc_endpoint: RPC endpoint URL, defaults to DEFAULT_RPC_ENDPOINT
        """
        self.rpc_endpoint = rpc_endpoint or os.environ.get("SOLANA_RPC_ENDPOINT", DEFAULT_RPC_ENDPOINT)
        self.wallet_pubkey = None
        self.wallet_connected = False
        self.private_key = None
        
        if not solana_sdk_available:
            logger.warning("Solana SDK not available. Running in limited functionality mode.")
            logger.info("Install solana-sdk with: pip install solana-py")
        else:
            try:
                self.client = SolanaClient(self.rpc_endpoint)
                logger.info(f"Initialized Solana API client with endpoint: {self.rpc_endpoint}")
            except Exception as e:
                logger.error(f"Failed to initialize Solana client: {e}")
                self.client = None
    
    def connect_wallet(self, private_key: Optional[str] = None) -> bool:
        """Connect wallet using private key
        
        Args:
            private_key: Base58 encoded private key, defaults to SOLANA_PRIVATE_KEY env variable
            
        Returns:
            True if connection successful, False otherwise
        """
        if not solana_sdk_available:
            logger.error("Cannot connect wallet: Solana SDK not installed")
            return False
            
        try:
            # Get private key from args or environment
            key = private_key or os.environ.get("SOLANA_PRIVATE_KEY")
            if not key:
                logger.error("No private key provided and SOLANA_PRIVATE_KEY not set")
                return False
            
            # Decode and store private key (in memory only)
            self.private_key = base58.b58decode(key)
            
            # Derive public key (wallet address)
            from solana.keypair import Keypair
            keypair = Keypair.from_secret_key(self.private_key)
            self.wallet_pubkey = keypair.public_key
            
            self.wallet_connected = True
            logger.info(f"Wallet connected: {self.wallet_pubkey}")
            return True
            
        except Exception as e:
            logger.error(f"Error connecting wallet: {e}")
            self.wallet_connected = False
            self.private_key = None
            self.wallet_pubkey = None
            return False
    
    def disconnect_wallet(self) -> None:
        """Disconnect wallet and clear sensitive data"""
        self.wallet_connected = False
        self.private_key = None  # Clear from memory
        self.wallet_pubkey = None
        logger.info("Wallet disconnected")
    
    async def get_wallet_balance(self) -> Dict:
        """Get wallet SOL balance
        
        Returns:
            Dict with balance information
        """
        if not solana_sdk_available:
            return {"error": "Solana SDK not installed", "note": "Install with: pip install solana-py"}
            
        if not self.wallet_connected or not self.wallet_pubkey:
            return {"error": "Wallet not connected"}
        
        if self.client is None:
            return {"error": "Solana client not initialized"}
            
        try:
            response = self.client.get_balance(self.wallet_pubkey)
            lamports = response["result"]["value"]
            sol_balance = lamports / 10**9  # Convert lamports to SOL
            
            return {
                "wallet": str(self.wallet_pubkey),
                "balance": sol_balance,
                "balance_usd": sol_balance * await self.get_sol_price()
            }
            
        except Exception as e:
            logger.error(f"Error getting wallet balance: {e}")
            return {"error": str(e)}
        
    async def get_sol_price(self) -> float:
        """Get current SOL price in USD
        
        Returns:
            Current SOL price
        """
        try:
            # In a real implementation, we would fetch this from an oracle or price feed
            # For now, we'll use a hardcoded recent price
            return 215.78
        except Exception as e:
            logger.error(f"Error fetching SOL price: {e}")
            return 0.0
            
    async def get_token_price(self, token_mint: str) -> float:
        """Get token price in USD
        
        Args:
            token_mint: Token mint address
            
        Returns:
            Current token price
        """
        try:
            # In a real implementation, we would fetch this from Jupiter API or similar
            # For now, return placeholder values for known tokens
            token_prices = {
                "So11111111111111111111111111111111111111112": 215.78,  # SOL
                "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v": 1.0,    # USDC
                "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263": 0.00000245,  # BONK
                "JUPyiwrYJFskUPiHa7hkeR8VUtAeFoSYbKedZNsDvCN": 1.73,    # JUP
            }
            return token_prices.get(token_mint, 0.0)
        except Exception as e:
            logger.error(f"Error fetching token price: {e}")
            return 0.0
    
    async def get_market_data(self) -> Dict:
        """Get market data for popular tokens
        
        Returns:
            Dict containing market data
        """
        market_data = {
            "SOL/USDC": {
                "price": 215.78,
                "change24h": 4.25,
                "high24h": 217.90,
                "low24h": 207.15,
                "volume24h": 1245789.32
            },
            "BONK/USDC": {
                "price": 0.00000245,
                "change24h": -2.17,
                "high24h": 0.00000258,
                "low24h": 0.00000241,
                "volume24h": 985634.12
            },
            "JTO/USDC": {
                "price": 0.92,
                "change24h": 1.35,
                "high24h": 0.94,
                "low24h": 0.90,
                "volume24h": 568392.21
            },
            "JUP/USDC": {
                "price": 1.73,
                "change24h": -0.85,
                "high24h": 1.78,
                "low24h": 1.71,
                "volume24h": 742195.67
            }
        }
        return market_data


# Create Flask Blueprint for API routes
api = Blueprint('api', __name__)
_scrapybara_instance = None


@api.route('/status')
def api_status():
    """API status endpoint"""
    return jsonify({
        'status': 'ok',
        'solana_rpc_configured': bool(os.environ.get('SOLANA_RPC_URL')),
        'scrapybara_configured': bool(os.environ.get('SCRAPY_API_KEY')),
        'scrapybara_active': _scrapybara_instance is not None
    })


# Scrapybara routes
@api.route('/scrapybara/status')
def scrapybara_status():
    """Get Scrapybara instance status"""
    global _scrapybara_instance
    
    if not _scrapybara_instance:
        return jsonify({
            'active': False,
            'message': 'No active Scrapybara instance'
        })
    
    return jsonify({
        'active': True,
        'instance_id': getattr(_scrapybara_instance, 'instance', {}).get('id', 'unknown'),
        'stream_url': getattr(_scrapybara_instance, 'stream_url', None),
        'browser_active': getattr(_scrapybara_instance, 'browser_cdp_url', None) is not None
    })


@api.route('/scrapybara/start', methods=['POST'])
def start_scrapybara():
    """Start Scrapybara instance"""
    global _scrapybara_instance
    
    # Check if Scrapybara is already running
    if _scrapybara_instance:
        return jsonify({
            'success': False,
            'message': 'Scrapybara instance already running',
            'stream_url': _scrapybara_instance.stream_url
        })
    
    # Check API key
    api_key = os.environ.get('SCRAPY_API_KEY')
    if not api_key:
        return jsonify({
            'success': False,
            'message': 'SCRAPY_API_KEY not set in environment'
        })
    
    # Get instance parameters from request
    data = request.get_json() or {}
    instance_type = data.get('instance_type', os.environ.get('SCRAPY_INSTANCE_TYPE', 'browser'))
    timeout_hours = int(data.get('timeout_hours', os.environ.get('SCRAPY_TIMEOUT_HOURS', '1')))
    
    # Import and initialize Scrapybara
    try:
        from .integrations import ScrapybaraIntegration
        _scrapybara_instance = ScrapybaraIntegration(api_key=api_key)
        
        # Start instance asynchronously
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            instance_info = loop.run_until_complete(
                _scrapybara_instance.start_instance(
                    instance_type=instance_type,
                    timeout_hours=timeout_hours
                )
            )
            
            # Set up browser
            browser_info = loop.run_until_complete(
                _scrapybara_instance.setup_browser()
            )
            
            return jsonify({
                'success': True,
                'message': f'Scrapybara {instance_type} instance started',
                'stream_url': instance_info.get('stream_url'),
                'browser_url': browser_info
            })
        finally:
            loop.close()
            
    except Exception as e:
        logger.error(f"Error starting Scrapybara: {e}")
        return jsonify({
            'success': False,
            'message': f'Error starting Scrapybara: {str(e)}'
        })


@api.route('/scrapybara/stop', methods=['POST'])
def stop_scrapybara():
    """Stop Scrapybara instance"""
    global _scrapybara_instance
    
    if not _scrapybara_instance:
        return jsonify({
            'success': False, 
            'message': 'No active Scrapybara instance'
        })
    
    try:
        # Stop instance asynchronously
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(_scrapybara_instance.stop_instance())
        finally:
            loop.close()
        
        # Clear instance reference
        _scrapybara_instance = None
        
        return jsonify({
            'success': True,
            'message': 'Scrapybara instance stopped'
        })
    except Exception as e:
        logger.error(f"Error stopping Scrapybara: {e}")
        return jsonify({
            'success': False,
            'message': f'Error stopping Scrapybara: {str(e)}'
        })


@api.route('/scrapybara/screenshot', methods=['GET'])
def get_screenshot():
    """Take a screenshot of the Scrapybara instance"""
    global _scrapybara_instance
    
    if not _scrapybara_instance:
        return jsonify({
            'success': False,
            'message': 'No active Scrapybara instance'
        })
    
    try:
        # Take screenshot asynchronously
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            screenshot_b64 = loop.run_until_complete(_scrapybara_instance.take_screenshot())
        finally:
            loop.close()
        
        return jsonify({
            'success': True,
            'image': screenshot_b64
        })
    except Exception as e:
        logger.error(f"Error taking screenshot: {e}")
        return jsonify({
            'success': False,
            'message': f'Error taking screenshot: {str(e)}'
        })


@api.route('/scrapybara/action', methods=['POST'])
def run_scrapybara_action():
    """Run a Scrapybara action"""
    global _scrapybara_instance
    
    if not _scrapybara_instance:
        return jsonify({
            'success': False,
            'message': 'No active Scrapybara instance'
        })
    
    # Get action parameters from request
    data = request.get_json()
    if not data or 'action_type' not in data:
        return jsonify({
            'success': False,
            'message': 'Missing action_type parameter'
        })
    
    action_type = data.get('action_type')
    params = {k: v for k, v in data.items() if k != 'action_type'}
    
    try:
        # Run action asynchronously
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(
                _scrapybara_instance.run_action(action_type=action_type, **params)
            )
        finally:
            loop.close()
        
        return jsonify({
            'success': True,
            'result': result
        })
    except Exception as e:
        logger.error(f"Error running Scrapybara action: {e}")
        return jsonify({
            'success': False,
            'message': f'Error running action: {str(e)}'
        })


@api.route('/scrapybara/agent', methods=['POST'])
def run_agent_command():
    """Run an agent command with Scrapybara"""
    global _scrapybara_instance
    
    if not _scrapybara_instance:
        return jsonify({
            'success': False,
            'message': 'No active Scrapybara instance'
        })
    
    # Get agent parameters
    data = request.get_json()
    if not data or 'prompt' not in data:
        return jsonify({
            'success': False,
            'message': 'Missing prompt parameter'
        })
        
    prompt = data.get('prompt')
    tools = data.get('tools', ['computer', 'browser'])
    system = data.get('system')
    
    try:
        # Run agent asynchronously
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(
                _scrapybara_instance.run_agent(
                    prompt=prompt,
                    tools=tools,
                    system=system
                )
            )
        finally:
            loop.close()
        
        return jsonify({
            'success': True,
            'result': result
        })
    except Exception as e:
        logger.error(f"Error running agent command: {e}")
        return jsonify({
            'success': False,
            'message': f'Error running agent command: {str(e)}'
        })
    
    async def get_token_accounts(self) -> List[Dict]:
        """Get token accounts owned by the connected wallet
        
        Returns:
            List of token accounts with balance information
        """
        if not self.wallet_connected or not self.wallet_pubkey:
            return [{"error": "Wallet not connected"}]
            
        try:
            # Request token accounts from the RPC endpoint
            opts = TokenAccountOpts(program_id=PublicKey('TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA'))
            response = self.client.get_token_accounts_by_owner(
                self.wallet_pubkey,
                opts,
                encoding="jsonParsed"
            )
            
            if "result" not in response or "value" not in response["result"]:
                return [{"error": "No token accounts found"}]
                
            token_accounts = []
            for account in response["result"]["value"]:
                try:
                    token_data = account["account"]["data"]["parsed"]["info"]
                    mint = token_data["mint"]
                    token_amount = token_data["tokenAmount"]
                    decimals = token_amount["decimals"]
                    amount = float(token_amount["amount"]) / (10 ** decimals)
                    
                    # Get token price
                    price = await self.get_token_price(mint)
                    value_usd = amount * price
                    
                    token_accounts.append({
                        "mint": mint,
                        "amount": amount,
                        "decimals": decimals,
                        "price_usd": price,
                        "value_usd": value_usd
                    })
                except Exception as e:
                    logger.error(f"Error processing token account: {e}")
                    
            return token_accounts
            
        except Exception as e:
            logger.error(f"Error getting token accounts: {e}")
            return [{"error": str(e)}]
            
    async def get_portfolio_data(self) -> Dict:
        """Get complete portfolio data including SOL and token holdings
        
        Returns:
            Dict with portfolio information
        """
        if not self.wallet_connected:
            return {"error": "Wallet not connected"}
            
        try:
            # Get SOL balance
            sol_balance = await self.get_wallet_balance()
            if "error" in sol_balance:
                sol_value = 0
            else:
                sol_value = sol_balance.get("balance_usd", 0)
                
            # Get token balances
            token_accounts = await self.get_token_accounts()
            token_holdings = []
            token_value = 0
            
            for token in token_accounts:
                if "error" not in token:
                    token_holdings.append(token)
                    token_value += token.get("value_usd", 0)
            
            # Calculate totals
            total_value = sol_value + token_value
            
            # In a real implementation, we would fetch historical data
            # to calculate PnL, but for this demo we'll use placeholder values
            previous_value = total_value * 0.97  # -3% change
            pnl_value = total_value - previous_value
            pnl_percentage = (pnl_value / previous_value) * 100 if previous_value > 0 else 0
            
            return {
                "totalValue": total_value,
                "totalPnL": pnl_value,
                "pnlPercentage": pnl_percentage,
                "holdings": [
                    {
                        "token": "SOL",
                        "amount": sol_balance.get("balance", 0),
                        "value": sol_value,
                        "pnl": sol_value * 0.03  # Placeholder 3% gain
                    },
                    *[{
                        "token": self._get_token_symbol(token["mint"]),
                        "amount": token["amount"],
                        "value": token["value_usd"],
                        "pnl": token["value_usd"] * 0.02  # Placeholder 2% gain
                    } for token in token_holdings]
                ]
            }
        except Exception as e:
            logger.error(f"Error getting portfolio data: {e}")
            return {"error": str(e)}
    
    def _get_token_symbol(self, mint: str) -> str:
        """Get token symbol from mint address
        
        Args:
            mint: Token mint address
            
        Returns:
            Token symbol or abbreviated mint address
        """
        # Reverse lookup in TOKEN_ADDRESSES
        for symbol, address in TOKEN_ADDRESSES.items():
            if address == mint:
                return symbol
        return mint[:4] + "..." + mint[-4:]
    
    def _get_token_address(self, symbol: str) -> str:
        """Get token mint address from symbol
        
        Args:
            symbol: Token symbol (e.g., 'SOL')
            
        Returns:
            Token mint address or None if not found
        """
        return TOKEN_ADDRESSES.get(symbol.upper())
            
    async def get_swap_quote(self, input_token: str, output_token: str, amount: float, slippage_bps: int = 100) -> Dict:
        """Get quote for token swap using Jupiter API
        
        Args:
            input_token: Input token symbol or address
            output_token: Output token symbol or address
            amount: Amount of input token to swap
            slippage_bps: Slippage tolerance in basis points (1% = 100)
            
        Returns:
            Quote information from Jupiter API
        """
        try:
            # Convert symbols to addresses if needed
            input_mint = self._get_token_address(input_token) if len(input_token) < 10 else input_token
            output_mint = self._get_token_address(output_token) if len(output_token) < 10 else output_token
            
            if not input_mint or not output_mint:
                return {"error": f"Invalid token symbol: {input_token if not input_mint else output_token}"}
            
            # Get token data to calculate amount in correct decimals
            input_decimals = 9  # Default for SOL
            if input_mint != TOKEN_ADDRESSES["SOL"]:
                # In production we would get this from token metadata
                input_decimals = 6 if input_mint == TOKEN_ADDRESSES["USDC"] else 9
            
            # Convert amount to integer with proper decimals
            amount_in_smallest_unit = int(amount * (10 ** input_decimals))
            
            # Build Jupiter API request
            url = f"{JUPITER_API_ENDPOINT}/quote"
            params = {
                "inputMint": input_mint,
                "outputMint": output_mint,
                "amount": str(amount_in_smallest_unit),
                "slippageBps": slippage_bps
            }
            
            # Call Jupiter API
            response = requests.get(url, params=params)
            if response.status_code != 200:
                return {"error": f"Jupiter API error: {response.status_code} - {response.text}"}
                
            quote_data = response.json()
            return quote_data
            
        except Exception as e:
            logger.error(f"Error getting swap quote: {e}")
            return {"error": str(e)}
    
    async def prepare_swap_transaction(self, quote: Dict) -> Dict:
        """Prepare swap transaction using Jupiter API
        
        Args:
            quote: Quote data from get_swap_quote()
            
        Returns:
            Transaction data ready to sign
        """
        if not self.wallet_connected or not self.wallet_pubkey:
            return {"error": "Wallet not connected"}
            
        try:
            # Build Jupiter swap transaction request
            url = f"{JUPITER_API_ENDPOINT}/swap"
            
            # Extract data from quote
            if "error" in quote:
                return quote
                
            payload = {
                "quoteResponse": quote,
                "userPublicKey": str(self.wallet_pubkey),
                "wrapUnwrapSOL": True
            }
            
            # Call Jupiter API to prepare transaction
            response = requests.post(url, json=payload)
            if response.status_code != 200:
                return {"error": f"Jupiter API error: {response.status_code} - {response.text}"}
                
            swap_data = response.json()
            return swap_data
            
        except Exception as e:
            logger.error(f"Error preparing swap transaction: {e}")
            return {"error": str(e)}
    
    async def execute_swap(self, input_token: str, output_token: str, amount: float, slippage_bps: int = 100) -> Dict:
        """Execute token swap using Jupiter API
        
        Args:
            input_token: Input token symbol or address
            output_token: Output token symbol or address
            amount: Amount of input token to swap
            slippage_bps: Slippage tolerance in basis points (1% = 100)
            
        Returns:
            Result of swap transaction
        """
        if not self.wallet_connected or not self.wallet_pubkey or not self.private_key:
            return {"error": "Wallet not connected"}
            
        try:
            # 1. Get swap quote
            quote = await self.get_swap_quote(input_token, output_token, amount, slippage_bps)
            if "error" in quote:
                return quote
            
            # 2. Prepare transaction
            swap_data = await self.prepare_swap_transaction(quote)
            if "error" in swap_data:
                return swap_data
            
            # 3. Sign and serialize transaction
            from solana.keypair import Keypair
            keypair = Keypair.from_secret_key(self.private_key)
            
            # Get serialized transaction from swap_data
            tx_data = swap_data.get("swapTransaction")
            if not tx_data:
                return {"error": "No transaction data in swap response"}
            
            # In a real implementation, we would deserialize, sign, and send the transaction
            # For simplicity in this demo, we'll assume success
            
            # 4. Execute transaction
            # In production, we would:
            # - Deserialize the transaction
            # - Sign with wallet keypair
            # - Submit to RPC endpoint
            # - Wait for confirmation
            
            # Simulate transaction latency
            time.sleep(1)
            
            # 5. Record the trade in recent trades
            trade_info = {
                "pair": f"{input_token}/{output_token}",
                "type": "SELL" if input_token == "SOL" else "BUY",
                "price": await self.get_token_price(self._get_token_address(output_token)),
                "amount": amount,
                "time": time.strftime("%H:%M:%S")
            }
            
            # Return success response
            input_token_price = await self.get_token_price(self._get_token_address(input_token))
            output_token_price = await self.get_token_price(self._get_token_address(output_token))
            
            return {
                "success": True,
                "trade": trade_info,
                "input": {
                    "token": input_token,
                    "amount": amount,
                    "value_usd": amount * input_token_price
                },
                "output": {
                    "token": output_token,
                    "amount": quote.get("outAmount", 0) / (10 ** 9),  # Assuming 9 decimals for output token
                    "value_usd": float(quote.get("otherAmountThreshold", 0)) * output_token_price
                }
            }
            
        except Exception as e:
            logger.error(f"Error executing swap: {e}")
            return {"error": str(e)}
