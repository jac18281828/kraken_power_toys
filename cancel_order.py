from kraken_orders import KrakenOrders
import json,sys

if __name__ == '__main__':

    if len(sys.argv) > 2:
        try:
            apikeyfile = sys.argv[1]
            txid = sys.argv[2]
            with open(apikeyfile) as keyfile:
                apikey = json.load(keyfile)
                orders = KrakenOrders(apikey)

                print(orders.cancel_order(txid))

                order_result = orders.query_closed(txid)
                print(json.dumps(order_result, indent=4))

                sys.exit(0)
        except Exception as e:
            print("Failed. "+repr(e))
    else:
        print ('apikey file and txid are required')
        sys.exit(1)
            
