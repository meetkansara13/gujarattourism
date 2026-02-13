from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.shortcuts import render, get_object_or_404, redirect
from .models import Destination
from .forms import DestinationForm
from .models import Booking
from .forms import BookingForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import login
from django.contrib.auth.models import User
from .models import Profile
from django.core.mail import send_mail
from .forms import ProfileForm
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponseBadRequest
from .models import HeritageSite, HeritageTour, TourRoute, HeritageTourBooking
from django.views.decorators.http import require_POST
import os, json
import random
import google.generativeai as genai
from decimal import Decimal
import razorpay
from .forms import EditProfileForm
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from openai import OpenAI


@login_required
def edit_profile(request):
    profile = request.user.profile  

    if request.method == "POST":
        form = EditProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile')  
    else:
        form = EditProfileForm(instance=profile)

    return render(request, 'edit_profile.html', {'form': form})



@login_required
def add_wishlist(request, id):
    destination = get_object_or_404(Destination, id=id)
    request.user.profile.wishlist.add(destination)
    return redirect('destinations-static')

@login_required
def remove_wishlist(request, id):
    destination = get_object_or_404(Destination, id=id)
    request.user.profile.wishlist.remove(destination)
    return redirect('destinations-static')

@login_required
def my_wishlist(request):
    items = request.user.profile.wishlist.all()
    return render(request, 'wishlist.html', {'items': items})


@login_required
def profile(request):
    # Razorpay client
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

    # Create a payment order (₹500 example)
    payment = client.order.create({
        "amount": 50000,   # amount in paise (₹500)
        "currency": "INR",
        "payment_capture": "1"
    })

    context = {
        "user": request.user,
        "razorpay_key": settings.RAZORPAY_KEY_ID,
        "order_id": payment["id"],
        "amount": 500,  # show rupees in template
    }
    return render(request, "profile.html", context)
def heritage_page(request):
    sites = HeritageSite.objects.all()
    tours = HeritageTour.objects.prefetch_related('routes').all()
    # featured content
    featured_tours = tours.filter(featured=True)
    context = {
        'sites': sites,
        'tours': tours,
        'featured_tours': featured_tours,
    }
    return render(request, 'heritage.html', context)


from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404
import json
from .models import HeritageTour, HeritageTourBooking

@login_required
@require_POST
def book_heritage_tour(request):
    # Check if user is logged in
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Login required to book.'}, status=401)

    # Get POST data (support both form-data and raw JSON)
    try:
        data = request.POST or json.loads(request.body.decode('utf-8') or '{}')
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid request data.'}, status=400)

    tour_id = data.get('tour_id')
    full_name = data.get('full_name')
    phone = data.get('phone')
    email = data.get('email', '')
    price = data.get('price')
    notes = data.get('notes', '')

    # Required fields check
    if not (tour_id and full_name and phone and price):
        return JsonResponse({'success': False, 'error': 'Missing required fields.'}, status=400)

    # Fetch tour
    tour = get_object_or_404(HeritageTour, id=tour_id)

    # Create booking linked to user
    booking = HeritageTourBooking.objects.create(
        tour=tour,
        full_name=full_name,
        phone=phone,
        email=email,
        price=price,
        notes=notes,
        user=request.user,  # store logged-in user
        approved=False
    )

    return JsonResponse({
        'success': True,
        'message': "heritagely approven",
        'booking_id': booking.id
    })


@login_required
def contact_view(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        subject = request.POST.get("subject")
        message = request.POST.get("message")

        full_message = f"""
        You have a new message from your website contact form:

        Name: {name}
        Email: {email}
        Subject: {subject}

        Message:
        {message}
        """

        try:
            send_mail(
                subject=f"Contact Form: {subject}",
                message=full_message,
                from_email="knowgujinfo@gmail.com",     # always from your Gmail
                recipient_list=["knowgujinfo@gmail.com"], # goes to your inbox
                fail_silently=False,
            )
            messages.success(request, "Your message has been sent successfully!")
        except Exception as e:
            messages.error(request, f"Error sending message: {e}")

        return redirect("contact")  # adjust if your URL name is different

    return render(request, "contact.html")
def home(request):
    return render(request, 'index.html')


def signup_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Validate unique username and email
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
        elif User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered. Please log in instead.")
        else:
            # Create and login new user
            user = User.objects.create_user(username=username, email=email, password=password)
            login(request, user)  # Auto-login after signup
            messages.success(request, "Account created successfully!")
            return redirect('home')

    return render(request, 'signup.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect('home')  # Redirect to homepage (or profile)
        else:
            messages.error(request, "Invalid username or password. Please try again or sign up first.")

    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    return redirect('login')

def forgot_password_view(request):
    if request.method == "POST":
        email = request.POST.get("email")

        try:
            # Check if user exists
            user = User.objects.get(email=email)

            # Generate 6-digit OTP
            otp = random.randint(100000, 999999)

            # Save OTP in session (or database if you prefer)
            request.session['reset_email'] = email
            request.session['reset_otp'] = str(otp)

            # Send OTP to user’s email
            send_mail(
                subject="Password Reset Code - Gujarat Tourism",
                message=f"Your password reset code is: {otp}\n\nUse this code to reset your password.",
                from_email="knowgujinfo@gmail.com",  # your app email
                recipient_list=[email],
                fail_silently=False,
            )

            messages.success(request, "A recovery code has been sent to your email.")
            return redirect("verify_code")  # redirect to OTP verification page

        except User.DoesNotExist:
            messages.error(request, "This email is not registered.")

    return render(request, "forgot_password.html")

def destination_list(request):
    destinations = Destination.objects.all()
    return render(request, 'destination_list.html', {'destinations': destinations})

def destination_create(request):
    if request.method == 'POST':
        form = DestinationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('destination-list')
    else:
        form = DestinationForm()
    return render(request, 'destination_form.html', {'form': form})

def pricing_view(request):
    # Fetch all destinations
    destinations = Destination.objects.all()
    return render(request, 'pricing.html', {'destinations': destinations})

def destination_update(request, pk):
    destination = get_object_or_404(Destination, pk=pk)
    form = DestinationForm(request.POST or None, request.FILES or None, instance=destination)
    if form.is_valid():
        form.save()
        return redirect('destination-list')
    return render(request, 'destination_form.html', {'form': form})

def destination_delete(request, pk):
    destination = get_object_or_404(Destination, pk=pk)
    if request.method == 'POST':
        destination.delete()
        return redirect('destination-list')
    return render(request, 'destination_confirm_delete.html', {'destination': destination})

def destination_static(request):
    destinations = Destination.objects.all().order_by('id')
    paginator = Paginator(destinations, 4)  # 6 per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)  # Get current page

    return render(request, 'destinations.html', {'page_obj': page_obj})

def destination_detail(request, pk):
    destination = get_object_or_404(Destination, pk=pk)
    return render(request, 'destination_detail.html', {'destination': destination})


@login_required
def profile_view(request):
    profile = None
    if hasattr(request.user, 'profile'):  # If Profile model exists
        profile = request.user.profile

    return render(request, 'profile.html', {
        'user': request.user,
        'profile': profile
    })

@login_required
def edit_profile(request):
    profile = request.user.profile  # get the logged-in user's profile
    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile')  # redirect back to profile page
    else:
        form = ProfileForm(instance=profile)
    return render(request, 'edit_profile.html', {'form': form})


@login_required
def my_bookings(request):
    # Get all bookings of the logged-in user
    bookings = Booking.objects.filter(user=request.user).order_by('-created_at')
    
    # Count total bookings
    total_bookings = bookings.count()
    
    context = {
        'bookings': bookings,
        'total_bookings': total_bookings,
    }
    return render(request, 'my_bookings.html', context)


@login_required(login_url='login')
def book_tour(request, pk):
    destination = get_object_or_404(Destination, pk=pk)
    base_price = 4000  # 👈 fixed price per person

    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.destination = destination

            # calculate total price
            booking.total_price = base_price * booking.number_of_people
            booking.save()

            messages.success(request, f'Tour booked successfully! Total Price: ₹{booking.total_price}')
            return redirect('destination-detail', pk=pk)
    else:
        form = BookingForm(initial={"destination": destination})

    return render(request, 'book_tour.html', {
        'form': form,
        'destination': destination,
        'base_price': base_price
    })


def view_package(request, pk):
    destination = get_object_or_404(Destination, pk=pk)
    return render(request, 'view_package.html', {'destination': destination})

def festivals(request):
    return render(request, 'festivals.html')

from django.shortcuts import render

def heritage(request):
    return render(request, 'heritage.html')


def search_destination(request):
    query = request.GET.get('q', '').strip()  # get search term

    if query:
        try:
            # Try to find a destination with exact match (case-insensitive)
            destination = Destination.objects.get(name__iexact=query)
            # Redirect to its detail page
            return redirect('destination-detail', pk=destination.pk)
        except Destination.DoesNotExist:
            # If not found, render a page with "not available" message
            return render(request, 'search_not_found.html', {'query': query})
    else:
        # If search box is empty, redirect to all destinations page
        return redirect('home')
    

    # this is all ai urls///////////////////////////////////////******ai*******/////////////////
    # tourism/views.py


# ---- OpenAI client (optional – works in real env if key set) ----
# ---- OpenAI client (optional – works in real env if key set) ----

# Connect to OpenAI
genai.configure(api_key=os.getenv("AIzaSyASWmBlVOf6_cIQ9UYtv7SeXaNpLqdKbHU"))

# Fast model (recommended)
MODEL = "models/gemini-2.5-flash"

# -----------------------------------
# AI HOME PAGE
# -----------------------------------
def ai_hub(request):
    return render(request, "ai_hub.html")


# -----------------------------------
# Helper – call Gemini safely
# -----------------------------------
def gemini_generate(prompt):
    try:
        model = genai.GenerativeModel(MODEL)
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"AI Error: {str(e)}"


# -----------------------------------
# 1. CHATBOT
# -----------------------------------
@csrf_exempt
def ai_chatbot_api(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=400)

    msg = json.loads(request.body).get("message", "")

    if not msg:
        return JsonResponse({"error": "Message required"}, status=400)

    prompt = f"""
    You are Gujarat’s smartest Tourism Guide.
    Answer with deep knowledge about:
    - history
    - culture
    - food
    - temples
    - routes
    - seasons
    - tips, local insights

    User asked: {msg}
    """

    reply = gemini_generate(prompt)

    return JsonResponse({"reply": reply})


# -----------------------------------
# 2. TRIP PLANNER
# -----------------------------------
@csrf_exempt
def ai_trip_planner_api(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=400)

    data = json.loads(request.body)
    days = data.get("days", "")
    interests = data.get("interests", "")
    start = data.get("start_city", "")

    prompt = f"""
    Create a detailed {days}-day Gujarat trip plan.

    Interests: {interests}
    Start city: {start or "Flexible"}

    Include:
    - Day-wise plan (Morning / Afternoon / Night)
    - Distances + travel time
    - Local food suggestions
    - Seasonal tips
    - Hidden gems only locals know
    """

    trip = gemini_generate(prompt)
    return JsonResponse({"itinerary": trip})


# -----------------------------------
# 3. TRANSLATOR
# -----------------------------------
@csrf_exempt
def ai_translate_api(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=400)

    data = json.loads(request.body)
    text = data.get("text")
    lang = data.get("target")

    lang_map = {
        "gu": "Gujarati",
        "hi": "Hindi",
        "en": "English"
    }

    target = lang_map.get(lang, "Gujarati")

    prompt = f"""
    Translate this Gujarat tourism text to {target}.
    Keep meaning, tone, and style natural.

    Text:
    {text}
    """

    translated = gemini_generate(prompt)
    return JsonResponse({"translated": translated})


# -----------------------------------
# 4. POSTER CAPTION GENERATOR
# -----------------------------------
@csrf_exempt
def ai_poster_api(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=400)

    data = json.loads(request.body)
    theme = data.get("theme", "")
    place = data.get("place", "")
    occasion = data.get("occasion", "")

    prompt = f"""
    Create a Gujarati tourism poster content.

    Theme: {theme}
    Place: {place}
    Occasion: {occasion}

    Provide:
    - One punchline caption
    - 3 bullet points
    - One AI image-generation prompt (cinematic)
    """

    poster = gemini_generate(prompt)
    return JsonResponse({"poster_text": poster})


# -----------------------------------
# 5. FOOD & HOTEL RECOMMENDER
# -----------------------------------
@csrf_exempt
def ai_recommend_api(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=400)

    data = json.loads(request.body)
    city = data.get("city", "")
    budget = data.get("budget", "")
    style = data.get("style", "")

    prompt = f"""
    Give Gujarat travel Food & Stay recommendations.

    City: {city}
    Budget: {budget or "Flexible"}
    Style: {style or "Any"}

    Include:
    - 3 must-eat authentic dishes
    - 3 recommended hotel zones (NOT hotel names)
    - Why each zone is best
    - Safety + transport notes
    """

    rec = gemini_generate(prompt)
    return JsonResponse({"recommendations": rec})


# -----------------------------------
# 6. AUDIO GUIDE SCRIPT
# -----------------------------------
@csrf_exempt
def ai_audio_guide_api(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=400)

    data = json.loads(request.body)
    place = data.get("place")
    duration = data.get("duration")

    prompt = f"""
    Create an engaging audio guide narration for:

    Place: {place}
    Length: {duration}

    Include:
    - History
    - Architecture
    - Culture significance
    - Visual storytelling
    """

    script = gemini_generate(prompt)
    return JsonResponse({"script": script})

# footer sides views

def careers(request):
    return render(request, "careers.html")

def press(request):
    return render(request, "press.html")

def faqs(request):
    return render(request, "faq.html")

def support(request):
    return render(request, "support.html")

def terms(request):
    return render(request, "terms.html")

def privacy(request):
    return render(request, "privacy.html")

def about(request):
    return render(request, "about.html")

def our_team(request):
    return render(request, "our_team.html")
