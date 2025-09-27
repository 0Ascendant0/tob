import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone


class PriceConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = 'price_updates'
        
        # Join price updates group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        # Leave price updates group
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )
    
    async def price_update(self, event):
        # Send price update to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'price_update',
            'data': event['data']
        }))


class TransactionConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        
        # Determine group based on user type
        if hasattr(self.user, 'is_timb_staff') and self.user.is_timb_staff:
            self.group_name = 'timb_staff'
        elif hasattr(self.user, 'is_merchant') and self.user.is_merchant:
            self.group_name = f'merchant_{self.user.id}'
        else:
            await self.close()
            return
        
        # Join group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        # Leave group
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )
    
    async def transaction_update(self, event):
        # Send transaction update to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'transaction_update',
            'data': event['data']
        }))


class AlertConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = 'market_alerts'
        
        # Join alerts group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        # Leave alerts group
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )
    
    async def market_alert(self, event):
        # Send alert to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'market_alert',
            'data': event['data']
        }))
    
    async def fraud_alert(self, event):
        # Send fraud alert to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'fraud_alert',
            'data': event['data']
        }))


class DashboardConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        self.user_type = self.scope['url_route']['kwargs']['user_type']
        
        # Validate user type
        if self.user_type == 'timb' and not (hasattr(self.user, 'is_timb_staff') and self.user.is_timb_staff):
            await self.close()
            return
        elif self.user_type == 'merchant' and not (hasattr(self.user, 'is_merchant') and self.user.is_merchant):
            await self.close()
            return
        
        self.group_name = f'{self.user_type}_dashboard'
        
        # Join dashboard group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        # Leave dashboard group
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )
    
    async def dashboard_update(self, event):
        # Send dashboard update to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'dashboard_update',
            'data': event['data']
        }))