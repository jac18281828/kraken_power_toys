import time
from kraken_request import KrakenRequest

class KrakenToken(KrakenRequest):

    def fetch_token(self):
        return self.fetch('/0/private/GetWebSocketsToken')
    
