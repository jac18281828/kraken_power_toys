from kraken_orders import KrakenOrders

import json


try:
    with open('apikey.json') as keyfile:
        apikey = json.load(keyfile)
        order = KrakenOrders(apikey)

        orderinfo = order.query_order('abc')

        print("OrderInfo = %s" % json.dumps(orderinfo, indent=4))
except Exception as e:
    print("Failed. "+str(e))
