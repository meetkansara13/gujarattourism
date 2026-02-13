from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone


class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    destination = models.ForeignKey('Destination', on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'destination')

    def __str__(self):
        return f"{self.user} -> {self.destination}"
    
class Destination(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    short_description = models.CharField(max_length=255)
    image = models.ImageField(upload_to='destinations/')
    featured = models.BooleanField(default=False)
    

    def __str__(self):
        return self.name

class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    full_name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    destination = models.ForeignKey("Destination", on_delete=models.CASCADE)
    booking_date = models.DateTimeField(default=timezone.now, null=True, blank=True)
    travel_date = models.DateField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00) 
    number_of_people = models.IntegerField()
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    

    def __str__(self):
        return f"{self.full_name} - {self.destination.name} ({self.travel_date})"


    



class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    savings = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    profile_pic = models.ImageField(upload_to="profile_pics/", default="profile_pics/default.png")
    wishlist = models.ManyToManyField(Destination, blank=True)

    def __str__(self):
        return self.user.username


# ✅ Signals should come after Profile is defined
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    Profile.objects.get_or_create(user=instance)
    instance.profile.save()



class HeritageSite(models.Model):
    name = models.CharField(max_length=200)
    short_desc = models.CharField(max_length=300, blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='heritage_images/', blank=True, null=True)
    is_national_monument = models.BooleanField(default=False)
    # optional coords for map
    lat = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    lng = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)

    class Meta:
        verbose_name = "Heritage Site"
        verbose_name_plural = "Heritage Sites"

    def __str__(self):
        return self.name


class HeritageTour(models.Model):
    name = models.CharField(max_length=200)
    short_desc = models.CharField(max_length=300, blank=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration_days = models.PositiveIntegerField(default=1)
    image = models.ImageField(upload_to='tour_images/', blank=True, null=True)
    # is this a featured tour?
    featured = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} — ₹{self.price}"


class TourRoute(models.Model):
    tour = models.ForeignKey(HeritageTour, on_delete=models.CASCADE, related_name='routes')
    order = models.PositiveIntegerField(default=0)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    # optional coords for each route stop
    lat = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    lng = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)

    class Meta:
        ordering = ['order']
        verbose_name = "Tour Route Stop"
        verbose_name_plural = "Tour Route Stops"

    def __str__(self):
        return f"{self.tour.name} — {self.order} — {self.title}"


class HeritageTourBooking(models.Model):
    tour = models.ForeignKey(HeritageTour, on_delete=models.SET_NULL, null=True, related_name='bookings')
    full_name = models.CharField(max_length=200)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=False)  # admin can toggle to approve

    def __str__(self):
        return f"{self.full_name} — {self.tour.name if self.tour else 'No tour'} — {self.created_at:%Y-%m-%d}"
