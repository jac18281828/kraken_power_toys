from kraken_request import KrakenRequest

class KrakenOrders(KrakenRequest):

    def query_closed(self, txid):

        if len(txid) > 0:
            param = {'txid': txid}
        else:
            param = {}
        
        return self.query('/0/private/ClosedOrders', param)

    def query_open(self):
        return self.query('/0/private/OpenOrders', {})

    def cancel_order(self, txid):
        return self.query('/0/private/CancelOrder', {'txid': txid})


    
