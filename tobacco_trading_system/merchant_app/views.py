from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Sum, Avg, Count, Q, F
from django.utils import timezone
from datetime import datetime, timedelta
from django.contrib import messages
from .models import *
from timb_dashboard.models import Transaction, TobaccoGrade, ContractFarmer
from ai_models.ai_engine import get_purchase_recommendations, assess_risk
from utils.qr_code import qr_manager
import json

@login_required
def dashboard(request):
    """Main Merchant Dashboard"""
    # Check user type using User model fields
    if not request.user.is_merchant:
        return redirect('timb_dashboard')
    
    merchant = get_object_or_404(Merchant, user=request.user)
    
    # Key statistics
    stats = {
        'total_inventory_value': MerchantInventory.objects.filter(
            merchant=merchant
        ).aggregate(
            total=Sum(F('quantity') * F('average_cost'))
        )['total'] or 0,
        
        'active_orders': ClientOrder.objects.filter(
            merchant=merchant,
            status__in=['PENDING', 'PROCESSING', 'PARTIALLY_FILLED']
        ).count(),
        
        'todays_purchases': Transaction.objects.filter(
            buyer=request.user,
            timestamp__date=timezone.now().date()
        ).count(),
        
        'monthly_volume': Transaction.objects.filter(
            buyer=request.user,
            timestamp__month=timezone.now().month
        ).aggregate(Sum('quantity'))['quantity__sum'] or 0,
    }
    
    # Inventory summary
    inventory = MerchantInventory.objects.filter(merchant=merchant).select_related('grade')
    
    # Recent transactions
    recent_purchases = Transaction.objects.filter(
        buyer=request.user
    ).select_related('grade', 'floor').order_by('-timestamp')[:10]
    
    # Active orders
    active_orders = ClientOrder.objects.filter(
        merchant=merchant,
        status__in=['PENDING', 'PROCESSING', 'PARTIALLY_FILLED']
    ).order_by('delivery_date')[:5]
    
    # AI recommendations
    recommendations = PurchaseRecommendation.objects.filter(
        merchant=merchant,
        is_acted_upon=False
    ).order_by('-confidence_score', '-created_at')[:5]
    
    # Risk assessments
    risks = RiskAssessment.objects.filter(
        merchant=merchant,
        is_active=True
    ).order_by('-risk_score')[:5]
    
    context = {
        'merchant': merchant,
        'stats': stats,
        'inventory': inventory,
        'recent_purchases': recent_purchases,
        'active_orders': active_orders,
        'recommendations': recommendations,
        'risks': risks,
    }
    
    return render(request, 'merchant_app/dashboard.html', context)

@login_required
def inventory_view(request):
    """Inventory management view"""
    merchant = get_object_or_404(Merchant, user=request.user)
    
    inventory = MerchantInventory.objects.filter(
        merchant=merchant
    ).select_related('grade').order_by('grade__grade_name')
    
    # Inventory analytics
    total_value = inventory.aggregate(
        total=Sum(F('quantity') * F('average_cost'))
    )['total'] or 0
    
    total_quantity = inventory.aggregate(Sum('quantity'))['quantity__sum'] or 0
    
    # Low stock alerts
    low_stock_threshold = 100  # kg
    low_stock_items = inventory.filter(quantity__lt=low_stock_threshold)
    
    context = {
        'inventory': inventory,
        'total_value': total_value,
        'total_quantity': total_quantity,
        'low_stock_items': low_stock_items,
    }
    
    return render(request, 'merchant_app/inventory.html', context)

@login_required
def orders_view(request):
    """Client orders management"""
    merchant = get_object_or_404(Merchant, user=request.user)
    
    orders = ClientOrder.objects.filter(merchant=merchant).order_by('-created_at')
    
    # Order statistics
    order_stats = {
        'pending': orders.filter(status='PENDING').count(),
        'processing': orders.filter(status='PROCESSING').count(),
        'completed': orders.filter(status='COMPLETED').count(),
        'total_value': orders.aggregate(
            total=Sum(F('requested_quantity') * F('target_price'))
        )['total'] or 0,
    }
    
    context = {
        'orders': orders,
        'order_stats': order_stats,
    }
    
    return render(request, 'merchant_app/orders.html', context)

@login_required
def create_order(request):
    """Create new client order"""
    merchant = get_object_or_404(Merchant, user=request.user)
    
    if request.method == 'POST':
        # Extract form data
        client_name = request.POST.get('client_name')
        custom_grade_id = request.POST.get('custom_grade')
        quantity = float(request.POST.get('quantity'))
        target_price = float(request.POST.get('target_price'))
        delivery_date = request.POST.get('delivery_date')
        
        # Generate order number
        order_number = f"ORD-{timezone.now().strftime('%Y%m%d')}-{merchant.id:03d}-{ClientOrder.objects.filter(merchant=merchant).count() + 1:04d}"
        
        # Create order
        order = ClientOrder.objects.create(
            merchant=merchant,
            order_number=order_number,
            client_name=client_name,
            custom_grade_id=custom_grade_id if custom_grade_id else None,
            requested_quantity=quantity,
            target_price=target_price,
            delivery_date=delivery_date,
        )
        
        # Set encrypted client details
        client_details = {
            'contact_info': request.POST.get('client_contact', ''),
            'shipping_address': request.POST.get('shipping_address', ''),
            'payment_terms': request.POST.get('payment_terms', ''),
        }
        order.set_client_details(client_details)
        order.save()
        
        messages.success(request, f'Order {order_number} created successfully')
        return redirect('merchant_orders')
    
    custom_grades = CustomGrade.objects.filter(merchant=merchant, is_active=True)
    
    context = {
        'custom_grades': custom_grades,
    }
    
    return render(request, 'merchant_app/create_order.html', context)

@login_required
def custom_grades_view(request):
    """Manage custom grades and aggregation rules"""
    merchant = get_object_or_404(Merchant, user=request.user)
    
    custom_grades = CustomGrade.objects.filter(merchant=merchant).order_by('-created_at')
    aggregation_rules = AggregationRule.objects.filter(merchant=merchant).order_by('-created_at')
    
    context = {
        'custom_grades': custom_grades,
        'aggregation_rules': aggregation_rules,
        'base_grades': TobaccoGrade.objects.filter(is_active=True),
    }
    
    return render(request, 'merchant_app/custom_grades.html', context)

@login_required
def create_custom_grade(request):
    """Create new custom grade"""
    merchant = get_object_or_404(Merchant, user=request.user)
    
    if request.method == 'POST':
        grade_name = request.POST.get('grade_name')
        description = request.POST.get('description')
        target_price = float(request.POST.get('target_price'))
        
        # Create custom grade
        custom_grade = CustomGrade.objects.create(
            merchant=merchant,
            custom_grade_name=grade_name,
            description=description,
            target_price=target_price,
        )
        
        # Add components
        components = []
        base_grades = request.POST.getlist('base_grade[]')
        percentages = request.POST.getlist('percentage[]')
        min_quantities = request.POST.getlist('min_quantity[]')
        
        for i, base_grade_id in enumerate(base_grades):
            if base_grade_id and percentages[i]:
                CustomGradeComponent.objects.create(
                    custom_grade=custom_grade,
                    base_grade_id=base_grade_id,
                    percentage=float(percentages[i]),
                    minimum_quantity=float(min_quantities[i]) if min_quantities[i] else 0,
                )
                components.append({
                    'grade_id': base_grade_id,
                    'percentage': float(percentages[i]),
                    'min_quantity': float(min_quantities[i]) if min_quantities[i] else 0,
                })
        
        # Store composition rules
        custom_grade.set_composition({
            'components': components,
            'total_percentage': sum([float(p) for p in percentages if p]),
        })
        custom_grade.save()
        
        messages.success(request, f'Custom grade "{grade_name}" created successfully')
        return redirect('merchant_custom_grades')
    
    base_grades = TobaccoGrade.objects.filter(is_active=True)
    
    context = {
        'base_grades': base_grades,
    }
    
    return render(request, 'merchant_app/create_custom_grade.html', context)

@login_required
def purchase_recommendations_view(request):
    """AI-powered purchase recommendations"""
    merchant = get_object_or_404(Merchant, user=request.user)
    
    # Get latest recommendations
    recommendations = PurchaseRecommendation.objects.filter(
        merchant=merchant
    ).order_by('-created_at')
    
    # Generate new recommendations if requested
    if request.method == 'POST' and request.POST.get('generate_new'):
        new_recommendations = get_purchase_recommendations(merchant)
        messages.success(request, f'Generated {len(new_recommendations)} new recommendations')
        return redirect('merchant_purchase_recommendations')
    
    context = {
        'recommendations': recommendations,
    }
    
    return render(request, 'merchant_app/purchase_recommendations.html', context)

@login_required
def risk_management_view(request):
    """Risk assessment and management"""
    merchant = get_object_or_404(Merchant, user=request.user)
    
    # Current risk assessments
    risks = RiskAssessment.objects.filter(merchant=merchant).order_by('-assessment_date')
    
    # Contract farmers risk
    farmers = ContractFarmer.objects.filter(contracted_merchant=merchant)
    
    # Generate new risk assessment if requested
    if request.method == 'POST' and request.POST.get('assess_risk'):
        risk_data = assess_risk(merchant)
        messages.success(request, 'Risk assessment completed')
        return redirect('merchant_risk_management')
    
    context = {
        'risks': risks,
        'farmers': farmers,
        'merchant': merchant,
    }
    
    return render(request, 'merchant_app/risk_management.html', context)

@login_required
def api_inventory_value(request):
    """API endpoint for inventory value trends"""
    merchant = get_object_or_404(Merchant, user=request.user)
    days = int(request.GET.get('days', 30))
    
    # This would typically track inventory value changes over time
    # For now, we'll return current inventory breakdown
    inventory_data = MerchantInventory.objects.filter(
        merchant=merchant
    ).values('grade__grade_name').annotate(
        quantity=Sum('quantity'),
        value=Sum(F('quantity') * F('average_cost'))
    )
    
    return JsonResponse(list(inventory_data), safe=False)

@login_required
def api_order_fulfillment(request):
    """API endpoint for order fulfillment analytics"""
    merchant = get_object_or_404(Merchant, user=request.user)
    
    orders = ClientOrder.objects.filter(merchant=merchant)
    fulfillment_data = orders.values('status').annotate(count=Count('id'))
    
    return JsonResponse(list(fulfillment_data), safe=False)

@login_required
def generate_inventory_qr(request):
    """Generate encrypted QR code for inventory data"""
    merchant = get_object_or_404(Merchant, user=request.user)
    
    # Get current inventory
    inventory_data = []
    for item in MerchantInventory.objects.filter(merchant=merchant).select_related('grade'):
        storage_details = item.get_storage_details()
        inventory_data.append({
            'grade': item.grade.grade_name,
            'quantity': float(item.quantity),
            'average_cost': float(item.average_cost),
            'location': item.location,
            'storage_conditions': storage_details.get('conditions', 'Standard'),
            'last_updated': item.last_updated.isoformat(),
        })
    
    # Create secure QR code
    qr_data = qr_manager.generate_access_token({
        'type': 'inventory',
        'merchant': merchant.company_name,
        'data': inventory_data,
        'generated_at': timezone.now().isoformat(),
    }, expiry_minutes=120)
    
    # Store in databases
    from authentication.models import QRToken, EncryptedData
    
    QRToken.objects.create(
        token=qr_data['token'],
        data_ref=qr_data['data_ref'],
        created_by=request.user,
        expires_at=datetime.fromisoformat(qr_data['expires_at'].replace('Z', '+00:00'))
    )
    
    EncryptedData.objects.create(
        data_ref=qr_data['data_ref'],
        encrypted_content=qr_data['encrypted_data'],
        data_type='inventory'
    )
    
    return JsonResponse({
        'qr_code': qr_data['qr_code'],
        'token': qr_data['token'],
        'expires_at': qr_data['expires_at']
    })