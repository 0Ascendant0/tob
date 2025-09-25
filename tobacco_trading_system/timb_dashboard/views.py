from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Sum, Avg, Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
from .models import *
from ai_models.models import YieldPredictionData, PredictionLog
from utils.qr_code import qr_manager
import json

@login_required
def dashboard(request):
    """Main TIMB Dashboard"""
    # Check user type using User model fields
    if request.user.is_merchant:
        return redirect('merchant_dashboard')
    
    # Key statistics
    stats = {
        'total_merchants': Merchant.objects.filter(status='ACTIVE').count(),
        'total_transactions_today': Transaction.objects.filter(
            timestamp__date=timezone.now().date()
        ).count(),
        'total_volume_today': Transaction.objects.filter(
            timestamp__date=timezone.now().date()
        ).aggregate(Sum('quantity'))['quantity__sum'] or 0,
        'active_alerts': FraudAlert.objects.filter(status='OPEN').count(),
        'total_farmers': ContractFarmer.objects.count(),
    }
    
    # Recent transactions
    recent_transactions = Transaction.objects.select_related(
        'seller', 'buyer', 'grade', 'floor'
    ).order_by('-timestamp')[:10]
    
    # Fraud alerts
    fraud_alerts = FraudAlert.objects.filter(
        status='OPEN'
    ).order_by('-created_at')[:5]
    
    # Price trends (last 30 days)
    thirty_days_ago = timezone.now() - timedelta(days=30)
    price_trends = PriceHistory.objects.filter(
        date__gte=thirty_days_ago
    ).values('date', 'grade__grade_name').annotate(
        avg_price=Avg('price')
    ).order_by('date')
    
    # AI predictions
    latest_yield_prediction = YieldPredictionData.objects.filter(
        year=timezone.now().year
    ).first()
    
    context = {
        'stats': stats,
        'recent_transactions': recent_transactions,
        'fraud_alerts': fraud_alerts,
        'price_trends': list(price_trends),
        'yield_prediction': latest_yield_prediction,
    }
    
    return render(request, 'timb_dashboard/dashboard.html', context)

@login_required
def merchants_view(request):
    """Merchants management view"""
    merchants = Merchant.objects.select_related('user').all()
    
    # Merchant statistics
    merchant_stats = {}
    for merchant in merchants:
        total_purchases = Transaction.objects.filter(buyer=merchant.user).aggregate(
            total_amount=Sum('total_amount'),
            total_quantity=Sum('quantity')
        )
        merchant_stats[merchant.id] = {
            'total_purchases': total_purchases['total_amount'] or 0,
            'total_quantity': total_purchases['total_quantity'] or 0,
            'risk_score': merchant.risk_score,
        }
    
    context = {
        'merchants': merchants,
        'merchant_stats': merchant_stats,
    }
    
    return render(request, 'timb_dashboard/merchants.html', context)

@login_required
def transactions_view(request):
    """Transactions monitoring view"""
    transactions = Transaction.objects.select_related(
        'seller', 'buyer', 'grade', 'floor'
    ).order_by('-timestamp')
    
    # Filters
    transaction_type = request.GET.get('type')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    if transaction_type:
        transactions = transactions.filter(transaction_type=transaction_type)
    
    if date_from:
        transactions = transactions.filter(timestamp__date__gte=date_from)
    
    if date_to:
        transactions = transactions.filter(timestamp__date__lte=date_to)
    
    # Flagged transactions
    flagged_transactions = transactions.filter(is_flagged=True)
    
    context = {
        'transactions': transactions[:100],  # Limit for performance
        'flagged_transactions': flagged_transactions[:20],
        'transaction_types': Transaction.TRANSACTION_TYPES,
    }
    
    return render(request, 'timb_dashboard/transactions.html', context)

@login_required
def fraud_detection_view(request):
    """Fraud detection and alerts view"""
    alerts = FraudAlert.objects.select_related(
        'transaction', 'merchant', 'farmer'
    ).order_by('-created_at')
    
    # Alert statistics
    alert_stats = FraudAlert.objects.aggregate(
        total_alerts=Count('id'),
        open_alerts=Count('id', filter=Q(status='OPEN')),
        critical_alerts=Count('id', filter=Q(severity='CRITICAL')),
    )
    
    # Recent fraud patterns
    fraud_patterns = FraudAlert.objects.values('alert_type').annotate(
        count=Count('id')
    ).order_by('-count')
    
    context = {
        'alerts': alerts[:50],
        'alert_stats': alert_stats,
        'fraud_patterns': fraud_patterns,
        'alert_types': FraudAlert.ALERT_TYPES,
        'severities': [choice[0] for choice in FraudAlert._meta.get_field('severity').choices],
    }
    
    return render(request, 'timb_dashboard/fraud_detection.html', context)

@login_required
def yield_prediction_view(request):
    """Yield prediction and analysis view"""
    # Historical data
    historical_data = YieldPredictionData.objects.order_by('-year')[:10]
    
    # Current year prediction
    current_year = timezone.now().year
    current_prediction = YieldPredictionData.objects.filter(year=current_year).first()
    
    # Prediction accuracy over years
    accuracy_data = YieldPredictionData.objects.filter(
        prediction_accuracy__isnull=False
    ).order_by('-year')[:10]
    
    context = {
        'historical_data': historical_data,
        'current_prediction': current_prediction,
        'accuracy_data': accuracy_data,
    }
    
    return render(request, 'timb_dashboard/yield_prediction.html', context)

@login_required
def price_monitoring_view(request):
    """Real-time price monitoring"""
    from realtime_data.models import RealTimePrice
    
    # Current prices by grade
    current_prices = RealTimePrice.objects.select_related('grade', 'floor').all()
    
    # Price changes today
    price_changes = RealTimePrice.objects.filter(
        last_updated__date=timezone.now().date()
    ).order_by('-price_change')
    
    # Trading volumes
    trading_volumes = RealTimePrice.objects.aggregate(
        total_volume=Sum('volume_traded_today')
    )
    
    context = {
        'current_prices': current_prices,
        'price_changes': price_changes,
        'trading_volumes': trading_volumes,
    }
    
    return render(request, 'timb_dashboard/price_monitoring.html', context)

@login_required
def api_transaction_data(request):
    """API endpoint for transaction data"""
    days = int(request.GET.get('days', 30))
    start_date = timezone.now() - timedelta(days=days)
    
    transactions = Transaction.objects.filter(
        timestamp__gte=start_date
    ).values(
        'timestamp__date'
    ).annotate(
        total_volume=Sum('quantity'),
        total_value=Sum('total_amount'),
        transaction_count=Count('id')
    ).order_by('timestamp__date')
    
    return JsonResponse(list(transactions), safe=False)

@login_required
def api_price_trends(request):
    """API endpoint for price trend data"""
    grade_id = request.GET.get('grade_id')
    days = int(request.GET.get('days', 30))
    start_date = timezone.now() - timedelta(days=days)
    
    query = PriceHistory.objects.filter(date__gte=start_date)
    if grade_id:
        query = query.filter(grade_id=grade_id)
    
    price_data = query.values('date', 'grade__grade_name').annotate(
        avg_price=Avg('price')
    ).order_by('date')
    
    return JsonResponse(list(price_data), safe=False)

@login_required
def generate_secure_report(request):
    """Generate encrypted report with QR access"""
    report_type = request.GET.get('type', 'daily')
    
    # Generate report data
    if report_type == 'daily':
        data = generate_daily_report()
    elif report_type == 'weekly':
        data = generate_weekly_report()
    else:
        data = generate_monthly_report()
    
    # Create secure QR code
    qr_data = qr_manager.generate_access_token(data, expiry_minutes=60)
    
    # Store in secure database
    from authentication.models import QRToken, EncryptedData
    
    # Store in QR tokens database
    QRToken.objects.create(
        token=qr_data['token'],
        data_ref=qr_data['data_ref'],
        created_by=request.user,
        expires_at=datetime.fromisoformat(qr_data['expires_at'].replace('Z', '+00:00'))
    )
    
    # Store encrypted data in main database
    EncryptedData.objects.create(
        data_ref=qr_data['data_ref'],
        encrypted_content=qr_data['encrypted_data'],
        data_type='report'
    )
    
    return JsonResponse({
        'qr_code': qr_data['qr_code'],
        'token': qr_data['token'],
        'expires_at': qr_data['expires_at']
    })

def generate_daily_report():
    """Generate daily trading report"""
    today = timezone.now().date()
    
    transactions = Transaction.objects.filter(timestamp__date=today)
    
    report = {
        'date': today.isoformat(),
        'total_transactions': transactions.count(),
        'total_volume': float(transactions.aggregate(Sum('quantity'))['quantity__sum'] or 0),
        'total_value': float(transactions.aggregate(Sum('total_amount'))['total_amount__sum'] or 0),
        'grade_breakdown': list(transactions.values('grade__grade_name').annotate(
            volume=Sum('quantity'),
            value=Sum('total_amount')
        )),
        'merchant_activity': list(transactions.values('buyer__username').annotate(
            purchases=Count('id'),
            volume=Sum('quantity')
        )),
        'fraud_alerts': FraudAlert.objects.filter(created_at__date=today).count(),
    }
    
    return report

def generate_weekly_report():
    """Generate weekly trading report"""
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=7)
    
    transactions = Transaction.objects.filter(
        timestamp__date__range=[start_date, end_date]
    )
    
    report = {
        'period': f'{start_date} to {end_date}',
        'total_transactions': transactions.count(),
        'total_volume': float(transactions.aggregate(Sum('quantity'))['quantity__sum'] or 0),
        'total_value': float(transactions.aggregate(Sum('total_amount'))['total_amount__sum'] or 0),
        'daily_breakdown': list(transactions.extra(
            select={'day': 'date(timestamp)'}
        ).values('day').annotate(
            volume=Sum('quantity'),
            value=Sum('total_amount')
        )),
    }
    
    return report

def generate_monthly_report():
    """Generate monthly trading report"""
    today = timezone.now().date()
    start_date = today.replace(day=1)
    
    transactions = Transaction.objects.filter(
        timestamp__date__range=[start_date, today]
    )
    
    report = {
        'month': today.strftime('%B %Y'),
        'total_transactions': transactions.count(),
        'total_volume': float(transactions.aggregate(Sum('quantity'))['quantity__sum'] or 0),
        'total_value': float(transactions.aggregate(Sum('total_amount'))['total_amount__sum'] or 0),
    }
    
    return report