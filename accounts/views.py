from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count
from .models import User
from treks.models import Trek
from bookings.models import Booking
from guides.models import GuideProfile
from recommendation.home_recommendation import get_home_recommendations
import re

def home(request):
    # Get personalized recommendations (6 treks)
    recommended_treks = get_home_recommendations(request.user)
    
    # Get featured treks (admin selected)
    featured_treks = Trek.objects.filter(featured=True)[:6]
    
    return render(request, 'user/home.html', {
        'recommended_treks': recommended_treks,
        'featured_treks': featured_treks
    })

def about_us(request):
    return render(request, 'user/about.html')

def contact_us(request):
    return render(request, 'user/contact.html')

def terms_conditions(request):
    return render(request, 'user/terms.html')

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        
        errors = {}
        form_data = {'username': username, 'password': password}
        
        if not username or not password:
            errors['general'] = 'Username and password are required'
            form_data['errors'] = errors
            return render(request, 'auth/login.html', form_data)
        
        user = authenticate(request, username=username, password=password)
        if user and user.role == 'user':
            login(request, user)
            return redirect('home')
        
        errors['general'] = 'Invalid username or password'
        form_data['errors'] = errors
        return render(request, 'auth/login.html', form_data)
    
    return render(request, 'auth/login.html')

def user_register(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        email = request.POST.get('email', '').strip().lower()
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')
        
        errors = {}
        form_data = {
            'full_name': full_name,
            'email': email,
            'username': username,
            'password': password,
            'confirm_password': confirm_password
        }
        
        # Validate full name
        if not full_name or len(full_name) < 2:
            errors['full_name'] = 'Full name must be at least 2 characters'
        
        # Validate email format
        email_pattern = r'^[a-zA-Z][a-zA-Z0-9._-]{2,}@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not email:
            errors['email'] = 'Email is required'
        elif not re.match(email_pattern, email):
            errors['email'] = 'Email must start with a letter, have at least 3 characters before @, and include a valid domain'
        elif User.objects.filter(email=email).exists():
            errors['email'] = 'This email is already registered'
        
        # Validate username
        if not username or len(username) < 3:
            errors['username'] = 'Username must be at least 3 characters'
        elif username[0].isdigit():
            errors['username'] = 'Username cannot start with a number'
        elif not re.match(r'^[a-zA-Z0-9_]+$', username):
            errors['username'] = 'Username can only contain letters, numbers, and underscores'
        elif User.objects.filter(username=username).exists():
            errors['username'] = 'This username is already taken'
        
        # Validate password match
        if password != confirm_password:
            errors['confirm_password'] = 'Passwords do not match'
        
        # Validate password strength
        if len(password) < 8:
            errors['password'] = 'Password must be at least 8 characters long'
        elif not re.search(r'[a-z]', password):
            errors['password'] = 'Password must contain at least one lowercase letter'
        elif not re.search(r'[A-Z]', password):
            errors['password'] = 'Password must contain at least one uppercase letter'
        elif not re.search(r'\d', password):
            errors['password'] = 'Password must contain at least one number'
        elif not re.search(r'[@$!%*?&#]', password):
            errors['password'] = 'Password must contain at least one special character (@$!%*?&#)'
        
        if errors:
            form_data['errors'] = errors
            return render(request, 'auth/register.html', form_data)
        
        # Create user
        User.objects.create_user(username=username, email=email, password=password, full_name=full_name, role='user')
        messages.success(request, 'Registration successful! Please login.')
        return redirect('login')
    
    return render(request, 'auth/register.html')

def user_logout(request):
    logout(request)
    return redirect('home')

def admin_logout(request):
    logout(request)
    return redirect('admin_login')

@login_required
def user_profile(request):
    if request.method == 'POST':
        request.user.full_name = request.POST.get('full_name')
        request.user.email = request.POST.get('email')
        request.user.username = request.POST.get('username')
        
        new_password = request.POST.get('new_password')
        if new_password:
            if not re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$', new_password):
                messages.error(request, 'Invalid password format')
                return redirect('user_profile')
            request.user.set_password(new_password)
        
        request.user.save()
        messages.success(request, 'Profile updated')
        return redirect('user_profile')
    
    return render(request, 'user/profile.html')

def admin_login(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        
        errors = {}
        form_data = {'username': username, 'password': password}
        
        if not username or not password:
            errors['general'] = 'Username and password are required'
            form_data['errors'] = errors
            return render(request, 'auth/admin_login.html', form_data)
        
        user = authenticate(request, username=username, password=password)
        if user and user.role in ['superadmin', 'admin', 'guide']:
            login(request, user)
            return redirect('admin_dashboard')
        
        errors['general'] = 'Invalid username or password'
        form_data['errors'] = errors
        return render(request, 'auth/admin_login.html', form_data)
    
    return render(request, 'auth/admin_login.html')

@login_required
def admin_dashboard(request):
    if request.user.role not in ['superadmin', 'admin', 'guide']:
        return redirect('home')

    from django.db.models import Sum
    from django.utils import timezone

    now = timezone.now()
    today = now.date()

    bookings_qs = Booking.objects.exclude(payment_status='Not Initiated')

    revenue_total = bookings_qs.aggregate(t=Sum('paid_amount'))['t'] or 0
    revenue_month = bookings_qs.filter(
        created_at__year=now.year, created_at__month=now.month
    ).aggregate(t=Sum('paid_amount'))['t'] or 0
    revenue_today = bookings_qs.filter(
        created_at__date=today
    ).aggregate(t=Sum('paid_amount'))['t'] or 0

    context = {
        'total_treks': Trek.objects.count(),
        'total_bookings': Booking.objects.count() if request.user.role != 'guide' else Booking.objects.filter(guide__user=request.user).count(),
        'total_users': User.objects.filter(role='user').count() if request.user.role != 'guide' else 0,
        'total_guides': GuideProfile.objects.count() if request.user.role != 'guide' else 0,
        'recent_bookings': Booking.objects.all()[:10] if request.user.role != 'guide' else Booking.objects.filter(guide__user=request.user)[:10],
        'revenue_total': revenue_total,
        'revenue_month': revenue_month,
        'revenue_today': revenue_today,
    }
    return render(request, 'admin_panel/dashboard.html', context)

@login_required
def admin_change_password(request):
    if request.user.role not in ['superadmin', 'admin', 'guide']:
        return redirect('home')
    
    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        if new_password != confirm_password:
            messages.error(request, 'Passwords do not match')
            return redirect('admin_change_password')
        
        if not re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$', new_password):
            messages.error(request, 'Invalid password format')
            return redirect('admin_change_password')
        
        request.user.set_password(new_password)
        request.user.save()
        messages.success(request, 'Password changed successfully')
        return redirect('admin_login')
    
    return render(request, 'admin_panel/change_password.html')

@login_required
def manage_admins(request):
    if request.user.role != 'superadmin':
        return redirect('admin_dashboard')
    
    admins = User.objects.filter(role='admin')
    return render(request, 'admin_panel/manage_admins.html', {'admins': admins})

@login_required
def add_admin(request):
    if request.user.role != 'superadmin':
        return redirect('admin_dashboard')
    
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        if password != confirm_password:
            messages.error(request, 'Passwords do not match')
            return redirect('add_admin')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return redirect('add_admin')
        
        User.objects.create_user(username=username, password=password, full_name=full_name, role='admin')
        messages.success(request, 'Admin added successfully')
        return redirect('manage_admins')
    
    return render(request, 'admin_panel/add_admin.html')

@login_required
def delete_admin(request, pk):
    if request.user.role != 'superadmin':
        return redirect('admin_dashboard')

    admin_user = get_object_or_404(User, pk=pk, role='admin')
    admin_user.delete()
    messages.success(request, 'Admin deleted successfully')
    return redirect('manage_admins')

@login_required
def view_users(request):
    if request.user.role not in ['superadmin', 'admin']:
        return redirect('admin_dashboard')
    
    users = User.objects.filter(role='user')
    return render(request, 'admin_panel/view_users.html', {'users': users})
