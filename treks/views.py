from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Min, Max   # <-- ADDED
from .models import Trek
from recommendation.utils import recommend_treks

def explore(request):
    treks = Trek.objects.all()
    
    # Filters
    region = request.GET.get('region', '')
    difficulty = request.GET.get('difficulty', '')
    min_cost = request.GET.get('min_cost', '')
    max_cost = request.GET.get('max_cost', '')
    search = request.GET.get('search', '')
    
    if region:
        treks = treks.filter(region=region)
    if difficulty:
        treks = treks.filter(difficulty=difficulty)
    if min_cost:
        treks = treks.filter(cost__gte=min_cost)
    if max_cost:
        treks = treks.filter(cost__lte=max_cost)
    if search:
        treks = treks.filter(title__icontains=search)
    
    context = {
        'treks': treks,
        'region': region,
        'difficulty': difficulty,
        'min_cost': min_cost,
        'max_cost': max_cost,
        'search': search,
    }
    return render(request, 'user/explore.html', context)

def smart_finder(request):

    # ---- ADDED: Fetch min & max cost from Trek table ----
    min_cost = Trek.objects.aggregate(Min('cost'))['cost__min']
    max_cost = Trek.objects.aggregate(Max('cost'))['cost__max']
    # ------------------------------------------------------

    if request.method == 'POST':
        user_prefs = {
            'min_budget': int(request.POST.get('min_budget', min_cost)),
            'max_budget': int(request.POST.get('max_budget', max_cost)),
            'max_duration': int(request.POST.get('max_duration', 50)),
            'max_altitude': int(request.POST.get('max_altitude', 6500)),
            'difficulty': request.POST.get('difficulty', 'Any'),
            'region': request.POST.get('region', 'Any'),
            'seasons': request.POST.getlist('seasons'),
            'interests': request.POST.getlist('interests'),
        }
        
        treks = Trek.objects.all()
        results = recommend_treks(user_prefs, treks)
        
        return render(request, 'user/smart_finder_results.html', {'results': results})
    
    # ---- ADDED: Send min_cost & max_cost to template ----
    return render(request, 'user/smart_finder.html', {
        'min_cost': min_cost,
        'max_cost': max_cost,
    })
    # ------------------------------------------------------

def trek_detail(request, pk):
    trek = get_object_or_404(Trek, pk=pk)
    return render(request, 'user/trek_detail.html', {'trek': trek})

@login_required
def admin_treks(request):
    if request.user.role not in ['superadmin', 'admin']:
        return redirect('admin_dashboard')
    
    treks = Trek.objects.all()
    return render(request, 'admin_panel/treks.html', {'treks': treks})

@login_required
def create_trek(request):
    if request.user.role not in ['superadmin', 'admin']:
        return redirect('admin_dashboard')
    
    if request.method == 'POST':
        trek = Trek(
            title=request.POST.get('title'),
            region=request.POST.get('region'),
            min_duration=request.POST.get('min_duration'),
            max_duration=request.POST.get('max_duration'),
            max_altitude=request.POST.get('max_altitude'),
            season_spring='spring' in request.POST.getlist('seasons'),
            season_summer='summer' in request.POST.getlist('seasons'),
            season_autumn='autumn' in request.POST.getlist('seasons'),
            season_winter='winter' in request.POST.getlist('seasons'),
            difficulty=request.POST.get('difficulty'),
            interest_scenic='scenic' in request.POST.getlist('interests'),
            interest_adventure='adventure' in request.POST.getlist('interests'),
            interest_photography='photography' in request.POST.getlist('interests'),
            interest_wildlife='wildlife' in request.POST.getlist('interests'),
            interest_cultural='cultural' in request.POST.getlist('interests'),
            interest_family='family' in request.POST.getlist('interests'),
            description=request.POST.get('description'),
            cost=request.POST.get('cost'),
            featured='featured' in request.POST,
            featured_image=request.FILES.get('featured_image')
        )
        trek.save()
        messages.success(request, 'Trek created successfully')
        return redirect('admin_treks')
    
    return render(request, 'admin_panel/create_trek.html')

@login_required
def edit_trek(request, pk):
    if request.user.role not in ['superadmin', 'admin']:
        return redirect('admin_dashboard')
    
    trek = get_object_or_404(Trek, pk=pk)
    
    if request.method == 'POST':
        trek.title = request.POST.get('title')
        trek.region = request.POST.get('region')
        trek.min_duration = request.POST.get('min_duration')
        trek.max_duration = request.POST.get('max_duration')
        trek.max_altitude = request.POST.get('max_altitude')
        trek.season_spring = 'spring' in request.POST.getlist('seasons')
        trek.season_summer = 'summer' in request.POST.getlist('seasons')
        trek.season_autumn = 'autumn' in request.POST.getlist('seasons')
        trek.season_winter = 'winter' in request.POST.getlist('seasons')
        trek.difficulty = request.POST.get('difficulty')
        trek.interest_scenic = 'scenic' in request.POST.getlist('interests')
        trek.interest_adventure = 'adventure' in request.POST.getlist('interests')
        trek.interest_photography = 'photography' in request.POST.getlist('interests')
        trek.interest_wildlife = 'wildlife' in request.POST.getlist('interests')
        trek.interest_cultural = 'cultural' in request.POST.getlist('interests')
        trek.interest_family = 'family' in request.POST.getlist('interests')
        trek.description = request.POST.get('description')
        trek.cost = request.POST.get('cost')
        trek.featured = 'featured' in request.POST
        if request.FILES.get('featured_image'):
            trek.featured_image = request.FILES.get('featured_image')
        trek.save()
        messages.success(request, 'Trek updated successfully')
        return redirect('admin_treks')
    
    return render(request, 'admin_panel/edit_trek.html', {'trek': trek})

@login_required
def delete_trek(request, pk):
    if request.user.role not in ['superadmin', 'admin']:
        return redirect('admin_dashboard')
    
    trek = get_object_or_404(Trek, pk=pk)
    trek.delete()
    messages.success(request, 'Trek deleted successfully')
    return redirect('admin_treks')