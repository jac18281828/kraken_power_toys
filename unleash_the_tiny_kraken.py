#!/usr/bin/env python

# wss server

import asyncio
import websockets
import json
import traceback
import uuid

class user_session:

    def __init__(self):
        self.subscription = set()
        self.orders = {}


    def add_subscription(self, name):
        self.subscription.add(name)

    def get_subscription(self):
        return frozenset(self.subscription)

    def add_order(self, order_event):
        id = str(uuid.uuid4())
        self.orders[id] = order_event
        return id

    
class kraken_server:

    TRADE_PRICE = 8000.0

    def __init__(self):
        self.user_map = {}


    async def send_json(self, websocket, event):
        event_payload = json.dumps(event)
        print(event_payload)
        await websocket.send(event_payload)


    async def error(self, message, event, websocket):
        error = {'errorMessage', message}
        if 'reqid' in event:
            error['reqid'] = event['reqid']
        await self.send_json(websocket, error)


    async def check_token(self, event, websocket):
        if 'token' in event:
            return True
        else:
            await error('API Token is required.', event, websocket)
            return False

    async def status(self, websocket):
        event = {'event': 'systemStatus'}
        await self.send_json(websocket, event)

    async def pong(self, event, websocket):
        response = {'event': 'pong'}
        response['reqid'] = event['reqid']
        await self.send_json(websocket, response)


    async def subscription(self, event, websocket):
        subscription_event = event['subscription']
        name = subscription_event['name']

        if name != None:
            print('client subscription: %s' % name)

            user = self.user_map[websocket]
            user.add_subscription(name)
            print("Subscriptions: %s" % (','.join(user.get_subscription())))
            
            if await self.check_token(subscription_event, websocket):
                
                subscription = {'event': 'subscriptionStatus'}
                subscription['status'] = 'subscribed'
                subscription['reqid'] = event['reqid']
                subscription['channelName'] = name
                await self.send_json(websocket, subscription)

                if 'ownTrades' == name or 'openOrders' == name:
                    orderEvent = [[], name]
                    await self.send_json(websocket, orderEvent)
                    
        else:
            await self.error('name is required for subscription', event, websocket)

    async def add_order_status(self, id, event, websocket):
        print('status')

    async def pending(self, id, event, websocket):
        print('pending')

    async def close(id, event, websocket):
        print('close')

    async def handle_market(self, id, event, websocket):
        await self.add_order_status(id, event, websocket)
        await self.pending(id, event, websocket)
        await self.close(id, event, websocket)                

    async def handle_limit(self, id, event, websocket):        
        await self.add_order_status(id, event, websocket)
        await self.pending(id, event, websocket)

        ## if buy greater than TRADE_PRICE then fill
        ## else rest
        ## if sell less than TRADE_PRICE then fill
        ## else rest
        
    async def add_order(self, event, websocket):
        if await self.check_token(event, websocket):
            user = self.user_map[websocket]
            
            id = user.add_order(event)

            if 'market' == event['ordertype']:
                await self.handle_limit(self, id, event, websocket)
                
            if 'limit' == event['ordertype']:
                await self.handle_limit(self, id, event, websocket)            
        

    async def message_loop(self, websocket, path):
        try:
            print('new connection')
            
            self.user_map[websocket] = user_session()
            
            while True:

                await self.status(websocket)
                
                async for message in websocket:
                    event = json.loads(message)
                    if 'ping' == event['event']:
                        await self.pong(event, websocket)

                    if 'subscribe' == event['event']:
                        await self.subscription(event, websocket)

                    if 'addOrder' == event['event']:
                        await self.add_order(event, websocket)
                        
        except Exception as e:
            print('Error: %s' % e)
            print(traceback.format_exc(e))


if __name__  == '__main__':

    kss = kraken_server()
    
    start_server = websockets.serve(kss.message_loop, 'localhost', 8777)

    asyncio.get_event_loop().run_until_complete(start_server)

    print('Ready!')
    
    asyncio.get_event_loop().run_forever()

    
