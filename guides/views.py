from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import GuideProfile
from accounts.models import User

def guides_list(request):
    guides = GuideProfile.objects.all()
    
    # Filters
    experience = request.GET.get('experience', '')
    availability = request.GET.get('availability', '')
    
    if experience:
        guides = guides.filter(experience__gte=experience)
    if availability:
        guides = guides.filter(availability=availability)
    
    context = {
        'guides': guides,
        'experience': experience,
        'availability': availability,
    }
    return render(request, 'user/guides.html', context)

@login_required
def admin_guides(request):
    if request.user.role not in ['superadmin', 'admin']:
        return redirect('admin_dashboard')
    
    guides = User.objects.filter(role='guide')
    return render(request, 'admin_panel/guides.html', {'guides': guides})

@login_required
def add_guide(request):
    if request.user.role not in ['superadmin', 'admin']:
        return redirect('admin_dashboard')
    
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        if password != confirm_password:
            messages.error(request, 'Passwords do not match')
            return redirect('add_guide')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return redirect('add_guide')
        
        User.objects.create_user(username=username, password=password, full_name=full_name, role='guide')
        messages.success(request, 'Guide added successfully')
        return redirect('admin_guides')
    
    return render(request, 'admin_panel/add_guide.html')

@login_required
def manage_guide_profile(request):
    if request.user.role != 'guide':
        return redirect('admin_dashboard')
    
    try:
        profile = request.user.guide_profile
    except GuideProfile.DoesNotExist:
        profile = None
    
    if request.method == 'POST':
        if profile:
            profile.email = request.POST.get('email')
            profile.phone = request.POST.get('phone')
            profile.experience = request.POST.get('experience')
            profile.languages = request.POST.get('languages')
            profile.bio = request.POST.get('bio')
            profile.availability = request.POST.get('availability')
            if request.FILES.get('profile_picture'):
                profile.profile_picture = request.FILES.get('profile_picture')
            profile.save()
            messages.success(request, 'Profile updated successfully')
        else:
            profile = GuideProfile(
                user=request.user,
                email=request.POST.get('email'),
                phone=request.POST.get('phone'),
                experience=request.POST.get('experience'),
                languages=request.POST.get('languages'),
                bio=request.POST.get('bio'),
                availability=request.POST.get('availability'),
            )
            if request.FILES.get('profile_picture'):
                profile.profile_picture = request.FILES.get('profile_picture')
            profile.save()
            messages.success(request, 'Profile created successfully')
        
        return redirect('manage_guide_profile')
    
    return render(request, 'admin_panel/guide_profile.html', {'profile': profile})

@login_required
def delete_guide(request, pk):
    if request.user.role not in ['superadmin', 'admin']:
        return redirect('admin_dashboard')

    guide_user = get_object_or_404(User, pk=pk, role='guide')
    guide_user.delete()
    messages.success(request, 'Guide deleted successfully')
    return redirect('admin_guides')

@login_required
def delete_guide_profile(request):
    if request.user.role != 'guide':
        return redirect('admin_dashboard')
    
    try:
        profile = request.user.guide_profile
        profile.delete()
        messages.success(request, 'Profile deleted successfully')
    except GuideProfile.DoesNotExist:
        messages.error(request, 'No profile found')
    
    return redirect('manage_guide_profile')
