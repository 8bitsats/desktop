"""
Example scripts demonstrating Solana Agent Kit capabilities
Run individual functions to test specific features
"""

import asyncio
import os
from dotenv import load_dotenv
from solana_agent_kit import SolanaAgentKit
from solders.pubkey import Pubkey
from solana_agent_kit.types import PumpfunTokenOptions
from e2b_desktop import Sandbox
import webview
import threading
from multiprocessing import Process, Queue

# Load environment variables
load_dotenv()

# Common token addresses for examples
USDC_MINT = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
SOL_MINT = "So11111111111111111111111111111111111111112"
RAY_MINT = "4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R"

# Window frame height for desktop UI
window_frame_height = 29  # Additional px for window border at the top

async def init_agent():
    """Initialize the Solana Agent"""
    private_key = os.getenv('SOLANA_PRIVATE_KEY')
    rpc_url = os.getenv('SOLANA_RPC_URL', 'https://api.mainnet-beta.solana.com')
    openai_key = os.getenv('OPENAI_API_KEY')
    
    if not private_key:
        raise ValueError("SOLANA_PRIVATE_KEY environment variable required")
    
    agent = SolanaAgentKit(private_key, rpc_url, openai_key)
    print(f"🔗 Connected to wallet: {agent.wallet_address}")
    return agent

async def example_wallet_operations(desktop=None):
    """Example: Basic wallet operations"""
    print("\n📱 WALLET OPERATIONS EXAMPLE")
    print("-" * 40)
    
    agent = await init_agent()
    
    # Get SOL balance
    balance = await agent.get_balance()
    sol_balance = balance / 1e9
    print(f"SOL Balance: {sol_balance:.4f} SOL")
    
    # Get network TPS
    try:
        tps = await agent.get_tps()
        print(f"Network TPS: {tps}")
    except Exception as e:
        print(f"Could not get TPS: {e}")
    
    # Get token data
    try:
        sol_data = await agent.get_token_data_by_ticker("SOL")
        if sol_data:
            print(f"SOL Price: ${sol_data.get('price', 'N/A')}")
            print(f"24h Change: {sol_data.get('price_change_24h', 'N/A')}%")
    except Exception as e:
        print(f"Could not get SOL data: {e}")
    
    # Display in desktop if available
    if desktop:
        desktop.set_clipboard(f"SOL Balance: {sol_balance:.4f}\nPrice: ${sol_data.get('price', 'N/A')}")
        print(" - Balance info copied to clipboard")

async def example_token_swap(desktop=None):
    """Example: Token swapping via Jupiter"""
    print("\n🔄 TOKEN SWAP EXAMPLE")
    print("-" * 40)
    
    agent = await init_agent()
    
    # Example: Swap 0.001 SOL to USDC
    try:
        print("Swapping 0.001 SOL to USDC via Jupiter...")
        
        signature = await agent.trade(
            output_mint=Pubkey.from_string(USDC_MINT),
            input_amount=int(0.001 * 1e9),  # 0.001 SOL in lamports
            input_mint=Pubkey.from_string(SOL_MINT),
            slippage_bps=300  # 3% slippage
        )
        
        print(f"✅ Swap successful! Transaction: {signature}")
        print(f"🔗 View on Solscan: https://solscan.io/tx/{signature}")
        
        # Display in desktop if available
        if desktop:
            solscan_url = f"https://solscan.io/tx/{signature}"
            desktop.set_clipboard(solscan_url)
            print(" - Transaction URL copied to clipboard")
            
    except Exception as e:
        print(f"❌ Swap failed: {e}")
        print("This is normal if you don't have enough SOL or in simulation mode")

async def example_pump_fun_token(desktop=None):
    """Example: Launch token on Pump.fun"""
    print("\n🚀 PUMP.FUN TOKEN EXAMPLE")
    print("-" * 40)
    
    agent = await init_agent()
    
    # Example: Launch a Pump.fun token
    try:
        print("Launching token on Pump.fun...")
        
        options = PumpfunTokenOptions()
        
        response = await agent.launch_pump_fun_token(
            token_name="Test Meme Token",
            token_ticker="TMT",
            description="A test meme token created by AI",
            image_url="https://raw.githubusercontent.com/solana-labs/token-list/main/assets/mainnet/So11111111111111111111111111111111111111112/logo.png",
            options=options
        )
        
        print(f"✅ Pump.fun token launched!")
        print(f"Response: {response}")
        
        # Display in desktop if available
        if desktop and "mint" in response:
            pump_url = f"https://pump.fun/token/{response['mint']}"
            desktop.set_clipboard(pump_url)
            print(" - Token URL copied to clipboard")
            
    except Exception as e:
        print(f"❌ Pump.fun launch failed: {e}")
        print("This requires significant SOL and is high risk")

async def example_market_data(desktop=None):
    """Example: Fetching market data"""
    print("\n📊 MARKET DATA EXAMPLE")
    print("-" * 40)
    
    agent = await init_agent()
    
    # Get data for popular tokens
    tokens = ["SOL", "RAY", "JUP"]
    market_data = []
    
    for ticker in tokens:
        try:
            data = await agent.get_token_data_by_ticker(ticker)
            if data:
                print(f"{ticker}:")
                print(f"  Price: ${data.get('price', 'N/A')}")
                print(f"  24h Change: {data.get('price_change_24h', 'N/A')}%")
                print(f"  Market Cap: ${data.get('market_cap', 'N/A'):,}")
                market_data.append(f"{ticker}: ${data.get('price', 'N/A')} ({data.get('price_change_24h', 'N/A')}%)")
            else:
                print(f"{ticker}: No data available")
        except Exception as e:
            print(f"{ticker}: Error fetching data - {e}")
    
    # Display in desktop if available
    if desktop and market_data:
        desktop.set_clipboard("\n".join(market_data))
        print(" - Market data copied to clipboard")

def create_window(stream_url, width, height, command_queue):
    """Create desktop window for stream"""
    # Thread to check for close command
    def check_queue():
        while True:
            if not command_queue.empty():
                command = command_queue.get()
                if command == 'close':
                    window.destroy()
                    break
            asyncio.sleep(1)  # Check every second

    window = webview.create_window("Solana Agent Desktop", stream_url, width=width, height=height + window_frame_height)

    # Start queue checking in a separate thread
    t = threading.Thread(target=check_queue)
    t.daemon = True
    t.start()

    webview.start()

async def main():
    """Main example runner with desktop integration"""
    examples = {
        1: example_wallet_operations,
        2: example_token_swap,
        3: example_pump_fun_token,
        4: example_market_data
    }
    
    print("🚀 Starting Solana Agent Kit with Desktop Integration")
    print("=" * 50)
    
    # Initialize desktop sandbox
    print("\n> Starting desktop sandbox...")
    desktop = Sandbox()
    print(" - Desktop Sandbox started, ID:", desktop.sandbox_id)
    
    # Get screen dimensions
    width, height = desktop.get_screen_size()
    print(" - Desktop screen size:", width, height)
    
    # Start stream
    print("\n> Starting desktop stream...")
    desktop.stream.start(require_auth=True)
    auth_key = desktop.stream.get_auth_key()
    stream_url = desktop.stream.get_url(auth_key=auth_key)
    print(" - Stream URL:", stream_url)
    
    # Create desktop window in separate process
    command_queue = Queue()
    webview_process = Process(target=create_window, args=(stream_url, width, height, command_queue))
    webview_process.start()
    
    # Wait for stream to initialize
    print("\n> Waiting 5 seconds for the stream to start...")
    for i in range(5, 0, -1):
        print(f" - {i} seconds remaining...")
        await asyncio.sleep(1)
    
    # Display examples menu and run selected examples
    while True:
        print("\n🎯 SOLANA AGENT KIT EXAMPLES")
        print("=" * 50)
        print("1. Wallet Operations")
        print("2. Token Swapping")
        print("3. Pump.fun Token Launch")
        print("4. Market Data")
        print("5. Run All Examples")
        print("0. Exit")
        
        try:
            choice = int(input("\nEnter your choice (0-5): "))
            
            if choice == 0:
                print("👋 Goodbye!")
                break
            elif choice == 5:
                print("\n🏃 Running all examples...")
                for i in range(1, 5):
                    try:
                        await examples[i](desktop)
                    except Exception as e:
                        print(f"Example {i} failed: {e}")
                    await asyncio.sleep(1)
            elif choice in examples:
                await examples[choice](desktop)
            else:
                print("❌ Invalid choice. Please try again.")
                
        except ValueError:
            print("❌ Please enter a valid number.")
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
        
        input("\nPress Enter to continue...")
    
    # Clean up resources
    print("\n> Stopping desktop stream...")
    desktop.stream.stop()
    print(" - Desktop stream stopped")
    
    print("\n> Closing webview...")
    command_queue.put('close')
    webview_process.join()
    print(" - Webview closed")
    
    print("\n> Killing desktop sandbox...")
    desktop.kill()
    print(" - Desktop sandbox killed")

if __name__ == "__main__":
    asyncio.run(main())
