import time
import base64
import hashlib
import hmac
import urllib.request
import urllib.parse
import json
import ssl
import certifi

class KrakenRequest:

    API_URL = 'https://api.kraken.com'

    def __init__(self, apikey):
        self.apikey = apikey

    def query(self, endpoint, params):

        apikey = self.apikey['key']
        secret = self.apikey['secret']

        otp = self.apikey['passphrase']

        nonce = str(int(time.time()*1000000))

        kraken_request = {
            'nonce': nonce
        }

        if len(otp) > 0:
            kraken_request['otp'] = otp

        kraken_request.update(params)
            
        post_body = urllib.parse.urlencode(kraken_request)

        api_post = post_body.encode('utf-8')

        hash_block = nonce.encode('utf-8') + api_post

        api_hash256 = hashlib.sha256(hash_block).digest()

        decoded_secret = base64.b64decode(secret)

        api_hmac = hmac.new(decoded_secret, endpoint.encode('utf-8') + api_hash256, hashlib.sha512).digest()
        api_signature = base64.b64encode(api_hmac)

        api_request = urllib.request.Request(self.API_URL + endpoint, data=api_post)
        api_request.add_header('API-Key', apikey)
        api_request.add_header('API-Sign', api_signature)

        with urllib.request.urlopen(api_request, context=ssl.create_default_context(cafile=certifi.where())) as api_call:
            request_result = api_call.read()
            status_code = api_call.getcode()
        
            response_payload=json.loads(request_result)

            if status_code != 200:
                print("Status code: %d" % status_code)
                print("Response: %s" % response_payload)

                if 'error' in response_payload and len(response_payload['error']):
                    print(response_payload)
                    raise RuntimeException('Request failed' + ':'.join(response_payload['error']))

            result = response_payload['result']
            return result

        raise RuntimeException('Request failed')



    def fetch(self, endpoint):
        return self.query(endpoint, {})

        
