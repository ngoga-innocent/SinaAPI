

from pathlib import Path
import os
from datetime import timedelta
import dj_database_url
from dotenv import load_dotenv
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv()
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-4kxfbm)#mq6vx2)ap03jktc7*&!u9*8z5_uj5+n$h!xlgbr31#'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'jazzmin',
    # 'cloudinary_storage',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    "corsheaders",
     'rest_framework',
    'rest_framework.authtoken',
     'rest_framework_simplejwt',
    'cloudinary',
    'cloudinary_storage',
     
     "django_filters",
    'Auths',
    'Products',
    'Payments',
    'ChatSupport',
    'drf_spectacular',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    "corsheaders.middleware.CorsMiddleware",
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'SinaApp.urls'
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        # 'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication', 
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    # 'DEFAULT_PERMISSION_CLASSES': (
    #     'rest_framework.permissions.IsAuthenticated',
    # ),
}


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates'],
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

WSGI_APPLICATION = 'SinaApp.wsgi.application'

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=50),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
}
# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db1.sqlite3',
    }
}
# DATABASES['default']=dj_database_url.parse(os.getenv("DATABASE_URL"))

# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

# TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True
TIME_ZONE = 'Africa/Kigali'  


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

# STATIC_URL = 'static/'
# STATIC_URL = '/static/'
# MEDIA_URL = '/media/'

# STATICFILES_DIRS = [
#     os.path.join(BASE_DIR, 'static'),
# # ]
STATIC_ROOT = os.path.join(BASE_DIR, "assets")
# MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
AUTH_USER_MODEL = 'Auths.User'

# site settings
JAZZMIN_SETTINGS = {
    "site_title": "SinaApp Admin",
    "site_header": "SinaApp Dashboard",
    "site_brand": "SinaApp",
    "welcome_sign": "Welcome to SinaApp Admin Panel",
    "site_logo": "images/Logo.png",  # Path to your logo inside `static/`
    "login_logo": "images/Logo.png",  # Login page logo
    "login_logo_dark": None,  # Dark mode login logo
    "site_logo_classes": "images/Logo.png",  # Add CSS classes to your logo
    "copyright": "SinaApp © 2025",
    "search_model": "auth.User",  # Enable search for Django users
}
JAZZMIN_SETTINGS["theme"] = "solar"


# Static files (CSS, JS, images)
STATIC_URL = "/static/"
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")] 

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")


CLOUDINARY_STORAGE = {
    'CLOUD_NAME': 'dlbdsv95f',
    'API_KEY': '226668397868968',
    'API_SECRET': 'lTcafDxVVVnGLSpDcxqDJRt8S2E'
}
# MEDIA_URL = '/media/'  # or any prefix you choose
STORAGES = {
    "default": {
        "BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'housemajorrwanda@gmail.com'         # Replace this
EMAIL_HOST_PASSWORD = 'qakq kaby hkci ufkb'      # And this
DEFAULT_FROM_EMAIL = 'housemajorrwanda@gmail.com'         # Replace this
# Allow specific origins
# CORS_ALLOWED_ORIGINS = [
#     "http://localhost:5173",  # your React dev server
#     "http://127.0.0.1:5173",
#     "http://localhost:3000",
# ]

# Or, during development only, allow all (⚠️ not for production)
CORS_ALLOW_ALL_ORIGINS = True
SPECTACULAR_SETTINGS = {
    'TITLE': 'Sina Gerard API',
    'DESCRIPTION': 'Sina Gerard Api Full Documentation',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    # OTHER SETTINGS
}