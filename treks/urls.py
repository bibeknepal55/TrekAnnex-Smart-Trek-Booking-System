from django.urls import path
from . import views

urlpatterns = [
    path('explore/', views.explore, name='explore'),
    path('smart-finder/', views.smart_finder, name='smart_finder'),
    path('trek/<int:pk>/', views.trek_detail, name='trek_detail'),
    
    # Admin
    path('admin/treks/', views.admin_treks, name='admin_treks'),
    path('admin/treks/create/', views.create_trek, name='create_trek'),
    path('admin/treks/edit/<int:pk>/', views.edit_trek, name='edit_trek'),
    path('admin/treks/delete/<int:pk>/', views.delete_trek, name='delete_trek'),
]
