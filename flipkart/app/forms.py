from django import forms
from .models import UserProfile, Address


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ["gender","dob","mobile","photo"]


class AddressForm(forms.ModelForm):
    class Meta:
        model=Address
        fields=["address","city","country","pincode"]



