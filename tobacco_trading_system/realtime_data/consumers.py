import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from django.utils import timezone
from datetime import datetime

class RealtimeDataConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Check authentication
        if self.scope["user"] == AnonymousUser():
            await self.close()
            return
        
        # Join real-time data group
        await self.channel_layer.group_add(
            "realtime_data",
            self.channel_name
        )
        
        await self.accept()
        
        # Send initial data
        await self.send_initial_data()
    
    async def disconnect(self, close_code):
        # Leave real-time data group
        await self.channel_layer.group_discard(
            "realtime_data",
            self.channel_name
        )
    
    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type')
        
        if message_type == 'subscribe_prices':
            # Subscribe to price updates for specific grades
            grades = data.get('grades', [])
            await self.subscribe_to_prices(grades)
        
        elif message_type == 'subscribe_transactions':
            # Subscribe to transaction updates
            await self.subscribe_to_transactions()
    
    async def send_initial_data(self):
        """Send initial real-time data when client connects"""
        # Get current prices
        current_prices = await self.get_current_prices()
        
        await self.send(text_data=json.dumps({
            'type': 'initial_data',
            'data': {
                'prices': current_prices,
                'timestamp': timezone.now().isoformat()
            }
        }))
    
    async def price_update(self, event):
        """Handle price update events"""
        await self.send(text_data=json.dumps({
            'type': 'price_update',
            'payload': event['data']
        }))
    
    async def transaction_update(self, event):
        """Handle transaction update events"""
        await self.send(text_data=json.dumps({
            'type': 'transaction',
            'payload': event['data']
        }))
    
    async def fraud_alert(self, event):
        """Handle fraud alert events"""
        await self.send(text_data=json.dumps({
            'type': 'fraud_alert',
            'payload': event['data']
        }))
    
    async def yield_prediction_update(self, event):
        """Handle yield prediction updates"""
        await self.send(text_data=json.dumps({
            'type': 'yield_prediction',
            'payload': event['data']
        }))
    
    @database_sync_to_async
    def get_current_prices(self):
        """Get current market prices"""
        from .models import RealTimePrice
        
        prices = []
        for price_obj in RealTimePrice.objects.select_related('grade', 'floor').all():
            prices.append({
                'grade': price_obj.grade.grade_name,
                'floor': price_obj.floor.name,
                'current_price': float(price_obj.current_price),
                'price_change': float(price_obj.price_change),
                'volume_traded': float(price_obj.volume_traded_today),
                'last_updated': price_obj.last_updated.isoformat()
            })
        
        return prices
    
    async def subscribe_to_prices(self, grades):
        """Subscribe to price updates for specific grades"""
        # Join grade-specific groups
        for grade in grades:
            await self.channel_layer.group_add(
                f"price_updates_{grade}",
                self.channel_name
            )
    
    async def subscribe_to_transactions(self):
        """Subscribe to transaction updates"""
        await self.channel_layer.group_add(
            "transaction_updates",
            self.channel_name
        )

class MerchantDataConsumer(AsyncWebsocketConsumer):
    """Specialized consumer for merchant-specific data"""
    
    async def connect(self):
        if self.scope["user"] == AnonymousUser():
            await self.close()
            return
        
        # Check if user is a merchant
        user = self.scope["user"]
        if not hasattr(user, 'profile') or not user.profile.is_merchant:
            await self.close()
            return
        
        # Get merchant ID
        merchant_id = await self.get_merchant_id(user)
        
        # Join merchant-specific group
        await self.channel_layer.group_add(
            f"merchant_{merchant_id}",
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        if hasattr(self, 'merchant_id'):
            await self.channel_layer.group_discard(
                f"merchant_{self.merchant_id}",
                self.channel_name
            )
    
    async def inventory_update(self, event):
        """Handle inventory updates"""
        await self.send(text_data=json.dumps({
            'type': 'inventory_update',
            'payload': event['data']
        }))
    
    async def order_update(self, event):
        """Handle order updates"""
        await self.send(text_data=json.dumps({
            'type': 'order_update',
            'payload': event['data']
        }))
    
    async def recommendation_update(self, event):
        """Handle new recommendations"""
        await self.send(text_data=json.dumps({
            'type': 'recommendation',
            'payload': event['data']
        }))
    
    @database_sync_to_async
    def get_merchant_id(self, user):
        """Get merchant ID for the user"""
        try:
            from timb_dashboard.models import Merchant
            merchant = Merchant.objects.get(user=user)
            return merchant.id
        except Merchant.DoesNotExist:
            return None