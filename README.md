# Crypto Project (Python-Project-3)

Lightweight backend + frontend for displaying cryptocurrency lists and charts.


python src/scripts/update_indexed_percent.py

# backend
python src/app.py

# frontend (ayrı terminal)
cd frontend
npm run dev
Quick start
-----------

Prerequisites
- Python 3.10+ and pip
- Node.js (for the frontend) and npm
- MongoDB running locally on default port

Backend
-------
- Install Python deps:

```bash
pip install -r requirements.txt
```

- Start the backend (recommended):

```bash
# Starts Flask server (default)
python src/app.py

# To run legacy analysis/update routine instead of server:
python src/main.py --analyze
```

Important backend scripts (in `src/scripts`):
- `populate_popular.py` — refresh popular coins collection
- `fill_missing_market_data.py` — fetch OHLC market data (Binance) for coins missing data
- `populate_market_data_fast.py` — parallel fetching for popular coins

Frontend
--------
- Install and run:

```bash
cd frontend
npm install
npm run dev
```

API endpoints
-------------
- `GET /api/market-coins` — returns only coins that have market data (used by the market page)
- `GET /api/all-coins` — returns all coins stored (detailed list)
- `GET /api/popular-coins` — popular coins summary
- `GET /api/market/<coin_id>` — historical OHLC/price data for `coin_id` (tries ID, symbol+USDT/BUSD/USDC fallbacks)

Notes
-----
- The frontend market and compare pages now request `/api/market-coins` so only coins with charts are shown.
- Market data is stored in the `market_data` collection; coin details are in `all_coins` and `all_coins_details`.
- If you re-run population scripts multiple times, the database may change; prefer running `fill_missing_market_data.py` once to populate OHLC for missing symbols.

If you want more README details (examples, deployment notes, or how to clean the DB), tell me which section to expand.

