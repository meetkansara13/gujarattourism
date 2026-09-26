import json
import os
from functools import wraps

import google.generativeai as genai
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.cache import cache
from django.core.mail import send_mail
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import BookingForm, DestinationForm, EditProfileForm, SignupForm
from .models import Booking, Destination, HeritageSite, HeritageTour, HeritageTourBooking


def staff_required(view):
    return user_passes_test(lambda user: user.is_authenticated and user.is_staff, login_url='custom_admin_login')(view)


def limited(scope, limit=10, seconds=300):
    def decorate(view):
        @wraps(view)
        def wrapped(request, *args, **kwargs):
            key = f'limit:{scope}:{request.META.get("REMOTE_ADDR", "unknown")}'
            if cache.get(key, 0) >= limit:
                return JsonResponse({'error': 'Too many requests. Try again shortly.'}, status=429) if request.content_type == 'application/json' else render(request, 'login.html', status=429)
            cache.set(key, cache.get(key, 0) + 1, seconds)
            return view(request, *args, **kwargs)
        return wrapped
    return decorate


def home(request): return render(request, 'index.html')
def festivals(request): return render(request, 'festivals.html')
def pricing_view(request): return render(request, 'pricing.html', {'destinations': Destination.objects.all()})
def view_package(request, pk): return render(request, 'view_package.html', {'destination': get_object_or_404(Destination, pk=pk)})
def careers(request): return render(request, 'careers.html')
def press(request): return render(request, 'press.html')
def faqs(request): return render(request, 'faq.html')
def support(request): return render(request, 'support.html')
def terms(request): return render(request, 'terms.html')
def privacy(request): return render(request, 'privacy.html')
def about(request): return render(request, 'about.html')
def our_team(request): return render(request, 'our_team.html')


@limited('signup', 5)
def signup_view(request):
    form = SignupForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save(); login(request, user); return redirect('home')
    return render(request, 'signup.html', {'form': form})


@limited('login', 10)
def login_view(request):
    if request.method == 'POST':
        user = authenticate(request, username=request.POST.get('username', '').strip(), password=request.POST.get('password', ''))
        if user: login(request, user); return redirect('home')
        messages.error(request, 'Invalid username or password.')
    return render(request, 'login.html')


def logout_view(request):
    # Logout has no destructive data effect; accepting the existing navigation
    # links keeps the site usable while all privileged mutations require POST.
    logout(request)
    return redirect('login')
def destination_list(request): return render(request, 'destination_list.html', {'destinations': Destination.objects.all()})
def destination_static(request): return render(request, 'destinations.html', {'page_obj': Destination.objects.all().order_by('id')})
def destination_detail(request, pk): return render(request, 'destination_detail.html', {'destination': get_object_or_404(Destination, pk=pk)})


@staff_required
def destination_create(request):
    form = DestinationForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid(): form.save(); return redirect('destination-list')
    return render(request, 'destination_form.html', {'form': form})


@staff_required
def destination_update(request, pk):
    form = DestinationForm(request.POST or None, request.FILES or None, instance=get_object_or_404(Destination, pk=pk))
    if request.method == 'POST' and form.is_valid(): form.save(); return redirect('destination-list')
    return render(request, 'destination_form.html', {'form': form})


@staff_required
@require_POST
def destination_delete(request, pk): get_object_or_404(Destination, pk=pk).delete(); return redirect('destination-list')


@login_required
def profile_view(request): return render(request, 'profile.html', {'user': request.user})


@login_required
def edit_profile(request):
    form = EditProfileForm(request.POST or None, request.FILES or None, instance=request.user.profile)
    if request.method == 'POST' and form.is_valid(): form.save(); return redirect('profile')
    return render(request, 'edit_profile.html', {'form': form})


@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'my_bookings.html', {'bookings': bookings, 'total_bookings': bookings.count()})


@login_required
@require_POST
def add_wishlist(request, id):
    request.user.profile.wishlist.add(get_object_or_404(Destination, pk=id))
    return redirect('my_wishlist')


@login_required
@require_POST
def remove_wishlist(request, id):
    request.user.profile.wishlist.remove(get_object_or_404(Destination, pk=id))
    return redirect('my_wishlist')


@login_required
def my_wishlist(request):
    return render(request, 'wishlist.html', {'items': request.user.profile.wishlist.all()})


@login_required
def book_tour(request, pk):
    destination = get_object_or_404(Destination, pk=pk); form = BookingForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        booking = form.save(commit=False); booking.user = request.user; booking.destination = destination; booking.total_price = 4000 * booking.number_of_people; booking.save(); return redirect('my_bookings')
    return render(request, 'book_tour.html', {'form': form, 'destination': destination, 'base_price': 4000})


def search_destination(request):
    destination = Destination.objects.filter(name__iexact=request.GET.get('q', '').strip()).first()
    return redirect('destination-detail', pk=destination.pk) if destination else render(request, 'search_not_found.html')


@login_required
@limited('contact', 3)
def contact_view(request):
    if request.method == 'POST':
        try: send_mail('Contact form: ' + request.POST.get('subject', '')[:150], request.POST.get('message', '')[:5000], None, [os.getenv('CONTACT_RECIPIENT', os.getenv('EMAIL_HOST_USER', ''))], fail_silently=False)
        except Exception: messages.error(request, 'Message could not be sent. Please try again later.')
        else: messages.success(request, 'Your message was sent.')
        return redirect('contact')
    return render(request, 'contact.html')


def heritage_page(request): return render(request, 'heritage.html', {'sites': HeritageSite.objects.all(), 'tours': HeritageTour.objects.all()})


@login_required
@require_POST
def book_heritage_tour(request):
    try: data = request.POST or json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError): return JsonResponse({'success': False, 'error': 'Invalid request.'}, status=400)
    tour = get_object_or_404(HeritageTour, pk=data.get('tour_id'))
    if not data.get('full_name') or not data.get('phone'): return JsonResponse({'success': False, 'error': 'Name and phone are required.'}, status=400)
    booking = HeritageTourBooking.objects.create(tour=tour, full_name=data['full_name'][:200], phone=data['phone'][:20], email=data.get('email', '')[:254], price=tour.price, notes=data.get('notes', '')[:2000])
    return JsonResponse({'success': True, 'message': 'Booking received; we will confirm availability.', 'booking_id': booking.pk})


GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
if GEMINI_API_KEY: genai.configure(api_key=GEMINI_API_KEY)
def ai_hub(request): return render(request, 'ai_hub.html')


def ai_endpoint(field, prompt):
    @login_required
    @require_POST
    @limited('ai', 20)
    def view(request):
        try: values = [str(value).strip()[:2000] for value in json.loads(request.body).values()]
        except (json.JSONDecodeError, UnicodeDecodeError): return JsonResponse({'error': 'Invalid request.'}, status=400)
        if not values or not values[0]: return JsonResponse({'error': 'Required information is missing.'}, status=400)
        if not GEMINI_API_KEY: return JsonResponse({'error': 'AI service is not configured.'}, status=503)
        try: return JsonResponse({field: genai.GenerativeModel('models/gemini-2.5-flash').generate_content(prompt(*values)).text})
        except Exception: return JsonResponse({'error': 'AI service is temporarily unavailable.'}, status=503)
    return view


ai_chatbot_api = ai_endpoint('reply', lambda message: f'You are a Gujarat tourism guide. Answer accurately: {message}')
ai_trip_planner_api = ai_endpoint('itinerary', lambda days, interests='', start_city='': f'Create Gujarat itinerary: {days} days; interests {interests}; start {start_city}.')
ai_translate_api = ai_endpoint('translated', lambda text, target='gu': f'Translate to {target}: {text}')
ai_poster_api = ai_endpoint('poster_text', lambda theme='', place='', occasion='': f'Create Gujarat poster copy: {theme}; {place}; {occasion}.')
ai_recommend_api = ai_endpoint('recommendations', lambda city, budget='', style='': f'Gujarat food/stay areas for {city}; {budget}; {style}.')
ai_audio_guide_api = ai_endpoint('script', lambda place, duration='short': f'Write a {duration} Gujarat audio guide for {place}.')
