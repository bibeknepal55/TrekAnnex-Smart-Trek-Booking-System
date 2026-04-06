from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.user_login, name='login'),
    path('register/', views.user_register, name='register'),
    path('logout/', views.user_logout, name='logout'),
    path('admin/logout/', views.admin_logout, name='admin_logout'),
    path('profile/', views.user_profile, name='user_profile'),
    path('about/', views.about_us, name='about_us'),
    path('contact/', views.contact_us, name='contact_us'),
    path('terms/', views.terms_conditions, name='terms_conditions'),
    
    # Admin Panel
    path('admin-login/', views.admin_login, name='admin_login'),
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/change-password/', views.admin_change_password, name='admin_change_password'),
    path('admin/manage-admins/', views.manage_admins, name='manage_admins'),
    path('admin/add-admin/', views.add_admin, name='add_admin'),
    path('admin/delete-admin/<int:pk>/', views.delete_admin, name='delete_admin'),
    path('admin/view-users/', views.view_users, name='view_users'),
]
