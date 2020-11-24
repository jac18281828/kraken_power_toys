from kraken_token import KrakenToken
import json,sys



if __name__ == '__main__':

    if len(sys.argv) > 1:
        try:
            apikeyfile = sys.argv[1]
            with open(apikeyfile) as keyfile:
                apikey = json.load(keyfile)
                token = KrakenToken(apikey)

                token_data = token.fetch_token();

                print("Token = %s" % token_data['token'])
                sys.exit(0)
        except Exception as e:
            print("Failed. "+repr(e))
    else:
        print ('apikey file is required')
        sys.exit(1)
            
