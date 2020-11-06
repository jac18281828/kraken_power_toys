#!/usr/bin/env python3

import time, base64, hashlib, hmac, urllib.request, json
import ssl,certifi

with open('apikey.json', 'r') as apikeyfile:
    apimap = json.load(apikeyfile)
    apikey = apimap['key']
    secret = apimap['secret']

    nonce = str(int(time.time()*1000000))
    api_nonce = bytes(nonce, 'utf-8')
    api_request = urllib.request.Request('https://api.kraken.com/0/private/GetWebSocketsToken', b'nonce=%s' % api_nonce)
    api_request.add_header('API-Key', apikey)
    api_request.add_header('API-Sign', base64.b64encode(hmac.new(base64.b64decode(secret), b'/0/private/GetWebSocketsToken' + hashlib.sha256(api_nonce + b'nonce=%s' % api_nonce).digest(), hashlib.sha512).digest()))

    print(json.loads(urllib.request.urlopen(api_request, context=ssl.create_default_context(cafile=certifi.where())).read()))
