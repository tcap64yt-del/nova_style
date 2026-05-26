from django import forms
from .models import Users
import re
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth import get_user_model


User = get_user_model()
class CustomPasswordResetForm(PasswordResetForm):

    def get_users(self, email):
        return User.objects.filter(
            email=email,
            status=True
        )

class SignupForm(forms.ModelForm):
    name = forms.CharField(min_length=5, max_length=255)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput(), min_length=8)
    confirm_password = forms.CharField(widget=forms.PasswordInput(), min_length=8)
    terms = forms.BooleanField(
        required=True,
        error_messages={"required": "Please agree with Privacy Policy and Terms"},
    )

    class Meta:
        model = Users
        fields = ["name", "email"]

    def clean_name(self):
        name = self.cleaned_data.get("name", "")
        if not name.replace(" ", "").isalpha():
            raise forms.ValidationError("Name must contain only letters.")
        if len(name.strip()) < 5:
            raise forms.ValidationError("Name must be at least 5 characters.")
        return name

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if Users.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already exists.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password:
            if not re.search(r"[A-Za-z]", password):
                self.add_error(
                    "password",
                    "Password must contain letter."
                )

            if not re.search(r"\d", password):
                self.add_error(
                    "password",
                    "Password must contain number."
                )

            if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
                self.add_error(
                    "password",
                    "Password must contain special character."
                ) 
        if password and confirm_password and password != confirm_password:
            self.add_error("confirm_password", "Passwords don't match.")

        return cleaned_data


class OTPForm(forms.Form):
    otp = forms.CharField(max_length=6, min_length=6)


class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput())


class ProfileForm(forms.Form):
    name = forms.CharField(min_length=5, max_length=255)
    email = forms.EmailField()

    def clean_name(self):
        name = self.cleaned_data["name"].strip()
        if not re.fullmatch(r"[A-Za-z ]+", name):
            raise forms.ValidationError("Name must contain only letters and spaces.")
        if len(name) < 5:
            raise forms.ValidationError("Name must be at least 5 characters.")
        return name

    def clean_email(self):
        email = self.cleaned_data["email"].lower().strip()
        if not email.endswith("@gmail.com"):
            raise forms.ValidationError("Only Gmail addresses are allowed.")
        return email
    
