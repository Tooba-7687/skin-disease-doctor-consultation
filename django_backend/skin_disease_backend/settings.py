from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-skin-disease-detection-fyp-2024-tooba-nadeem'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'skin_detection',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'skin_disease_backend.urls'



TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'skin_detection', 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'skin_disease_backend.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE     = 'Asia/Karachi'
USE_I18N      = True
USE_TZ        = True

# Static files
STATIC_URL  = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR.parent, 'frontend', 'static')
]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Media files
MEDIA_URL  = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# CORS Settings
CORS_ALLOW_ALL_ORIGINS = True

# ML Model Path
# Using EfficientNetB4 (85.31% accuracy) - Single model for better performance

MODEL_PATH = os.path.join(BASE_DIR.parent, 'model', 'skin_disease_balanced.h5')
NEW_MODEL_PATH = os.path.join(BASE_DIR.parent, 'model', 'efficientnet_skin.keras')

# Use new model if it exists, fallback to old model
if os.path.exists(NEW_MODEL_PATH):
    MODEL_PATH = NEW_MODEL_PATH

MODEL_IMAGE_SIZE = (300, 300)  # New model uses 300x300 images

# Disease Information
DISEASE_INFO = {
    'akiec': {
        'name'        : 'Actinic Keratosis',
        'description' : 'A rough, scaly patch on skin caused by years of sun exposure.',
        'care'        : 'Consult a dermatologist. Use sunscreen regularly.',
        'severity'    : 'Moderate'
    },
    'bcc': {
        'name'        : 'Basal Cell Carcinoma',
        'description' : 'A type of skin cancer that begins in the basal cells.',
        'care'        : 'Immediate medical attention required.',
        'severity'    : 'High'
    },
    'bkl': {
        'name'        : 'Benign Keratosis',
        'description' : 'A non-cancerous skin growth that appears waxy or scaly.',
        'care'        : 'Usually harmless. Monitor for changes.',
        'severity'    : 'Low'
    },
    'df': {
        'name'        : 'Dermatofibroma',
        'description' : 'A common benign fibrous nodule usually found on the skin.',
        'care'        : 'Usually harmless. No treatment needed.',
        'severity'    : 'Low'
    },
    'mel': {
        'name'        : 'Melanoma',
        'description' : 'The most serious type of skin cancer.',
        'care'        : 'Immediate medical attention required!',
        'severity'    : 'Very High'
    },
    'nv': {
        'name'        : 'Melanocytic Nevi',
        'description' : 'Common moles that are usually harmless.',
        'care'        : 'Monitor for changes in size or color.',
        'severity'    : 'Low'
    },
    'scc': {
        'name'        : 'Squamous Cell Carcinoma',
        'description' : 'A type of skin cancer arising from squamous cells.',
        'care'        : 'Immediate medical attention required.',
        'severity'    : 'High'
    },
    'vasc': {
        'name'        : 'Vascular Lesions',
        'description' : 'Abnormalities of the blood vessels in the skin.',
        'care'        : 'Consult a dermatologist for treatment options.',
        'severity'    : 'Moderate'
    }
}

# TensorFlow Configuration for Model Serving

import logging
logging.getLogger('tensorflow').setLevel(logging.ERROR)

# ============================================
# EMAIL CONFIGURATION (CONSOLE BACKEND - TESTING)
# ============================================
# Emails will be printed to terminal console
# This is perfect for development and testing

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_HOST = 'localhost'
EMAIL_PORT = 1025
EMAIL_USE_TLS = False
EMAIL_USE_SSL = False
DEFAULT_FROM_EMAIL = 'noreply@dermai.com'
SERVER_EMAIL = 'server@dermai.com'

# ============================================
# LOGGING CONFIGURATION
# ============================================
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}