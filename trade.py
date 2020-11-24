import asyncio
import websockets
import json
import sys
import time
import traceback

class KrakenWss:

    WS_URL = 'wss://ws.kraken.com'

    PRODUCT_ID='XBT/USD'

    is_running = True

    def __init__(self):
        self.update_time = 0
        self.requestId = 1


    async def send_json(self, websocket, event):
        event_payload = json.dumps(event)
        print(event_payload)
        await websocket.send(event_payload)

    async def ping(self, websocket):
        event = {'event': 'ping', 'reqid': self.requestId}
        self.requestId = self.requestId + 1
        self.update_time = time.time()
        await self.send_json(websocket, event)

    async def on_subscription(self, websocket, event):
        print(event)
        
    async def on_message(self, websocket, message):
        self.update_time = time.time()
        event_message = json.loads(message)

        print(message)
        
        if type(event_message) == list:

            event_name = ''
            event_data = []
            
            for event_element in event_message:
                if type(event_element) == list:
                    event_data = event_element
                if type(event_element) == str:
                    event_name = event_element

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
            'reqid': self.requestId
        }
        
        self.requestId = self.requestId + 1

        pair_array = [ self.PRODUCT_ID ]
        
        subscription = {
            'name': name
        }

        event['pair'] = pair_array
        event['subscription'] = subscription
        await self.send_json(websocket, event)

    async def on_open(self, websocket):
        await self.send_subscription(websocket, 'trade')
        
    async def heartbeat(self, websocket):
        now = time.time()
        timedelta = now - self.update_time
        if timedelta > 1:
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

            async with websockets.connect(self.WS_URL) as websocket:
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

if __name__ == "__main__":

        try:
            kwss = KrakenWss()
            asioloop = asyncio.get_event_loop()
            asioloop.run_until_complete(kwss.run_event_loop())
        finally:
            asioloop.close()

        sys.exit(0)
        
