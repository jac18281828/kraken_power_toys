from kraken_request import KrakenRequest

class KrakenOrders(KrakenRequest):

    def query_order(self, ):
        return self.query('/0/private/ClosedOrders', {})

