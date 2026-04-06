from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .models import Booking, Payment
from treks.models import Trek
from guides.models import GuideProfile
from decimal import Decimal
import uuid
import requests
import logging
import hashlib
import hmac
import base64

logger = logging.getLogger(__name__)

def generate_esewa_signature(total_amount, transaction_uuid, product_code, secret_key):
    """Generate HMAC SHA256 signature for eSewa v2 API"""
    message = f"total_amount={total_amount},transaction_uuid={transaction_uuid},product_code={product_code}"
    signature = hmac.new(
        secret_key.encode('utf-8'),
        message.encode('utf-8'),
        hashlib.sha256
    ).digest()
    return base64.b64encode(signature).decode('utf-8')

@login_required
def user_bookings(request):
    if request.user.role != 'user':
        return redirect('home')
    
    bookings = Booking.objects.filter(user=request.user)
    
    # Check for expired payments
    for booking in bookings:
        if booking.status == 'Approved' and booking.is_payment_expired():
            booking.status = 'Cancelled'
            if booking.guide:
                booking.guide.availability = 'Available'
                booking.guide.save()
            booking.save()
    
    return render(request, 'user/bookings.html', {'bookings': bookings})

@login_required
def book_trek(request, trek_id):
    if request.user.role != 'user':
        return redirect('home')
    
    trek = get_object_or_404(Trek, pk=trek_id)
    available_guides = GuideProfile.objects.filter(availability='Available')
    
    if request.method == 'POST':
        guide2_id = request.POST.get('guide2')
        guide3_id = request.POST.get('guide3')
        booking = Booking(
            user=request.user,
            trek=trek,
            guide_id=request.POST.get('guide'),
            guide2_id=guide2_id if guide2_id else None,
            guide3_id=guide3_id if guide3_id else None,
            start_date=request.POST.get('start_date'),
            num_travellers=request.POST.get('num_travellers', 1),
            special_requests=request.POST.get('special_requests', ''),
            status='Pending',
            payment_status='Not Initiated'
        )
        booking.save()
        messages.success(request, 'Booking submitted! Waiting for guide approval.')
        return redirect('user_bookings')
    
    return render(request, 'user/book_trek.html', {'trek': trek, 'guides': available_guides})

def generate_esewa_signature(total_amount, transaction_uuid, product_code, secret_key):
    """Generate HMAC SHA256 signature for eSewa v2 API"""
    message = f"total_amount={total_amount},transaction_uuid={transaction_uuid},product_code={product_code}"
    signature = hmac.new(
        secret_key.encode('utf-8'),
        message.encode('utf-8'),
        hashlib.sha256
    ).digest()
    return base64.b64encode(signature).decode('utf-8')

@login_required
def payment_page(request, booking_id):
    """Handle payment initiation for approved bookings"""
    if request.user.role != 'user':
        return redirect('home')
    
    booking = get_object_or_404(Booking, pk=booking_id, user=request.user)
    
    # Payment allowed when booking is Approved OR Confirmed with partial payment
    if booking.status == 'Approved':
        pass  # First payment or retry after failure
    elif booking.status == 'Confirmed' and booking.payment_status == 'Partial Paid':
        pass  # Remaining payment
    else:
        messages.error(request, 'Payment not available for this booking')
        return redirect('user_bookings')
    
    # Check payment timeout for Approved bookings
    if booking.status == 'Approved' and booking.is_payment_expired():
        booking.status = 'Cancelled'
        if booking.guide:
            booking.guide.availability = 'Available'
            booking.guide.save()
        booking.save()
        messages.error(request, 'Payment time expired. Booking cancelled.')
        return redirect('user_bookings')
    
    # Calculate amounts
    total_cost = booking.trek.cost * booking.num_travellers
    min_payment = total_cost * Decimal('0.20')
    remaining_to_pay = total_cost - booking.paid_amount
    
    # Prevent payment if already fully paid
    if booking.payment_status == 'Paid':
        messages.info(request, 'This booking is already fully paid')
        return redirect('user_bookings')
    
    if request.method == 'POST':
        percentage = Decimal(request.POST.get('percentage', 0))
        
        # Validate percentage range
        if percentage < 20 or percentage > 100:
            messages.error(request, 'Payment must be between 20% and 100%')
            return render(request, 'user/payment.html', {
                'booking': booking,
                'total_cost': total_cost,
                'min_payment': min_payment,
                'remaining_amount': remaining_to_pay
            })
        
        # Calculate payment amount
        if booking.paid_amount == 0:
            # First payment - percentage of total
            payment_amount = (total_cost * percentage) / 100
            if payment_amount < min_payment:
                messages.error(request, 'First payment must be at least 20% of total cost')
                return render(request, 'user/payment.html', {
                    'booking': booking,
                    'total_cost': total_cost,
                    'min_payment': min_payment,
                    'remaining_amount': remaining_to_pay
                })
        else:
            # Remaining payment - percentage of remaining amount
            payment_amount = (remaining_to_pay * percentage) / 100
        
        # Prevent overpayment
        if payment_amount > remaining_to_pay:
            payment_amount = remaining_to_pay
        
        # Create Payment record
        try:
            # Use simple transaction ID
            transaction_id = f"TRK{booking.id}{int(timezone.now().timestamp())}"
            
            payment = Payment.objects.create(
                booking=booking,
                amount_paid=payment_amount,
                payment_status='Initiated',
                transaction_id=transaction_id
            )
            
            # eSewa v2 API parameters
            esewa_config = settings.ESEWA_CONFIG
            
            # Generate proper signature
            signature = generate_esewa_signature(
                total_amount=float(payment_amount),
                transaction_uuid=transaction_id,
                product_code=esewa_config['MERCHANT_CODE'],
                secret_key=esewa_config['SECRET_KEY']
            )
            
            context = {
                'booking': booking,
                'payment': payment,
                'amount': float(payment_amount),
                'tax_amount': 0,
                'product_service_charge': 0,
                'product_delivery_charge': 0,
                'total_amount': float(payment_amount),
                'transaction_uuid': transaction_id,
                'product_code': esewa_config['MERCHANT_CODE'],
                'success_url': f"{esewa_config['SUCCESS_URL']}{booking.id}/",
                'failure_url': f"{esewa_config['FAILURE_URL']}{booking.id}/",
                'signature': signature,
                'gateway_url': esewa_config['GATEWAY_URL']
            }
            
            return render(request, 'user/esewa_payment_v2.html', context)
            
        except Exception as e:
            logger.error(f"Payment creation failed for booking {booking_id}: {str(e)}")
            print(f"DEBUG: Payment error - {str(e)}")  # Console debug
            messages.error(request, 'Payment initiation failed. Please try again.')
            return redirect('user_bookings')
    
    return render(request, 'user/payment.html', {
        'booking': booking,
        'total_cost': total_cost,
        'min_payment': min_payment,
        'remaining_amount': remaining_to_pay
    })

@csrf_exempt
def payment_success(request, booking_id):
    """Handle eSewa success callback"""
    booking = get_object_or_404(Booking, pk=booking_id)
    
    # Debug: Print all GET parameters
    print(f"DEBUG: All GET params: {dict(request.GET)}")
    
    # Get eSewa response parameters
    oid = request.GET.get('oid') or request.GET.get('pid')  # Try both
    amt = request.GET.get('amt')
    refId = request.GET.get('refId')
    
    # Find the most recent initiated payment for this booking
    try:
        payment = Payment.objects.filter(
            booking=booking, 
            payment_status='Initiated'
        ).order_by('-created_at').first()
        
        if not payment:
            logger.error(f"No initiated payment found for booking {booking_id}")
            messages.error(request, 'Payment record not found')
            return redirect('user_bookings')
            
    except Exception as e:
        logger.error(f"Error finding payment for booking {booking_id}: {str(e)}")
        messages.error(request, 'Payment record not found')
        return redirect('user_bookings')
    
    # Verify payment with eSewa v2 API
    if amt and refId:
        esewa_config = settings.ESEWA_CONFIG
        verify_params = {
            'product_code': esewa_config['MERCHANT_CODE'],
            'total_amount': amt,
            'transaction_uuid': oid,
        }
        
        try:
            response = requests.get(
                esewa_config['VERIFY_URL'], 
                params=verify_params, 
                timeout=10
            )
            response_data = response.json()
            
            if response_data.get('status') != 'COMPLETE':
                logger.warning(f"eSewa verification failed: {response_data}")
                
        except Exception as e:
            logger.warning(f"eSewa verification error: {str(e)}")
    
    # Update payment record
    payment.payment_status = 'Success'
    payment.reference_id = refId
    payment.save()
    
    # Update booking amounts
    booking.paid_amount += payment.amount_paid
    total_cost = booking.trek.cost * booking.num_travellers
    booking.remaining_amount = total_cost - booking.paid_amount
    
    # Update booking status
    booking.status = 'Confirmed'
    
    # Update payment status based on remaining amount
    if booking.remaining_amount <= 0:
        booking.payment_status = 'Paid'
    else:
        booking.payment_status = 'Partial Paid'
    
    booking.save()
    
    # Update guide availability
    if booking.guide and booking.guide.availability != 'On a Trek':
        booking.guide.availability = 'On a Trek'
        booking.guide.save()
    
    logger.info(f"Payment successful for booking {booking_id}")
    messages.success(request, 'Payment successful! Your booking is confirmed.')
    return redirect('user_bookings')

@csrf_exempt
def payment_failure(request, booking_id):
    """Handle eSewa failure callback"""
    booking = get_object_or_404(Booking, pk=booking_id)
    
    # Get transaction ID from request
    pid = request.GET.get('pid')
    
    # Find and update payment record
    if pid:
        try:
            payment = Payment.objects.get(transaction_id=pid, booking=booking)
            payment.payment_status = 'Failed'
            payment.save()
            logger.info(f"Payment failed for transaction {pid}")
        except Payment.DoesNotExist:
            logger.error(f"Payment not found for failed transaction {pid}")
    
    # Update booking payment status to Failed
    booking.payment_status = 'Failed'
    booking.save()
    
    messages.error(request, 'Payment failed or cancelled. You can retry payment from your bookings page.')
    return redirect('user_bookings')

@login_required
def admin_bookings(request):
    if request.user.role == 'guide':
        bookings = Booking.objects.filter(guide__user=request.user)
    elif request.user.role in ['superadmin', 'admin']:
        bookings = Booking.objects.all()
    else:
        return redirect('home')
    
    return render(request, 'admin_panel/bookings.html', {'bookings': bookings})

@login_required
def update_booking_status(request, pk):
    if request.user.role not in ['superadmin', 'admin', 'guide']:
        return redirect('home')
    
    booking = get_object_or_404(Booking, pk=pk)
    
    if request.user.role == 'guide' and booking.guide.user != request.user:
        messages.error(request, 'Unauthorized')
        return redirect('admin_bookings')
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        
        # Admin/SuperAdmin can only cancel
        if request.user.role in ['superadmin', 'admin']:
            if new_status == 'Cancelled':
                booking.status = 'Cancelled'
                # Revert guide availability if booking was approved/confirmed
                if booking.guide and booking.status in ['Approved', 'Confirmed']:
                    booking.guide.availability = 'Available'
                    booking.guide.save()
                booking.save()
                messages.success(request, 'Booking cancelled by admin')
            else:
                messages.error(request, 'Admins can only cancel bookings')
        
        # Guide approval/cancellation logic
        elif request.user.role == 'guide':
            # Check guide availability
            guide_profile = booking.guide
            
            if guide_profile.availability != 'Available':
                messages.error(request, 'You must be Available to approve or cancel bookings')
                return redirect('admin_bookings')
            
            # Only allow actions on Pending bookings
            if booking.status != 'Pending':
                messages.error(request, f'Cannot modify {booking.status} booking')
                return redirect('admin_bookings')
            
            if new_status == 'Approved':
                booking.status = 'Approved'
                booking.approved_at = timezone.now()
                booking.save()
                
                # Immediately change guide availability
                guide_profile.availability = 'On a Trek'
                guide_profile.save()
                
                messages.success(request, 'Booking approved. Your status is now "On a Trek". Tourist can now make payment.')
            
            elif new_status == 'Cancelled':
                # Move to backup guide if available
                if booking.guide2:
                    booking.guide = booking.guide2
                    booking.guide2 = booking.guide3
                    booking.guide3 = None
                    booking.status = 'Pending'
                    messages.success(request, 'Booking forwarded to backup guide')
                elif booking.guide3:
                    booking.guide = booking.guide3
                    booking.guide3 = None
                    booking.status = 'Pending'
                    messages.success(request, 'Booking forwarded to backup guide')
                else:
                    booking.status = 'Cancelled'
                    messages.success(request, 'Booking cancelled - no backup guide available')
                booking.save()
    
    return redirect('admin_bookings')