from django import forms
from .models import Destination
from .models import Booking
from .models import Profile
from django.contrib.auth.models import User


class DestinationForm(forms.ModelForm):
    class Meta:
        model = Destination
        fields = '__all__'



class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = [
            'full_name',
            'email',
            'phone',
            'destination',
            'travel_date',
            'number_of_people',
        ]
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your full name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your email'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your phone number'
            }),
            'destination': forms.Select(attrs={'class': 'form-control'}),
            'travel_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'number_of_people': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1
            }),
        }


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['phone_number', 'profile_pic']

class EditProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['phone_number', 'profile_pic']
        widgets = {
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter phone number'}),
        }