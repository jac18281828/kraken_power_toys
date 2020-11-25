import asyncio
import websockets
import json
import sys
import time
import traceback
import ssl
import certifi
import math
import zlib
from kraken_token import KrakenToken
from pricelistener import PriceListener

class KrakenBookWss:

    WS_URL = 'wss://ws.kraken.com'
    #WS_URL = 'ws://localhost:8777'

    PRODUCT_ID='XBT/USD'
    DEPTH=10

    is_running = True

    def __init__(self):
        self.update_time = 0
        self.requestId = 1
        self.bids = {}
        self.asks = {}
        self.pricelistener = PriceListener()

    async def send_json(self, websocket, event):
        event_payload = json.dumps(event)
        print(event_payload)
        await websocket.send(event_payload)

    async def ping(self, websocket):
        event = {'event': 'ping', 'reqid': self.requestId}
        self.requestId = self.requestId + 1
        self.update_time = time.time()
        await self.send_json(websocket, event)
        await asyncio.sleep(1)        

    async def on_subscription(self, websocket, event):
        print(event)

    def on_entry_update(self, entry, message):
        for level in message:
            price = float(level[0])
            qty   = float(level[1])

            if math.isclose(qty, 0.0):
                if level[0] in entry:
                    del entry[level[0]]
            else:
                entry[level[0]] = level[:3]

            self.prune_levels()
                

    def format_entry(self, entry):
        return entry.replace('.', '').lstrip('0')


    def checksum_block(self):
        SUM_DEPTH = 10

        best_asks = sorted(self.asks.items(), reverse=False, key=lambda level: float(level[0]))[:SUM_DEPTH]

        ask_entry = [ self.format_entry(str(level[0])) + self.format_entry(str(level[1])) for price,level in best_asks ]

        asks = ''.join(ask_entry)

        best_bids = sorted(self.bids.items(), reverse=True, key=lambda level: float(level[0]))[:SUM_DEPTH]

        bid_entry = [ self.format_entry(str(level[0])) + self.format_entry(str(level[1])) for price,level in best_bids ]

        bids = ''.join(bid_entry)

        return asks + bids
        

    def book_checksum(self):

        crc_block = self.checksum_block()

        kraken_crc32 = zlib.crc32(crc_block.encode('utf-8'))

        return kraken_crc32


    def on_book_update(self, payload):

        crc_32 = 0
        
        for event, message in payload.items():
            if 'as' == event:
                self.asks = {}
            if 'as' == event or 'a' == event:
                self.on_entry_update(self.asks, message)
            if 'bs' == event:
                self.bids = {}
            if 'bs' == event or 'b' == event:
                self.on_entry_update(self.bids, message)
            if 'c' == event:
                crc_32 = int(message)
                

        if crc_32 != 0:
            book_crc = self.book_checksum()
            if crc_32 != book_crc:
                self.is_running = False
                print('Payload = %s' % payload)
                print('Checksum failure %d, expected %d' % (book_crc, crc_32))

        if self.is_running:
            self.on_price_update()
            



    def on_price_update(self):

        print('\t\tbest asks')
        best_offers = sorted(self.asks.items(), reverse=True, key=lambda level: float(level[0]))
        best_offers = [k[1] for k in best_offers[:5]]
        for level in best_offers:
            print ('\t\t%s' % str(level))                                

        best_bids = sorted(self.bids.items(), reverse=True, key=lambda level: float(level[0]))
        best_bids = [k[1] for k in best_bids[:5]]
        for level in best_bids:
            print (level)

        print('best bids')

        best_offers = [[k[0], k[1]] for k in best_offers]
        best_bids = [[k[0], k[1]] for k in best_bids]

        best_bid = best_bids[0]
        best_offer = best_offers[-1]

        print('bb=%s, bo=%s' % (best_bid, best_offer))

        if float(best_bid[0]) >= float(best_offer[0]):
            print('CROSSING!  This can not be correct!')
            self.is_running = False

        self.pricelistener.on_price_update(best_bids, best_offers)

        if self.pricelistener.get_theo() > float(best_offer[0]):
            print('Theo is a SELLER, quantity = %0.2f' % float(best_offer[1]))
        else:
            if self.pricelistener.get_theo() < float(best_bid[0]):
                print('Theo is a BUYER, quantity = %0.2f' % float(best_bid[1]))

        print('')
        print('')
        print('')


    def prune_levels(self):
        if len(self.asks) > self.DEPTH+1:
            worst_asks = sorted(self.asks, reverse=False, key=lambda level: float(level))
            worst_asks = worst_asks[self.DEPTH:]
            for a in worst_asks:
                del self.asks[a]

        if len(self.bids) > self.DEPTH+1:
            worst_bids = sorted(self.bids, reverse=True, key=lambda level: float(level))
            worst_bids = worst_bids[self.DEPTH:]
            for b in worst_bids:
                del self.bids[b]

                    
    async def on_message(self, websocket, message):
        self.update_time = time.time()
        event_message = json.loads(message)
        
        if type(event_message) == list:
            for payload in event_message:
                if type(payload) == dict:
                    self.on_book_update(payload)

        else:

            if 'pong' == event_message['event'] or 'heartbeat' == event_message['event']:
                print (message)
                return

            if 'systemStatus' == event_message['event']:
                print (message)
                return
        
            if 'subscriptionStatus' == event_message['event']:
                await self.on_subscription(websocket, event_message)
                return
        
            print ('unknown event: %s' % event_message['event'])

    async def send_subscription(self, websocket, name):
        event = {
            'event': 'subscribe',
            'reqid': self.requestId,
            'pair': [self.PRODUCT_ID],
        }
        self.requestId = self.requestId + 1
        subscription = {
            'name':name,
            'depth':self.DEPTH
        }
        event['subscription'] = subscription
        await self.send_json(websocket, event)

    async def on_open(self, websocket):
        await self.send_subscription(websocket, 'book')
        
    async def heartbeat(self, websocket):
        now = time.time()
        timedelta = now - self.update_time
        if timedelta > 10:
            print('Idle: sending ping')
            await self.ping(websocket)
        else:
            await asyncio.sleep(1 - timedelta)

    async def receive_message(self, websocket):
        async for message in websocket:
            await self.on_message(websocket, message)

    def on_error(self, err):
        print('Error in websocket connection: {}'.format(err))
        print(traceback.format_exc(err))
        sys.exit(1)

    async def run_event_loop(self):
        try:

            async with websockets.connect(self.WS_URL,ssl=ssl.create_default_context(cafile=certifi.where())) as websocket:
                await self.on_open(websocket)

                while self.is_running:

                    tasks = [
                        asyncio.ensure_future(self.heartbeat(websocket)),
                        asyncio.ensure_future(self.receive_message(websocket))
                    ]

                    done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)

                    for task in pending:
                        task.cancel()
                    
        except Exception as e:
            self.on_error(e)

if __name__ == '__main__':

    try:
        kwss = KrakenBookWss()
        asioloop = asyncio.get_event_loop()
        asioloop.run_until_complete(kwss.run_event_loop())
    except Exception as e:
        print('Error: %s' % repr(e))
        sys.exit(1)
    finally:
        asioloop.close()
        sys.exit(0)
        
