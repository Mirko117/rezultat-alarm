import os

os.environ.setdefault("DJANGO_SECRET_KEY", "test-secret-key")
os.environ.setdefault("FERNET_KEY", "oGQH5o0m0vChmIYiM3wkL7sj9j2xQe_XvHeHpuZ1CsQ=")
os.environ.setdefault("DEFAULT_FROM_EMAIL", "test@example.com")
os.environ.setdefault("POSTGRES_DB_NAME", "test")
os.environ.setdefault("POSTGRES_USER", "test")
os.environ.setdefault("POSTGRES_PASSWORD", "test")

from .base import *  # noqa: F403

DEBUG = False

DATABASES = {  # noqa: F405
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "test.sqlite3",  # noqa: F405
    }
}

EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]
