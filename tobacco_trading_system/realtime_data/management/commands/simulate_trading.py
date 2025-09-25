from django.core.management.base import BaseCommand
from django.utils import timezone
from timb_dashboard.models import TobaccoGrade, TobaccoFloor, Transaction, User
from realtime_data.models import RealTimePrice, LiveTransaction
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import random
import time
import threading

class Command(BaseCommand):
    help = 'Simulate real-time trading activity'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--duration',
            type=int,
            default=60,
            help='Duration to run simulation in seconds'
        )
        
        parser.add_argument(
            '--interval',
            type=int,
            default=5,
            help='Interval between transactions in seconds'
        )
    
    def handle(self, *args, **options):
        duration = options['duration']
        interval = options['interval']
        
        self.stdout.write(f'Starting trading simulation for {duration} seconds...')
        
        # Initialize real-time prices
        self.initialize_prices()
        
        # Start simulation
        end_time = time.time() + duration
        
        while time.time() < end_time:
            self.simulate_transaction()
            time.sleep(interval)
        
        self.stdout.write(
            self.style.SUCCESS('Trading simulation completed')
        )
    
    def initialize_prices(self):
        """Initialize real-time prices for all grade-floor combinations"""
        grades = TobaccoGrade.objects.filter(is_active=True)
        floors = TobaccoFloor.objects.filter(is_active=True)
        
        for grade in grades:
            for floor in floors:
                price_obj, created = RealTimePrice.objects.get_or_create(
                    floor=floor,
                    grade=grade,
                    defaults={
                        'current_price': float(grade.base_price) * random.uniform(0.8, 1.2),
                        'volume_traded_today': 0
                    }
                )
                
                if created:
                    self.stdout.write(f'Initialized price for {grade.grade_code} at {floor.name}')
    
    def simulate_transaction(self):
        """Simulate a single transaction"""
        # Select random grade and floor
        grade = random.choice(list(TobaccoGrade.objects.filter(is_active=True)))
        floor = random.choice(list(TobaccoFloor.objects.filter(is_active=True)))
        
        # Generate transaction details
        quantity = random.uniform(50, 500)
        base_price = float(grade.base_price)
        price_variation = random.uniform(0.9, 1.1)
        price = base_price * price_variation
        
        # Create live transaction
        transaction_id = f"SIM-{timezone.now().strftime('%Y%m%d%H%M%S')}-{random.randint(1000, 9999)}"
        
        live_transaction = LiveTransaction.objects.create(
            transaction_id=transaction_id,
            floor=floor,
            grade=grade,
            quantity=quantity,
            price=price,
            buyer_info=f"Buyer-{random.randint(1, 100)}",
            seller_info=f"Seller-{random.randint(1, 50)}"
        )
        
        # Update real-time price
        price_obj, created = RealTimePrice.objects.get_or_create(
            floor=floor,
            grade=grade,
            defaults={
                'current_price': price,
                'volume_traded_today': quantity
            }
        )
        
        if not created:
            price_obj.previous_price = price_obj.current_price
            price_obj.current_price = price
            price_obj.price_change = price - (price_obj.previous_price or price)
            price_obj.volume_traded_today += quantity
            price_obj.save()
        
        # Broadcast via WebSocket
        channel_layer = get_channel_layer()
        if channel_layer:
            async_to_sync(channel_layer.group_send)(
                "realtime_data",
                {
                    "type": "transaction_update",
                    "data": {
                        "transaction_id": transaction_id,
                        "floor": floor.name,
                        "grade": grade.grade_name,
                        "quantity": quantity,
                        "price": price,
                        "timestamp": live_transaction.timestamp.isoformat()
                    }
                }
            )
            
            async_to_sync(channel_layer.group_send)(
                "realtime_data",
                {
                    "type": "price_update",
                    "data": {
                        "floor": floor.name,
                        "grade": grade.grade_name,
                        "current_price": float(price_obj.current_price),
                        "price_change": float(price_obj.price_change),
                        "volume_traded": float(price_obj.volume_traded_today),
                        "timestamp": price_obj.last_updated.isoformat()
                    }
                }
            )
        
        self.stdout.write(
            f'Simulated: {quantity:.0f}kg {grade.grade_code} @ ${price:.2f}/kg on {floor.name}'
        )