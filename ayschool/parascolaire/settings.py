import os
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY', 'vercel-demo-secret-key')
DEBUG = os.environ.get('DEBUG', 'False') == 'True'
DEMO_MODE = os.environ.get('AYSCHOOL_MODE', 'demo') == 'demo'
if not DEMO_MODE:
    SECRET_KEY = os.environ.get('SECRET_KEY', '')
    if len(SECRET_KEY) < 50:
        raise ImproperlyConfigured('Le mode établissement exige une SECRET_KEY privée de 50 caractères minimum.')
    AUTH_PASSWORD_VALIDATORS = [
        {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
        {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 12}},
        {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
        {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
    ]
    SESSION_COOKIE_SECURE = CSRF_COOKIE_SECURE = not DEBUG
    SECURE_SSL_REDIRECT = not DEBUG
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

ALLOWED_HOSTS = [
    '127.0.0.1',
    'localhost',
    'testserver',
    '.vercel.app',
] if DEMO_MODE else ['127.0.0.1', 'localhost'] + [
    host.strip() for host in os.environ.get('AYSCHOOL_ALLOWED_HOSTS', '').split(',') if host.strip()
]

CSRF_TRUSTED_ORIGINS = [
    'https://*.vercel.app',
] if DEMO_MODE else [
    origin.strip() for origin in os.environ.get('AYSCHOOL_TRUSTED_ORIGINS', '').split(',') if origin.strip()
]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'activites',
    'authentification',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'parascolaire.urls'

TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [],
    'APP_DIRS': True,
    'OPTIONS': {
        'context_processors': [
            'django.template.context_processors.debug',
            'django.template.context_processors.request',
            'django.contrib.auth.context_processors.auth',
            'django.contrib.messages.context_processors.messages',
            'parascolaire.context_processors.demo_user',
        ],
    },
}]

WSGI_APPLICATION = 'parascolaire.wsgi.application'

if DEMO_MODE:
    DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': '/tmp/ayschool-demo.sqlite3'}}
    SESSION_ENGINE = 'django.contrib.sessions.backends.signed_cookies'
    MESSAGE_STORAGE = 'django.contrib.messages.storage.cookie.CookieStorage'
elif os.environ.get('AYSCHOOL_DB_HOST'):
    DATABASES = {'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'HOST': os.environ['AYSCHOOL_DB_HOST'],
        'PORT': os.environ.get('AYSCHOOL_DB_PORT', '5432'),
        'NAME': os.environ['AYSCHOOL_DB_NAME'],
        'USER': os.environ['AYSCHOOL_DB_USER'],
        'PASSWORD': os.environ['AYSCHOOL_DB_PASSWORD'],
        'OPTIONS': {'sslmode': os.environ.get('AYSCHOOL_DB_SSLMODE', 'require')},
    }}
elif DEBUG and not os.environ.get('VERCEL'):
    DATABASES = {'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'ayschool.sqlite3',
        'OPTIONS': {'transaction_mode': 'IMMEDIATE'},
    }}
else:
    raise ImproperlyConfigured('Configurez PostgreSQL pour le mode établissement hors développement local.')

AUTH_USER_MODEL = 'authentification.Utilisateur'

LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'Africa/Casablanca'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
LOGIN_URL = 'connexion'
LOGIN_REDIRECT_URL = 'liste_activites'
LOGOUT_REDIRECT_URL = 'accueil'
