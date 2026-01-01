#!/bin/sh
set -e

echo "Starting initial data population..."

echo "1) Populating all_coins and all_coins_details"
python src/scripts/populate_all_coins.py

echo "2) Populating market data (fast)"
python src/scripts/populate_market_data_fast.py

echo "3) Filling missing market data"
python src/scripts/fill_missing_market_data.py

echo "Initial data population complete."

exit 0
