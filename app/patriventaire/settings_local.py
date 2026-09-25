"""Local database and email settings loaded from the repository .env file."""

from pathlib import Path


def _load_environment():
    env_path = Path(__file__).resolve().parents[2] / '.env'
    environment = {}

    if not env_path.exists():
        return environment

    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue

        name, value = line.split('=', 1)
        if name.startswith(('DB_', 'EMAIL_')) or name == 'DEFAULT_FROM_EMAIL':
            environment[name] = value.strip().strip('"\'')

    return environment


_environment = _load_environment()

if _environment.get('DB_NAME'):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': _environment['DB_NAME'],
            'USER': _environment.get('DB_USER'),
            'PASSWORD': _environment.get('DB_PASSWORD'),
            'HOST': _environment.get('DB_HOST'),
            'PORT': int(_environment['DB_PORT'])
            if _environment.get('DB_PORT')
            else '',
        }
    }

if _environment.get('EMAIL_HOST'):
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = _environment['EMAIL_HOST']
    EMAIL_PORT = int(_environment.get('EMAIL_PORT', '587'))
    EMAIL_HOST_USER = _environment.get('EMAIL_HOST_USER', '')
    EMAIL_HOST_PASSWORD = _environment.get('EMAIL_HOST_PASSWORD', '')
    EMAIL_USE_TLS = _environment.get('EMAIL_USE_TLS', 'True').lower() == 'true'
    EMAIL_USE_SSL = _environment.get('EMAIL_USE_SSL', 'False').lower() == 'true'
    DEFAULT_FROM_EMAIL = _environment.get(
        'DEFAULT_FROM_EMAIL',
        EMAIL_HOST_USER,
    )