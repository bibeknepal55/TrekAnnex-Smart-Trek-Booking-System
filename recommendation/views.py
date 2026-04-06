from django.shortcuts import render
from django.db.models import Min, Max
from .models import Trek

def smart_finder(request):
    min_cost = Trek.objects.aggregate(Min('cost'))['cost__min']
    max_cost = Trek.objects.aggregate(Max('cost'))['cost__max']

    return render(request, 'user/smart_finder.html', {
        'min_cost': min_cost,
        'max_cost': max_cost
    })