import asyncio
import websockets
import json
import sys
import time
import traceback
import ssl
import certifi
import math
from kraken_token import KrakenToken

class KrakenWss:

    WS_URL = 'wss://ws.kraken.com'
    #WS_URL = 'ws://localhost:8777'

    PRODUCT_ID='XBT/USD'

    is_running = True

    def __init__(self):
        self.update_time = 0
        self.requestId = 1
        self.bids = {}
        self.asks = {}

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

    async def on_entry_update(self, entry, message):
        for level in message:
            price = float(level[0])
            qty   = float(level[1])

            if math.isclose(qty, 0.0):
                if level[0] in entry:
                    del entry[level[0]]
            else:
                entry[level[0]] = level

    async def on_book_update(self, payload):
        for event, message in payload.items():
            if 'as' == event or 'a' == event:
                await self.on_entry_update(self.asks, message)
            else:
                if 'bs' == event or 'b' == event:
                    await self.on_entry_update(self.bids, message)


        await self.on_price_update()

    async def on_price_update(self):

            NBEST=3
            
            print('\t\tbest asks')
            best_offers = reversed(sorted(self.asks.items(), key=lambda level: float(level[0]))[:NBEST])
            best_offers = [k for k in best_offers]
            for level in best_offers:
                print ('\t\t%s' % str(level))                                
                    
            best_bids = sorted(self.bids.items(), reverse=True, key=lambda level: float(level[0]))[:NBEST]
            best_bids = [k for k in best_bids]
            for level in best_bids:
                print (level)
                    
            print('best bids')

        
    async def on_message(self, websocket, message):
        self.update_time = time.time()
        event_message = json.loads(message)
        
        if type(event_message) == list:

            (id, payload, name, pair) = event_message
            await self.on_book_update(payload)

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
            'name':name
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
        kwss = KrakenWss()
        asioloop = asyncio.get_event_loop()
        asioloop.run_until_complete(kwss.run_event_loop())
    except Exception as e:
        print('Error: %s' % repr(e))
    finally:
        asioloop.close()
        sys.exit(0)
        
