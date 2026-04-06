from pathlib import Path
from decouple import config
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY') # Ключ составляется автоматически при создании приложения в формате ‘fsbndihsbfdoijsdjfsoisjfoibios’
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', cast=bool)
ALLOWED_HOSTS = []
# Application definition
INSTALLED_APPS = [
 'django.contrib.admin',
 'django.contrib.auth',
 'django.contrib.contenttypes',
 'django.contrib.sessions',
 'django.contrib.messages',
 'django.contrib.staticfiles',
 'posts', # Добавляем posts для корректной работы
]
MIDDLEWARE = [
 'django.middleware.security.SecurityMiddleware',
 'django.contrib.sessions.middleware.SessionMiddleware',
 'django.middleware.common.CommonMiddleware',
 'django.middleware.csrf.CsrfViewMiddleware',
 'django.contrib.auth.middleware.AuthenticationMiddleware',
 'django.contrib.messages.middleware.MessageMiddleware',
 'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
ROOT_URLCONF = 'bd_lab3.urls'
TEMPLATES = [
 {
 'BACKEND': 'django.template.backends.django.DjangoTemplates',
 'DIRS': [],
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
WSGI_APPLICATION = 'bd_lab3.wsgi.application'
# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases
DATABASES = {
 'default': {
 'ENGINE': 'django.db.backends.postgresql',
 'NAME': config("DATABASE_NAME"), #указывается в формате string(‘database’)
 'USER': config("DATABASE_USER"), #указывается в формате string(‘postgre’)
 'PASSWORD': config("DATABASE_PASSWORD"), #указывается в форматеstring
 'HOST': config("DATABASE_HOST"), #указывается в формате string
 'PORT': config("DATABASE_PORT"), #указывается в формате string
 }
}
# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-passwordvalidators
AUTH_PASSWORD_VALIDATORS = [
 {
 'NAME':
'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
 },
 {
 'NAME':
'django.contrib.auth.password_validation.MinimumLengthValidator',
 },
 {
 'NAME':
'django.contrib.auth.password_validation.CommonPasswordValidator',
 },
 {
 'NAME':
'django.contrib.auth.password_validation.NumericPasswordValidator',
 },
]
# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/
STATIC_URL = 'static/'
# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'