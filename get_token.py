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
        except Exception as e:
            print("Failed. "+str(e))
    else:
        print ('apikeyfile is required')
        sys.exit(1)
            
