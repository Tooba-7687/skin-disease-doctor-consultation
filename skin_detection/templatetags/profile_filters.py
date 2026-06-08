from django import template
from django.contrib.auth.models import User
from skin_detection.models import UserProfile

register = template.Library()


@register.filter
def get_user_role(user):
    """
    Get user role safely.
    Returns 'patient', 'doctor', or None
    """
    if not user or not user.is_authenticated:
        return None
    
    try:
        profile = UserProfile.objects.get(user=user)
        return profile.role
    except UserProfile.DoesNotExist:
        return None


@register.filter
def has_profile(user):
    """
    Check if user has a profile
    """
    if not user or not user.is_authenticated:
        return False
    
    return UserProfile.objects.filter(user=user).exists()


@register.filter
def is_doctor(user):
    """
    Check if user is a doctor
    """
    role = get_user_role(user)
    return role == 'doctor'


@register.filter
def is_patient(user):
    """
    Check if user is a patient
    """
    role = get_user_role(user)
    return role == 'patient'
