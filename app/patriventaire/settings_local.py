"""Local database settings loaded from the repository .env file."""

from pathlib import Path


def _load_database_environment():
    env_path = Path(__file__).resolve().parents[2] / '.env'
    database_environment = {}

    if not env_path.exists():
        return database_environment

    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue

        name, value = line.split('=', 1)
        if name.startswith('DB_'):
            database_environment[name] = value.strip().strip('"\'')

    return database_environment


_database_environment = _load_database_environment()

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': _database_environment.get('DB_NAME'),
        'USER': _database_environment.get('DB_USER'),
        'PASSWORD': _database_environment.get('DB_PASSWORD'),
        'HOST': _database_environment.get('DB_HOST'),
        'PORT': int(_database_environment['DB_PORT'])
        if _database_environment.get('DB_PORT')
        else '',
    }
}