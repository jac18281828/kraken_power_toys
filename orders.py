from kraken_orders import KrakenOrders

import json

if __name__ == '__main__':

    try:
        with open('apikey.json') as keyfile:
            apikey = json.load(keyfile)
            order = KrakenOrders(apikey)

            orderinfo = order.query_order('abc')

            print("OrderInfo = %s" % json.dumps(orderinfo, indent=4))
            sys.exit(0)
    except Exception as e:
        print("Failed. "+str(e))
        sys.exit(1)
