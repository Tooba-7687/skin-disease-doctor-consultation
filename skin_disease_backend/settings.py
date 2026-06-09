from pathlib import Path
import os

# Optional dotenv support
try:
    from decouple import config
except ImportError:
    def config(key, default=None, cast=None):
        value = os.environ.get(key, default)
        if cast and value:
            return cast(value)
        return value


# =========================
# BASE SETTINGS
# =========================
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config(
    'SECRET_KEY',
    default='django-insecure-skin-disease-detection-fyp-2024'
)

# IMPORTANT: set DEBUG=False on PythonAnywhere
DEBUG = config(
    'DEBUG',
    default=True,
    cast=lambda v: str(v).lower() in ('true', '1', 'yes')
)

# IMPORTANT: Production-safe ALLOWED_HOSTS
ALLOWED_HOSTS = config(
    'ALLOWED_HOSTS',
    default='localhost,127.0.0.1',
    cast=lambda v: [s.strip() for s in v.split(',')]
)


# =========================
# INSTALLED APPS
# =========================
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


# =========================
# MIDDLEWARE
# =========================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',

    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',

    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


ROOT_URLCONF = 'skin_disease_backend.urls'


# =========================
# TEMPLATES
# =========================
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


# =========================
# DATABASE
# =========================
if config('DATABASE_URL', default=None):
    import dj_database_url
    DATABASES = {
        'default': dj_database_url.config(
            default=config('DATABASE_URL'),
            conn_max_age=600
        )
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }


# =========================
# PASSWORD VALIDATION
# =========================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# =========================
# INTERNATIONALIZATION
# =========================
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Karachi'
USE_I18N = True
USE_TZ = True


# =========================
# STATIC FILES (IMPORTANT FOR DEPLOYMENT)
# =========================
STATIC_URL = '/static/'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'skin_detection', 'static'),
]

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# WhiteNoise for production static handling
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


# =========================
# MEDIA FILES
# =========================
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


# =========================
# DEFAULT PRIMARY KEY
# =========================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# =========================
# CORS SETTINGS
# =========================
CORS_ALLOW_ALL_ORIGINS = config(
    'CORS_ALLOW_ALL_ORIGINS',
    default=False,
    cast=lambda v: str(v).lower() in ('true', '1', 'yes')
)

CORS_ALLOWED_ORIGINS = config(
    'CORS_ALLOWED_ORIGINS',
    default='http://localhost:3000',
    cast=lambda v: [s.strip() for s in v.split(',')]
)


# =========================
# ML MODEL PATH (SAFE FOR DEPLOYMENT)
# =========================
MODEL_DIR = os.path.join(BASE_DIR, 'model')

MODEL_PATH = os.path.join(MODEL_DIR, 'skin_disease_balanced.h5')
NEW_MODEL_PATH = os.path.join(MODEL_DIR, 'efficientnet_skin.keras')

if os.path.exists(NEW_MODEL_PATH):
    MODEL_PATH = NEW_MODEL_PATH

MODEL_IMAGE_SIZE = (300, 300)


# =========================
# DISEASE INFO
# =========================
DISEASE_INFO = {
    'akiec': {
        'name': 'Actinic Keratosis',
        'description': 'A rough, scaly patch caused by sun exposure.',
        'care': 'Consult a dermatologist. Use sunscreen.',
        'severity': 'Moderate'
    },
    'bcc': {
        'name': 'Basal Cell Carcinoma',
        'description': 'A type of skin cancer starting in basal cells.',
        'care': 'Immediate medical attention required.',
        'severity': 'High'
    },
    'bkl': {
        'name': 'Benign Keratosis',
        'description': 'Non-cancerous skin growth.',
        'care': 'Usually harmless.',
        'severity': 'Low'
    },
    'df': {
        'name': 'Dermatofibroma',
        'description': 'Benign fibrous skin nodule.',
        'care': 'No treatment needed.',
        'severity': 'Low'
    },
    'mel': {
        'name': 'Melanoma',
        'description': 'Most dangerous skin cancer.',
        'care': 'Urgent medical attention required.',
        'severity': 'Very High'
    },
    'nv': {
        'name': 'Melanocytic Nevi',
        'description': 'Common harmless moles.',
        'care': 'Monitor changes.',
        'severity': 'Low'
    },
    'scc': {
        'name': 'Squamous Cell Carcinoma',
        'description': 'Cancer from squamous cells.',
        'care': 'Medical attention required.',
        'severity': 'High'
    },
    'vasc': {
        'name': 'Vascular Lesions',
        'description': 'Blood vessel skin abnormalities.',
        'care': 'Consult dermatologist.',
        'severity': 'Moderate'
    }
}


# =========================
# LOGGING
# =========================
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


# =========================
# EMAIL (DEV MODE)
# =========================
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'noreply@dermai.com'


# =========================
# PRODUCTION SECURITY
# =========================
# if not DEBUG:
#     SECURE_SSL_REDIRECT = False
#     SESSION_COOKIE_SECURE = False
#     CSRF_COOKIE_SECURE = False

#     SECURE_HSTS_SECONDS = 0
#     SECURE_HSTS_INCLUDE_SUBDOMAINS = False
#     SECURE_HSTS_PRELOAD = False

#     SECURE_BROWSER_XSS_FILTER = True

#     SECURE_CONTENT_SECURITY_POLICY = {
#         "default-src": ("'self'",),
#     }

SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_HSTS_SECONDS = 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False

# =========================
# TENSORFLOW LOGS CLEAN
# =========================
import logging
logging.getLogger('tensorflow').setLevel(logging.ERROR)