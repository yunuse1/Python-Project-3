#!/bin/sh
set -e

echo "=============================================="
echo "Starting initial data population..."
echo "=============================================="

echo ""
echo "1) Populating coin list and OHLC market data"
echo "   (This pulls 90 days of data for ~100 coins)"
python src/scripts/populate_market_data_fast.py

echo ""
echo "2) Generating Seaborn visualizations"
python analysis/seaborn_analysis.py

echo ""
echo "=============================================="
echo "Initial data population complete!"
echo "=============================================="

exit 0
