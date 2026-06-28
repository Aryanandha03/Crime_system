
from django import forms
from django.contrib.auth.models import User
from .models import Complaint
import os


# ---------------- REGISTER FORM ----------------

class RegisterForm(forms.ModelForm):

    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter Username",
                "autocomplete": "username"
            }
        )
    )

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter Email Address",
                "autocomplete": "email"
            }
        )
    )

    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Create Password",
                "id": "password"
            }
        )
    )

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password",
        ]

    def clean_username(self):

        username = self.cleaned_data["username"]

        if User.objects.filter(username=username).exists():
            raise forms.ValidationError(
                "Username already exists."
            )

        return username

    def clean_email(self):

        email = self.cleaned_data["email"]

        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(
                "Email already registered."
            )

        return email


# ---------------- COMPLAINT FORM ----------------

class ComplaintForm(forms.ModelForm):

    class Meta:

        model = Complaint

        fields = [

            "category",
            "priority",
            "phone",
            "anonymous",
            "title",
            "description",
            "location",
            "crime_date",
            "evidence",

        ]

        widgets = {

            "category": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),

            "priority": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),

            "phone": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter Mobile Number"
                }
            ),

            "anonymous": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input"
                }
            ),

            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter Complaint Title"
                }
            ),

            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 6,
                    "placeholder": "Describe the incident in detail..."
                }
            ),

            "location": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter Crime Location"
                }
            ),

            "crime_date": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date"
                }
            ),

            "evidence": forms.ClearableFileInput(
                attrs={
                    "class": "form-control"
                }
            ),

        }

        labels = {

            "category": "Crime Category",
            "priority": "Priority Level",
            "phone": "Mobile Number",
            "anonymous": "Submit Anonymously",
            "title": "Complaint Title",
            "description": "Incident Description",
            "location": "Crime Location",
            "crime_date": "Date of Crime",
            "evidence": "Upload Evidence",

        }

    def clean_phone(self):

        phone = self.cleaned_data.get("phone")

        if phone:

            if not phone.isdigit() or len(phone) != 10:

                raise forms.ValidationError(
                    "Enter a valid 10-digit mobile number."
                )

        return phone

    def clean_evidence(self):

        evidence = self.cleaned_data.get("evidence")

        if evidence:

            if evidence.size > 10 * 1024 * 1024:

                raise forms.ValidationError(
                    "File size must be less than 10 MB."
                )

            allowed_extensions = [
                ".jpg",
                ".jpeg",
                ".png",
                ".pdf",
                ".doc",
                ".docx"
            ]

            extension = os.path.splitext(
                evidence.name
            )[1].lower()

            if extension not in allowed_extensions:

                raise forms.ValidationError(
                    "Only JPG, PNG, PDF, DOC and DOCX files are allowed."
                )

        return evidence
