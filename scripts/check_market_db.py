import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from db import database_manager as db

def safe_print(title, obj):
    print(f"--- {title} ---")
    try:
        print(obj)
    except Exception as e:
        print('Error printing:', e)

try:
    client = db.client
    coll = client['crypto_project_db']['market_data']
    details = client['crypto_project_db']['all_coins_details']

    safe_print('market_data count', coll.count_documents({}))
    distinct_ids = coll.distinct('coin_id')
    safe_print('distinct coin_ids (first 50)', distinct_ids[:50])

    sample = list(coll.find({}, {'_id': 0}).limit(5))
    safe_print('market_data sample (up to 5)', sample)

    safe_print('all_coins_details count', details.count_documents({}))
    sample_details = list(details.find({}, {'_id': 0}).limit(5))
    safe_print('all_coins_details sample (up to 5)', sample_details)

    from db.database_manager import get_market_data
    df = get_market_data('bitcoin')
    safe_print("get_market_data('bitcoin') empty?", df.empty)
    if not df.empty:
        safe_print("get_market_data('bitcoin') rows", len(df))
        safe_print("first row", df.iloc[0].to_dict())

except Exception as e:
    print('Diagnostic script failed:', e)
    import traceback
    traceback.print_exc()
