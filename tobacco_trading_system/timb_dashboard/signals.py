from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from django.db import models
from .models import Transaction, DashboardMetric, SystemAlert


@receiver(post_save, sender=Transaction)
def update_transaction_metrics(sender, instance, created, **kwargs):
    """Update dashboard metrics when transaction is created/updated"""
    if created:
        today = timezone.now().date()
        
        # Update transaction count metric
        DashboardMetric.objects.create(
            metric_type='TRANSACTION_COUNT',
            value=Transaction.objects.filter(timestamp__date=today).count(),
            floor=instance.floor,
            grade=instance.grade,
            metadata={
                'transaction_id': instance.transaction_id,
                'transaction_type': instance.transaction_type
            }
        )
        
        # Update volume metric
        total_volume = Transaction.objects.filter(
            timestamp__date=today
        ).aggregate(total=models.Sum('quantity'))['total'] or 0
        
        DashboardMetric.objects.create(
            metric_type='TOTAL_VOLUME',
            value=total_volume,
            metadata={'date': today.isoformat()}
        )
        
        # Update value metric
        total_value = Transaction.objects.filter(
            timestamp__date=today
        ).aggregate(total=models.Sum('total_amount'))['total'] or 0
        
        DashboardMetric.objects.create(
            metric_type='TOTAL_VALUE',
            value=total_value,
            metadata={'date': today.isoformat()}
        )
        
        # Check for unusual activity
        recent_transactions = Transaction.objects.filter(
            seller=instance.seller,
            timestamp__gte=timezone.now() - timezone.timedelta(hours=1)
        ).count()
        
        if recent_transactions > 10:  # More than 10 transactions in an hour
            SystemAlert.objects.create(
                title=f'High transaction volume: {instance.seller.username}',
                message=f'User {instance.seller.username} has {recent_transactions} transactions in the last hour',
                alert_type='BUSINESS',
                severity='MEDIUM',
                metadata={
                    'user_id': instance.seller.id,
                    'transaction_count': recent_transactions,
                    'time_period': '1_hour'
                }
            )


@receiver(post_save, sender=SystemAlert)
def update_alert_metrics(sender, instance, created, **kwargs):
    """Update alert metrics when new alert is created"""
    if created:
        active_alerts = SystemAlert.objects.filter(is_active=True).count()
        
        DashboardMetric.objects.create(
            metric_type='FRAUD_ALERTS',
            value=active_alerts,
            metadata={
                'alert_type': instance.alert_type,
                'severity': instance.severity,
                'alert_id': instance.id
            }
        )