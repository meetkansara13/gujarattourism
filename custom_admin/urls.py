from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('login/', views.custom_admin_login, name='custom_admin_login'),
    path('dashboard/', views.dashboard, name='custom_admin_dashboard'),
    path('destinations/', views.destination_list, name='destination_list'),
    path('destinations/add/', views.destination_add, name='destination_add'),
    path('destinations/<int:pk>/edit/', views.destination_edit, name='destination_edit'),
    path('destinations/<int:pk>/delete/', views.destination_delete, name='destination_delete'),
    path('manage-bookings/', views.manage_bookings, name='manage_bookings'),
    path("edit-booking/<int:booking_id>/", views.edit_booking, name="edit_booking"), 
    path('delete-booking/<int:booking_id>/', views.delete_booking, name='delete_booking'),
    path('manage-users/', views.manage_users, name='manage_users'),
    path('edit-user/<int:user_id>/', views.edit_user, name='edit_user'),
    path('delete-user/<int:user_id>/', views.delete_user, name='delete_user'),
    path('manage-tours/', views.manage_tours, name='manage_tours'),
    path('toggle-staff/<int:user_id>/', views.toggle_staff, name='toggle_staff'),


]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
