from django import forms
from django.contrib.auth.models import User
from .models import (
    UserProfile, DoctorProfile, DoctorEducation,
    DoctorCertification, DoctorWorkExperience,
    Consultation, Prescription, DoctorReview
)


# ============================================
# PATIENT FORMS
# ============================================
class PatientSignUpForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username',
            'required': True
        })
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email',
            'required': True
        })
    )
    first_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'First Name'
        })
    )
    last_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Last Name'
        })
    )
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password',
            'required': True
        })
    )
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm Password',
            'required': True
        })
    )
    phone_number = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+1 (555) 123-4567'
        })
    )


# ============================================
# DOCTOR FORMS
# ============================================
class DoctorSignUpForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username',
            'required': True
        })
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email',
            'required': True
        })
    )
    first_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'First Name',
            'required': True
        })
    )
    last_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Last Name',
            'required': True
        })
    )
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password',
            'required': True
        })
    )
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm Password',
            'required': True
        })
    )


class DoctorProfileForm(forms.ModelForm):
    class Meta:
        model = DoctorProfile
        fields = [
            'medical_license_number',
            'specialization',
            'years_of_experience',
            'bio',
            'office_address',
            'office_phone'
        ]
        widgets = {
            'medical_license_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., MD123456',
                'required': True
            }),
            'specialization': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Cardiology, Dermatology',
                'required': True
            }),
            'years_of_experience': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 10',
                'required': True
            }),
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Brief description of your experience and expertise',
                'rows': 4
            }),
            'office_address': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': '123 Medical Center Dr',
                'rows': 3
            }),
            'office_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+1 (555) 123-4567'
            })
        }


class DoctorEducationForm(forms.ModelForm):
    class Meta:
        model = DoctorEducation
        fields = ['degree', 'school_name', 'graduation_year', 'details']
        widgets = {
            'degree': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., MBBS, BS, PhD'
            }),
            'school_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'School/College/University'
            }),
            'graduation_year': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 2015'
            }),
            'details': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Additional details about this degree',
                'rows': 2
            })
        }


class DoctorCertificationForm(forms.ModelForm):
    class Meta:
        model = DoctorCertification
        fields = [
            'certification_name',
            'issuing_organization',
            'issue_date',
            'expiry_date',
            'certificate_file'
        ]
        widgets = {
            'certification_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Board Certified Dermatologist'
            }),
            'issuing_organization': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Organization name'
            }),
            'issue_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'expiry_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'certificate_file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.jpg,.jpeg,.png'
            })
        }


class DoctorWorkExperienceForm(forms.ModelForm):
    class Meta:
        model = DoctorWorkExperience
        fields = [
            'hospital_name',
            'department',
            'position',
            'start_date',
            'end_date',
            'description'
        ]
        widgets = {
            'hospital_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Hospital/Clinic Name'
            }),
            'department': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Cardiology'
            }),
            'position': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Senior Consultant'
            }),
            'start_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Description of your role',
                'rows': 3
            })
        }


# ============================================
# CONSULTATION FORMS
# ============================================
class ConsultationRequestForm(forms.ModelForm):
    class Meta:
        model = Consultation
        fields = []


class ConsultationNoteForm(forms.ModelForm):
    class Meta:
        model = Consultation
        fields = ['consultation_notes']
        widgets = {
            'consultation_notes': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Add your consultation notes here...',
                'rows': 4
            })
        }


class ConsultationStatusForm(forms.ModelForm):
    class Meta:
        model = Consultation
        fields = ['status']
        widgets = {
            'status': forms.Select(attrs={
                'class': 'form-control'
            })
        }


# ============================================
# PRESCRIPTION FORMS
# ============================================
class PrescriptionForm(forms.ModelForm):
    class Meta:
        model = Prescription
        fields = [
            'medicine_name',
            'dosage',
            'frequency',
            'duration_days',
            'instructions',
            'side_effects_warning'
        ]
        widgets = {
            'medicine_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Medicine Name',
                'required': True
            }),
            'dosage': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 500mg',
                'required': True
            }),
            'frequency': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 3 times daily, after meals',
                'required': True
            }),
            'duration_days': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Number of days',
                'required': True
            }),
            'instructions': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Special instructions (optional)',
                'rows': 3
            }),
            'side_effects_warning': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Possible side effects and warnings (optional)',
                'rows': 3
            })
        }


# ============================================
# DOCTOR REVIEW FORMS
# ============================================
class DoctorReviewForm(forms.ModelForm):
    rating = forms.ChoiceField(
        choices=[(i, f"{i}★") for i in range(1, 6)],
        widget=forms.RadioSelect(),
        required=True,
        label="How would you rate your experience?"
    )
    
    class Meta:
        model = DoctorReview
        fields = ['rating', 'review_text']
        widgets = {
            'review_text': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Share your experience with this doctor',
                'rows': 4
            })
        }
