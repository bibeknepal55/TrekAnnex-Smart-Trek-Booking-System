from django.urls import path
from . import views

urlpatterns = [
    path('bookings/', views.user_bookings, name='user_bookings'),
    path('book/<int:trek_id>/', views.book_trek, name='book_trek'),
    path('payment/<int:booking_id>/', views.payment_page, name='payment_page'),
    path('payment/success/<int:booking_id>/', views.payment_success, name='payment_success'),
    path('payment/failure/<int:booking_id>/', views.payment_failure, name='payment_failure'),
    
    # Admin
    path('admin/bookings/', views.admin_bookings, name='admin_bookings'),
    path('admin/bookings/update/<int:pk>/', views.update_booking_status, name='update_booking_status'),
]
