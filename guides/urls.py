from django.urls import path
from . import views

urlpatterns = [
    path('guides/', views.guides_list, name='guides_list'),
    
    # Admin
    path('admin/guides/', views.admin_guides, name='admin_guides'),
    path('admin/guides/add/', views.add_guide, name='add_guide'),
    path('admin/guides/profile/', views.manage_guide_profile, name='manage_guide_profile'),
    path('admin/guides/profile/delete/', views.delete_guide_profile, name='delete_guide_profile'),
    path('admin/guides/<int:pk>/delete/', views.delete_guide, name='delete_guide'),
]
