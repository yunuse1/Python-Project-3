import requests
try:
    r = requests.get('http://127.0.0.1:5000/api/market/bitcoin', timeout=5)
    print('STATUS', r.status_code)
    text = r.text
    print('LEN', len(text))
    print(text[:2000])
except Exception as e:
    print('ERROR', e)
