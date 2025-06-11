# SolanaAI Agent Backend

This backend is built with FastAPI and provides API endpoints for authentication, AI agent runs, browser automation, blockchain operations, and payments.

## Structure

- `src/api/` - API routers and services
- `src/agent/` - Core agent logic
- `src/browser/` - Browser automation modules
- `src/blockchain/` - Solana and blockchain integration
- `src/payment/` - Payment protocol integration
- `src/config/` - Configuration and settings
- `src/models/` - Pydantic models and schemas
- `src/utils/` - Utilities (auth, database, etc.)
- `main.py` - FastAPI app entrypoint

## Running the Backend

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Set up your `.env` file with the required environment variables.
3. Start the server:
   ```bash
   uvicorn src.main:app --reload
   ``` 