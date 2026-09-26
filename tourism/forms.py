from datetime import date
import re

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Booking, Destination, Profile


class SignupForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=15, required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'phone', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('An account with this email already exists.')
        return email

    def clean_phone(self):
        phone = self.cleaned_data['phone'].strip()
        if not re.fullmatch(r'\+?[0-9]{10,15}', phone):
            raise forms.ValidationError('Enter a valid 10–15 digit phone number.')
        return phone

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            user.profile.phone_number = self.cleaned_data['phone']
            user.profile.save(update_fields=['phone_number'])
        return user


class DestinationForm(forms.ModelForm):
    class Meta:
        model = Destination
        fields = ('name', 'short_description', 'description', 'image', 'featured')


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ('full_name', 'email', 'phone', 'travel_date', 'number_of_people')
        widgets = {
            'travel_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'number_of_people': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 20}),
        }

    def clean_travel_date(self):
        travel_date = self.cleaned_data['travel_date']
        if travel_date < date.today():
            raise forms.ValidationError('Travel date cannot be in the past.')
        return travel_date

    def clean_number_of_people(self):
        people = self.cleaned_data['number_of_people']
        if not 1 <= people <= 20:
            raise forms.ValidationError('Bookings must be for 1 to 20 people.')
        return people

    def clean_phone(self):
        phone = self.cleaned_data['phone'].strip()
        if not re.fullmatch(r'\+?[0-9]{10,15}', phone):
            raise forms.ValidationError('Enter a valid 10–15 digit phone number.')
        return phone


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['phone_number', 'profile_pic']

    def clean_profile_pic(self):
        image = self.cleaned_data.get('profile_pic')
        if image and image.size > 5 * 1024 * 1024:
            raise forms.ValidationError('Profile image must be 5 MB or smaller.')
        return image


class EditProfileForm(ProfileForm):
    pass
