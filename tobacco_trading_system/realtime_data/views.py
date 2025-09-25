from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Sum, Avg, Count
from .models import RealTimePrice, LiveTransaction, MarketAlert
from timb_dashboard.models import Transaction, TobaccoGrade, TobaccoFloor
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json

@login_required
def realtime_dashboard(request):
    """Real-time data monitoring dashboard"""
    # Current market overview
    market_overview = RealTimePrice.objects.select_related('grade', 'floor').all()
    
    # Recent transactions
    recent_transactions = LiveTransaction.objects.select_related(
        'grade', 'floor'
    ).order_by('-timestamp')[:20]
    
    # Active alerts
    active_alerts = MarketAlert.objects.filter(
        is_resolved=False
    ).order_by('-created_at')[:10]
    
    # Trading statistics for today
    today_stats = Transaction.objects.filter(
        timestamp__date=timezone.now().date()
    ).aggregate(
        total_volume=Sum('quantity'),
        total_value=Sum('total_amount'),
        transaction_count=Count('id'),
        avg_price=Avg('price_per_kg')
    )
    
    context = {
        'market_overview': market_overview,
        'recent_transactions': recent_transactions,
        'active_alerts': active_alerts,
        'today_stats': today_stats,
    }
    
    return render(request, 'realtime_data/dashboard.html', context)

@login_required
def update_price(request):
    """Update real-time price (for testing/simulation)"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)
    
    try:
        data = json.loads(request.body)
        floor_id = data.get('floor_id')
        grade_id = data.get('grade_id')
        new_price = float(data.get('price'))
        volume = float(data.get('volume', 0))
        
        # Update price
        price_obj, created = RealTimePrice.objects.get_or_create(
            floor_id=floor_id,
            grade_id=grade_id,
            defaults={
                'current_price': new_price,
                'volume_traded_today': volume
            }
        )
        
        if not created:
            price_obj.previous_price = price_obj.current_price
            price_obj.current_price = new_price
            price_obj.price_change = new_price - (price_obj.previous_price or new_price)
            price_obj.volume_traded_today += volume
            price_obj.save()
        
        # Broadcast update via WebSocket
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "realtime_data",
            {
                "type": "price_update",
                "data": {
                    "floor": price_obj.floor.name,
                    "grade": price_obj.grade.grade_name,
                    "current_price": float(price_obj.current_price),
                    "price_change": float(price_obj.price_change),
                    "volume_traded": float(price_obj.volume_traded_today),
                    "timestamp": price_obj.last_updated.isoformat()
                }
            }
        )
        
        # Check for price alerts
        check_price_alerts(price_obj)
        
        return JsonResponse({
            'success': True,
            'message': 'Price updated successfully'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@login_required
def create_transaction(request):
    """Create live transaction (for real-time feed)"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)
    
    try:
        data = json.loads(request.body)
        
        # Create live transaction
        live_transaction = LiveTransaction.objects.create(
            transaction_id=f"LIVE-{timezone.now().strftime('%Y%m%d%H%M%S')}",
            floor_id=data.get('floor_id'),
            grade_id=data.get('grade_id'),
            quantity=data.get('quantity'),
            price=data.get('price'),
            buyer_info=data.get('buyer_info', 'Anonymous'),
            seller_info=data.get('seller_info', 'Anonymous')
        )
        
        # Broadcast transaction via WebSocket
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "realtime_data",
            {
                "type": "transaction_update",
                "data": {
                    "transaction_id": live_transaction.transaction_id,
                    "floor": live_transaction.floor.name,
                    "grade": live_transaction.grade.grade_name,
                    "quantity": float(live_transaction.quantity),
                    "price": float(live_transaction.price),
                    "timestamp": live_transaction.timestamp.isoformat()
                }
            }
        )
        
        # Update real-time price data
        try:
            price_obj = RealTimePrice.objects.get(
                floor=live_transaction.floor,
                grade=live_transaction.grade
            )
            price_obj.volume_traded_today += live_transaction.quantity
            price_obj.save()
        except RealTimePrice.DoesNotExist:
            pass
        
        return JsonResponse({
            'success': True,
            'transaction_id': live_transaction.transaction_id
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@login_required
def market_alerts(request):
    """Get market alerts"""
    alerts = MarketAlert.objects.filter(
        is_resolved=False
    ).order_by('-created_at')
    
    alert_data = []
    for alert in alerts:
        alert_info = {
            'id': alert.id,
            'alert_type': alert.alert_type,
            'title': alert.title,
            'message': alert.message,
            'severity': alert.severity,
            'created_at': alert.created_at.isoformat(),
        }
        
        if alert.floor:
            alert_info['floor'] = alert.floor.name
        
        if alert.grade:
            alert_info['grade'] = alert.grade.grade_name
        
        alert_data.append(alert_info)
    
    return JsonResponse({
        'alerts': alert_data
    })

@login_required
def resolve_alert(request, alert_id):
    """Resolve a market alert"""
    try:
        alert = MarketAlert.objects.get(id=alert_id)
        alert.is_resolved = True
        alert.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Alert resolved successfully'
        })
        
    except MarketAlert.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Alert not found'
        }, status=404)

def check_price_alerts(price_obj):
    """Check for price-related alerts"""
    # Price spike detection
    if price_obj.previous_price and price_obj.price_change:
        change_percentage = (price_obj.price_change / price_obj.previous_price) * 100
        
        if abs(change_percentage) > 10:  # 10% change threshold
            severity = 'HIGH' if abs(change_percentage) > 20 else 'MEDIUM'
            direction = 'increased' if change_percentage > 0 else 'decreased'
            
            alert = MarketAlert.objects.create(
                alert_type='PRICE_SPIKE',
                title=f'Price {direction} for {price_obj.grade.grade_name}',
                message=f'Price has {direction} by {abs(change_percentage):.1f}% to ${price_obj.current_price:.2f}/kg',
                severity=severity,
                floor=price_obj.floor,
                grade=price_obj.grade
            )
            
            # Set alert data
            alert.set_alert_data({
                'previous_price': float(price_obj.previous_price),
                'current_price': float(price_obj.current_price),
                'change_percentage': change_percentage,
                'threshold_exceeded': True
            })
            alert.save()
            
            # Broadcast alert
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                "realtime_data",
                {
                    "type": "fraud_alert",
                    "data": {
                        "alert_type": alert.alert_type,
                        "title": alert.title,
                        "message": alert.message,
                        "severity": alert.severity,
                        "timestamp": alert.created_at.isoformat()
                    }
                }
            )

@login_required
def trading_volume_data(request):
    """Get trading volume data for charts"""
    days = int(request.GET.get('days', 7))
    end_date = timezone.now().date()
    start_date = end_date - timezone.timedelta(days=days)
    
    # Daily volume data
    daily_volume = Transaction.objects.filter(
        timestamp__date__range=[start_date, end_date]
    ).extra(
        select={'day': 'date(timestamp)'}
    ).values('day').annotate(
        total_volume=Sum('quantity'),
        total_value=Sum('total_amount'),
        transaction_count=Count('id')
    ).order_by('day')
    
    return JsonResponse({
        'daily_volume': list(daily_volume)
    })

@login_required
def price_trends_data(request):
    """Get price trends data for charts"""
    grade_id = request.GET.get('grade_id')
    days = int(request.GET.get('days', 30))
    
    # Get price history
    from timb_dashboard.models import PriceHistory
    
    end_date = timezone.now().date()
    start_date = end_date - timezone.timedelta(days=days)
    
    query = PriceHistory.objects.filter(date__range=[start_date, end_date])
    
    if grade_id:
        query = query.filter(grade_id=grade_id)
    
    price_data = query.values('date', 'grade__grade_name').annotate(
        avg_price=Avg('price'),
        total_volume=Sum('volume_traded')
    ).order_by('date')
    
    return JsonResponse({
        'price_trends': list(price_data)
    })