from kraken_orders import KrakenOrders
import json,sys

if __name__ == '__main__':

    if len(sys.argv) > 1:
        try:
            apikeyfile = sys.argv[1]
            with open(apikeyfile) as keyfile:
                apikey = json.load(keyfile)
                orders = KrakenOrders(apikey)

                order_result = orders.query_closed('')
                print(json.dumps(order_result, indent=4))

                order_result = orders.query_open()
                print(json.dumps(order_result, indent=4))
                sys.exit(0)
        except Exception as e:
            print("Failed. "+repr(e))
    else:
        print ('apikey file is required')
        sys.exit(1)
            
