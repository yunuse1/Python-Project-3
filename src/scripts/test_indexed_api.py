import requests, json
URL = 'http://127.0.0.1:5000/api/market/indexed?coins=bitcoin,ethereum'
try:
    r = requests.get(URL, timeout=10)
    print('STATUS', r.status_code)
    print('CONTENT-TYPE', r.headers.get('Content-Type'))
    txt = r.text
    print('PREVIEW\n', txt[:2000])
    try:
        data = json.loads(txt)
        print('PARSE_OK; coins=', list(data.get('coins', {}).keys()))
    except Exception as e:
        print('PARSE_ERROR', e)
except Exception as e:
    print('REQUEST_ERROR', e)
