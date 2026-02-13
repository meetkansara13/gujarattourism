from django.contrib import admin
from .models import Destination, Booking, HeritageSite, HeritageTour, TourRoute, HeritageTourBooking

admin.site.register(Destination)
admin.site.register(Booking)

class TourRouteInline(admin.TabularInline):
    model = TourRoute
    extra = 1

@admin.register(HeritageTour)
class HeritageTourAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'duration_days', 'featured')
    inlines = [TourRouteInline]

@admin.register(HeritageSite)
class HeritageSiteAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_national_monument')

@admin.register(HeritageTourBooking)
class HeritageTourBookingAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'tour', 'phone', 'price', 'approved', 'created_at')
    list_filter = ('approved', 'created_at', 'tour')
    search_fields = ('full_name', 'phone', 'email')
