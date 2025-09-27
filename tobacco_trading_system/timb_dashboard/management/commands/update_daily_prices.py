from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from timb_dashboard.models import TobaccoGrade, Transaction, DailyPrice


class Command(BaseCommand):
    help = 'Update daily prices for all tobacco grades'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--date',
            type=str,
            help='Date to calculate prices for (YYYY-MM-DD). Defaults to yesterday.',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force update even if prices already exist for the date',
        )
    
    def handle(self, *args, **options):
        if options['date']:
            target_date = timezone.datetime.strptime(options['date'], '%Y-%m-%d').date()
        else:
            target_date = timezone.now().date() - timedelta(days=1)
        
        self.stdout.write(f'Calculating daily prices for {target_date}')
        
        grades = TobaccoGrade.objects.filter(is_active=True, is_tradeable=True)
        updated_count = 0
        created_count = 0
        
        for grade in grades:
            # Check if price already exists
            existing_price = DailyPrice.objects.filter(
                grade=grade,
                date=target_date
            ).first()
            
            if existing_price and not options['force']:
                self.stdout.write(f'Price already exists for {grade.grade_code} on {target_date}')
                continue
            
            # Get transactions for the date
            transactions = Transaction.objects.filter(
                grade=grade,
                timestamp__date=target_date,
                status='COMPLETED'
            ).order_by('timestamp')
            
            if not transactions.exists():
                self.stdout.write(f'No transactions found for {grade.grade_code} on {target_date}')
                continue
            
            # Calculate price statistics
            prices = [t.price_per_kg for t in transactions]
            volumes = [t.quantity for t in transactions]
            
            opening_price = prices[0]
            closing_price = prices[-1]
            high_price = max(prices)
            low_price = min(prices)
            avg_price = sum(prices) / len(prices)
            total_volume = sum(volumes)
            
            if existing_price:
                # Update existing price
                existing_price.opening_price = opening_price
                existing_price.closing_price = closing_price
                existing_price.high_price = high_price
                existing_price.low_price = low_price
                existing_price.average_price = avg_price
                existing_price.volume_traded = total_volume
                existing_price.number_of_transactions = transactions.count()
                existing_price.save()
                updated_count += 1
                action = 'Updated'
            else:
                # Create new price record
                DailyPrice.objects.create(
                    grade=grade,
                    date=target_date,
                    opening_price=opening_price,
                    closing_price=closing_price,
                    high_price=high_price,
                    low_price=low_price,
                    average_price=avg_price,
                    volume_traded=total_volume,
                    number_of_transactions=transactions.count(),
                )
                created_count += 1
                action = 'Created'
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'{action} price for {grade.grade_code}: ${closing_price} (Vol: {total_volume}kg)'
                )
            )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Daily price update completed: {created_count} created, {updated_count} updated'
            )
        )