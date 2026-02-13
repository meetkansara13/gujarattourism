from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import authenticate, login
from django.contrib import messages
from tourism.models import Destination, Booking
from tourism.forms import DestinationForm
from django.contrib.auth.models import User
from tourism.models import Booking



def edit_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)

    if request.method == "POST":
        # Example: update booking status
        booking.status = request.POST.get("status")
        booking.save()
        return redirect("manage_bookings")

def delete_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    booking.delete()
    return redirect('manage_bookings')

    return render(request, "custom_admin/edit_booking.html", {"booking": booking})
def custom_admin_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None and user.is_staff:
            login(request, user)
            return redirect('custom_admin_dashboard')
        else:
            messages.error(request, "Invalid credentials or unauthorized user.")
    
    return render(request, 'custom_admin/login.html')


@user_passes_test(lambda u: u.is_staff, login_url='custom_admin_login')
def dashboard(request):
    total_destinations = Destination.objects.count()
    total_bookings = Booking.objects.count()
    return render(request, 'custom_admin/dashboard.html', {
        'total_destinations': total_destinations,
        'total_bookings': total_bookings
    })


@user_passes_test(lambda u: u.is_staff)
def manage_bookings(request):
    bookings = Booking.objects.all().order_by("-created_at")

    # ✅ Handle status update
    if request.method == "POST":
        booking_id = request.POST.get("booking_id")
        action = request.POST.get("action")
        booking = get_object_or_404(Booking, id=booking_id)

        if action == "confirm":
            booking.status = "confirmed"
            messages.success(request, f"Booking for {booking.full_name} confirmed.")
        elif action == "cancel":
            booking.status = "cancelled"
            messages.warning(request, f"Booking for {booking.full_name} cancelled.")
        elif action == "pending":
            booking.status = "pending"
            messages.info(request, f"Booking for {booking.full_name} marked as pending.")
        elif action == "delete":
            booking.delete()
            messages.error(request, "Booking deleted successfully.")
            return redirect("manage_bookings")

        booking.save()
        return redirect("manage_bookings")

    return render(request, "custom_admin/manage_bookings.html", {"bookings": bookings})






@user_passes_test(lambda u: u.is_staff)
def manage_tours(request):
    return redirect('destination_list')


@user_passes_test(lambda u: u.is_staff)
def destination_list(request):
    destinations = Destination.objects.all()
    return render(request, 'destination_list.html', {'destinations': destinations})


@user_passes_test(lambda u: u.is_staff)
def destination_add(request):
    if request.method == "POST":
        form = DestinationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('destination_list')
    else:
        form = DestinationForm()
    return render(request, 'custom_admin/destination_form.html', {'form': form, 'title': 'Add Destination'})


@user_passes_test(lambda u: u.is_staff)
def destination_edit(request, pk):
    dest = get_object_or_404(Destination, pk=pk)
    if request.method == "POST":
        form = DestinationForm(request.POST, request.FILES, instance=dest)
        if form.is_valid():
            form.save()
            return redirect('destination_list')
    else:
        form = DestinationForm(instance=dest)
    return render(request, 'custom_admin/destination_form.html', {'form': form, 'title': 'Edit Destination'})


@user_passes_test(lambda u: u.is_staff)
def destination_delete(request, pk):
    dest = get_object_or_404(Destination, pk=pk)
    if request.method == "POST":
        dest.delete()
        return redirect('destination_list')
    return render(request, 'custom_admin/confirm_delete.html', {'object': dest})

# ------------------ MANAGE USERS ------------------
@user_passes_test(lambda u: u.is_staff)
def manage_users(request):
    users = User.objects.all().order_by("id")
    return render(request, "custom_admin/manage_users.html", {"users": users})


# ------------------ EDIT USER ------------------
@user_passes_test(lambda u: u.is_staff)
def edit_user(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")

        # Basic validation
        if not username or not email:
            messages.error(request, "Username and Email are required.")
            return redirect("edit_user", user_id=user_id)

        # Update fields
        user.username = username
        user.email = email
        user.first_name = first_name
        user.last_name = last_name
        user.save()

        messages.success(request, "User updated successfully!")
        return redirect("manage_users")

    return render(request, "custom_admin/edit_user.html", {"user": user})


# ------------------ DELETE USER ------------------
@user_passes_test(lambda u: u.is_staff)
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)

    # Prevent deleting superuser
    if user.is_superuser:
        messages.error(request, "❌ Cannot delete a superuser!")
        return redirect("manage_users")

    user.delete()
    messages.success(request, "User deleted successfully.")
    return redirect("manage_users")

@user_passes_test(lambda u: u.is_staff)
def toggle_staff(request, user_id):
    user = get_object_or_404(User, id=user_id)

    # Prevent admin from removing their own staff role
    if request.user.id == user.id:
        messages.error(request, "You cannot change your own staff status.")
        return redirect("manage_users")

    # Toggle staff flag
    user.is_staff = not user.is_staff
    user.save()

    if user.is_staff:
        messages.success(request, f"{user.username} is now a Staff Member.")
    else:
        messages.success(request, f"{user.username} is no longer Staff.")

    return redirect("manage_users")
