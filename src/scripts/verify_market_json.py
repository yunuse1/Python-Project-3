import requests
import json

URL = 'http://127.0.0.1:5000/api/market/bitcoin'
try:
    r = requests.get(URL, timeout=10)
    print('STATUS', r.status_code)
    print('CONTENT-TYPE', r.headers.get('Content-Type'))
    txt = r.text
    print('PREVIEW:\n', txt[:2000])
    try:
        data = json.loads(txt)
        print('JSON_PARSE_OK; items =', len(data) if isinstance(data, list) else 'not-list')
    except Exception as e:
        print('JSON_PARSE_ERROR', e)
except Exception as e:
    print('REQUEST_ERROR', e)
