from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import Transaction, FraudAlert, ContractFarmer, Merchant
from ai_models.ai_engine import fraud_model, side_buying_model
from realtime_data.models import MarketAlert
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import pandas as pd

@shared_task
def monitor_fraud_patterns():
    """Continuously monitor for fraud patterns"""
    # Get recent transactions
    recent_transactions = Transaction.objects.filter(
        timestamp__gte=timezone.now() - timedelta(hours=1)
    )
    
    fraud_alerts_created = 0
    
    for transaction in recent_transactions:
        if transaction.is_flagged:
            continue  # Already flagged
        
        # Prepare transaction data for AI model
        transaction_data = {
            'grade': transaction.grade.grade_code,
            'purchase_price_per_kg': float(transaction.price_per_kg),
            'sale_price_per_kg': float(transaction.price_per_kg * 1.2),  # Estimated
            'quantity_kg': float(transaction.quantity),
            'time_difference_days': 1,  # Default
            'merchant_experience_years': 5,  # Default
            'market_volatility': 0.15,  # Default
            'season': 'peak',
            'floor_location': transaction.floor.location if transaction.floor else 'unknown'
        }
        
        # Get fraud prediction
        if fraud_model.is_trained:
            prediction = fraud_model.predict(pd.DataFrame([transaction_data]))
            
            if prediction['fraud_probability'] > 0.7:  # High fraud probability
                # Create fraud alert
                alert = FraudAlert.objects.create(
                    alert_type='UNUSUAL_PATTERN',
                    transaction=transaction,
                    merchant=transaction.buyer.merchant if hasattr(transaction.buyer, 'merchant') else None,
                    severity='HIGH' if prediction['fraud_probability'] > 0.9 else 'MEDIUM',
                    description=f"AI detected potential fraud pattern. Probability: {prediction['fraud_probability']:.2%}"
                )
                
                # Set evidence
                alert.set_evidence({
                    'ai_prediction': prediction,
                    'transaction_data': transaction_data,
                    'detection_timestamp': timezone.now().isoformat()
                })
                alert.save()
                
                # Flag the transaction
                transaction.is_flagged = True
                transaction.fraud_score = prediction['fraud_probability']
                transaction.save()
                
                fraud_alerts_created += 1
                
                # Broadcast alert
                broadcast_fraud_alert(alert)
    
    return f"Fraud monitoring completed. {fraud_alerts_created} new alerts created."

@shared_task
def monitor_side_buying():
    """Monitor contract farmers for side buying"""
    # Get farmers with recent delivery activity
    farmers = ContractFarmer.objects.filter(
        contract_end_date__gte=timezone.now().date()
    )
    
    alerts_created = 0
    
    for farmer in farmers:
        # Check delivery ratio
        delivery_ratio = farmer.delivered_quantity / farmer.contracted_quantity if farmer.contracted_quantity > 0 else 0
        
        if delivery_ratio < 0.8:  # Less than 80% delivery
            # Prepare farmer data for AI model
            farmer_data = {
                'contracted_quantity_kg': float(farmer.contracted_quantity),
                'delivered_to_contractor_kg': float(farmer.delivered_quantity),
                'delivered_to_others_kg': 0,  # This would need to be tracked
                'delivery_ratio': delivery_ratio,
                'distance_to_contractor_km': 20,  # Default
                'distance_to_alternative_km': 15,  # Default
                'alternative_price_premium': 0.1,  # Default
                'farmer_debt_level_usd': 500,  # Default
                'contractor_support_score': 70,  # Default
                'harvest_season': 'mid'
            }
            
            # Get side buying prediction
            if side_buying_model.is_trained:
                prediction = side_buying_model.predict(pd.DataFrame([farmer_data]))
                
                if prediction['side_buying_probability'] > 0.6:
                    # Create fraud alert
                    alert = FraudAlert.objects.create(
                        alert_type='SIDE_BUYING',
                        farmer=farmer,
                        merchant=farmer.contracted_merchant,
                        severity=prediction['risk_level'],
                        description=f"Potential side buying detected. Risk: {prediction['risk_level']}, Probability: {prediction['side_buying_probability']:.2%}"
                    )
                    
                    # Set evidence
                    alert.set_evidence({
                        'ai_prediction': prediction,
                        'farmer_data': farmer_data,
                        'delivery_shortfall': float(farmer.contracted_quantity - farmer.delivered_quantity)
                    })
                    alert.save()
                    
                    alerts_created += 1
    
    return f"Side buying monitoring completed. {alerts_created} new alerts created."

@shared_task
def update_merchant_risk_scores():
    """Update risk scores for all merchants"""
    merchants = Merchant.objects.all()
    
    for merchant in merchants:
        # Calculate risk score based on various factors
        recent_transactions = Transaction.objects.filter(
            buyer=merchant.user,
            timestamp__gte=timezone.now() - timedelta(days=30)
        )
        
        # Transaction volume risk
        total_volume = sum(t.quantity for t in recent_transactions)
        volume_risk = min(1.0, total_volume / 10000)  # Normalize to 0-1
        
        # Price volatility risk
        if recent_transactions:
            prices = [float(t.price_per_kg) for t in recent_transactions]
            price_std = pd.Series(prices).std()
            volatility_risk = min(1.0, price_std / 2.0)  # Normalize
        else:
            volatility_risk = 0
        
        # Fraud alerts risk
        fraud_alerts = FraudAlert.objects.filter(
            merchant=merchant,
            created_at__gte=timezone.now() - timedelta(days=30)
        ).count()
        fraud_risk = min(1.0, fraud_alerts / 5)  # Normalize
        
        # Calculate overall risk score (0-100)
        risk_score = (volume_risk * 0.3 + volatility_risk * 0.4 + fraud_risk * 0.3) * 100
        
        # Update merchant risk score
        merchant.risk_score = risk_score
        merchant.save()
    
    return f"Updated risk scores for {merchants.count()} merchants."

@shared_task
def generate_daily_reports():
    """Generate daily trading reports"""
    from timb_dashboard.views import generate_daily_report
    
    # Generate report data
    report_data = generate_daily_report()
    
    # Store report (could be saved to database, sent via email, etc.)
    # For now, we'll just log it
    print(f"Daily report generated: {report_data}")
    
    return "Daily report generated successfully."

@shared_task
def cleanup_expired_qr_tokens():
    """Clean up expired QR tokens"""
    from authentication.models import QRToken, EncryptedData
    
    # Get expired tokens
    expired_tokens = QRToken.objects.filter(
        expires_at__lt=timezone.now()
    )
    
    # Get associated data references
    data_refs = list(expired_tokens.values_list('data_ref', flat=True))
    
    # Delete expired tokens
    deleted_tokens = expired_tokens.count()
    expired_tokens.delete()
    
    # Delete associated encrypted data
    deleted_data = EncryptedData.objects.filter(
        data_ref__in=data_refs
    ).delete()[0]
    
    return f"Cleaned up {deleted_tokens} expired tokens and {deleted_data} encrypted data records."

def broadcast_fraud_alert(alert):
    """Broadcast fraud alert via WebSocket"""
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "realtime_data",
        {
            "type": "fraud_alert",
            "data": {
                "alert_id": alert.id,
                "alert_type": alert.alert_type,
                "severity": alert.severity,
                "description": alert.description,
                "timestamp": alert.created_at.isoformat()
            }
        }
    )

# Schedule periodic tasks
from celery.schedules import crontab

app.conf.beat_schedule = {
    'monitor-fraud-patterns': {
        'task': 'timb_dashboard.tasks.monitor_fraud_patterns',
        'schedule': crontab(minute='*/10'),  # Every 10 minutes
    },
    'monitor-side-buying': {
        'task': 'timb_dashboard.tasks.monitor_side_buying',
        'schedule': crontab(hour=6, minute=0),  # Daily at 6 AM
    },
    'update-risk-scores': {
        'task': 'timb_dashboard.tasks.update_merchant_risk_scores',
        'schedule': crontab(hour=2, minute=0),  # Daily at 2 AM
    },
    'generate-daily-reports': {
        'task': 'timb_dashboard.tasks.generate_daily_reports',
        'schedule': crontab(hour=23, minute=0),  # Daily at 11 PM
    },
    'cleanup-expired-tokens': {
        'task': 'timb_dashboard.tasks.cleanup_expired_qr_tokens',
        'schedule': crontab(hour=1, minute=0),  # Daily at 1 AM
    },
}