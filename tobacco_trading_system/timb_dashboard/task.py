from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
import logging

from .models import (
    Transaction, TobaccoGrade, DailyPrice, DashboardMetric, 
    SystemAlert, TobaccoFloor
)

logger = logging.getLogger(__name__)


@shared_task
def calculate_daily_prices():
    """Calculate daily prices for all grades"""
    today = timezone.now().date()
    yesterday = today - timedelta(days=1)
    
    try:
        grades = TobaccoGrade.objects.filter(is_active=True, is_tradeable=True)
        updated_count = 0
        
        for grade in grades:
            # Get yesterday's transactions
            transactions = Transaction.objects.filter(
                grade=grade,
                timestamp__date=yesterday,
                status='COMPLETED'
            ).order_by('timestamp')
            
            if transactions.exists():
                prices = [t.price_per_kg for t in transactions]
                volumes = [t.quantity for t in transactions]
                
                opening_price = prices[0]
                closing_price = prices[-1]
                high_price = max(prices)
                low_price = min(prices)
                avg_price = sum(prices) / len(prices)
                total_volume = sum(volumes)
                
                # Create daily price record
                daily_price, created = DailyPrice.objects.get_or_create(
                    grade=grade,
                    date=yesterday,
                    defaults={
                        'opening_price': opening_price,
                        'closing_price': closing_price,
                        'high_price': high_price,
                        'low_price': low_price,
                        'average_price': avg_price,
                        'volume_traded': total_volume,
                        'number_of_transactions': transactions.count(),
                    }
                )
                
                if created:
                    updated_count += 1
                    logger.info(f"Created daily price for {grade.grade_code}: ${closing_price}")
        
        logger.info(f"Daily price calculation completed: {updated_count} grades updated")
        return updated_count
        
    except Exception as e:
        logger.error(f"Error calculating daily prices: {str(e)}")
        raise


@shared_task
def detect_price_anomalies():
    """Detect unusual price movements"""
    try:
        today = timezone.now().date()
        alert_count = 0
        
        # Get today's prices
        todays_prices = DailyPrice.objects.filter(date=today)
        
        for price_record in todays_prices:
            # Get previous price
            previous_price = DailyPrice.objects.filter(
                grade=price_record.grade,
                date__lt=today
            ).order_by('-date').first()
            
            if previous_price:
                # Calculate percentage change
                change_pct = (
                    (price_record.closing_price - previous_price.closing_price) 
                    / previous_price.closing_price
                ) * 100
                
                # Check for significant changes
                if abs(change_pct) > 15:  # More than 15% change
                    severity = 'HIGH' if abs(change_pct) > 25 else 'MEDIUM'
                    
                    SystemAlert.objects.create(
                        title=f'Price anomaly detected: {price_record.grade.grade_code}',
                        message=f'Price changed by {change_pct:.1f}% from ${previous_price.closing_price} to ${price_record.closing_price}',
                        alert_type='PRICE',
                        severity=severity,
                        grade=price_record.grade,
                        metadata={
                            'previous_price': float(previous_price.closing_price),
                            'current_price': float(price_record.closing_price),
                            'change_percentage': float(change_pct),
                            'date': today.isoformat()
                        }
                    )
                    
                    alert_count += 1
        
        logger.info(f"Price anomaly detection completed: {alert_count} alerts created")
        return alert_count
        
    except Exception as e:
        logger.error(f"Error detecting price anomalies: {str(e)}")
        raise


@shared_task
def cleanup_old_metrics():
    """Clean up old dashboard metrics"""
    try:
        cutoff_date = timezone.now() - timedelta(days=30)
        
        # Delete old metrics
        deleted_count = DashboardMetric.objects.filter(
            timestamp__lt=cutoff_date
        ).delete()[0]
        
        logger.info(f"Cleaned up {deleted_count} old metrics")
        return deleted_count
        
    except Exception as e:
        logger.error(f"Error cleaning up metrics: {str(e)}")
        raise


@shared_task
def generate_daily_report():
    """Generate daily trading report"""
    try:
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)
        
        # Get yesterday's statistics
        transactions = Transaction.objects.filter(timestamp__date=yesterday)
        
        total_transactions = transactions.count()
        total_volume = sum([t.quantity for t in transactions])
        total_value = sum([t.total_amount for t in transactions])
        avg_price = total_value / total_volume if total_volume > 0 else 0
        
        # Get floor statistics
        floor_stats = {}
        for floor in TobaccoFloor.objects.filter(is_active=True):
            floor_transactions = transactions.filter(floor=floor)
            floor_stats[floor.name] = {
                'transactions': floor_transactions.count(),
                'volume': sum([t.quantity for t in floor_transactions]),
                'value': sum([t.total_amount for t in floor_transactions]),
            }
        
        # Get top grades
        grade_stats = {}
        for transaction in transactions:
            grade_code = transaction.grade.grade_code
            if grade_code not in grade_stats:
                grade_stats[grade_code] = {
                    'volume': 0,
                    'value': 0,
                    'transactions': 0
                }
            grade_stats[grade_code]['volume'] += transaction.quantity
            grade_stats[grade_code]['value'] += transaction.total_amount
            grade_stats[grade_code]['transactions'] += 1
        
        # Sort by volume
        top_grades = sorted(
            grade_stats.items(),
            key=lambda x: x[1]['volume'],
            reverse=True
        )[:10]
        
        report_data = {
            'date': yesterday.isoformat(),
            'summary': {
                'total_transactions': total_transactions,
                'total_volume': float(total_volume),
                'total_value': float(total_value),
                'average_price': float(avg_price),
            },
            'floor_statistics': floor_stats,
            'top_grades': dict(top_grades),
            'generated_at': timezone.now().isoformat()
        }
        
        # Store as dashboard metric
        DashboardMetric.objects.create(
            metric_type='DAILY_REPORT',
            value=total_transactions,
            metadata=report_data
        )
        
        logger.info(f"Generated daily report for {yesterday}")
        return report_data
        
    except Exception as e:
        logger.error(f"Error generating daily report: {str(e)}")
        raise


@shared_task
def monitor_system_health():
    """Monitor system health and performance"""
    try:
        from django.db import connection
        
        # Check database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            db_healthy = True
        
        # Check recent transaction volume
        recent_transactions = Transaction.objects.filter(
            timestamp__gte=timezone.now() - timedelta(hours=1)
        ).count()
        
        # Check for stuck transactions
        stuck_transactions = Transaction.objects.filter(
            status='PENDING',
            timestamp__lt=timezone.now() - timedelta(hours=24)
        ).count()
        
        # Create health metrics
        health_data = {
            'database_healthy': db_healthy,
            'recent_transactions': recent_transactions,
            'stuck_transactions': stuck_transactions,
            'timestamp': timezone.now().isoformat()
        }
        
        # Create alerts for issues
        if stuck_transactions > 0:
            SystemAlert.objects.create(
                title=f'{stuck_transactions} stuck transactions detected',
                message=f'Found {stuck_transactions} transactions pending for more than 24 hours',
                alert_type='SYSTEM',
                severity='HIGH',
                metadata=health_data
            )
        
        if recent_transactions == 0:
            # No transactions in the last hour during business hours
            current_hour = timezone.now().hour
            if 8 <= current_hour <= 17:  # Business hours
                SystemAlert.objects.create(
                    title='No recent transaction activity',
                    message='No transactions recorded in the last hour during business hours',
                    alert_type='BUSINESS',
                    severity='MEDIUM',
                    metadata=health_data
                )
        
        logger.info("System health monitoring completed")
        return health_data
        
    except Exception as e:
        logger.error(f"Error monitoring system health: {str(e)}")
        
        # Create critical alert for monitoring failure
        SystemAlert.objects.create(
            title='System monitoring failed',
            message=f'Health monitoring task failed: {str(e)}',
            alert_type='SYSTEM',
            severity='CRITICAL',
            metadata={'error': str(e), 'timestamp': timezone.now().isoformat()}
        )
        raise