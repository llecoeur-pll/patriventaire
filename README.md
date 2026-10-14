## Patriventaire

Patriventaire est un outil permettant un inventaire collaboratif de patrimoine.

## Configuration locale

La configuration locale est chargée depuis un fichier `.env` à la racine du
projet, au même niveau que le dossier `app`. Ce fichier est ignoré par Git et
ne doit pas être ajouté au dépôt.

### Base de données PostgreSQL

Créez `.env` avec les variables suivantes :

```dotenv
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=patriventaire
POSTGRES_PASSWORD=mot-de-passe
POSTGRES_DB=patriventaire
```

La présence du fichier `.env` active la connexion PostgreSQL à la place de la
base SQLite utilisée par défaut. Après avoir créé la base, appliquez les
migrations depuis le dossier `app` :

```bash
python manage.py migrate
```

### Envoi des mails

Ajoutez les paramètres SMTP à `.env` :

```dotenv
EMAIL_HOST=smtp.example.org
EMAIL_PORT=587
EMAIL_HOST_USER=utilisateur@example.org
EMAIL_HOST_PASSWORD=mot-de-passe
EMAIL_USE_TLS=True
EMAIL_USE_SSL=False
DEFAULT_FROM_EMAIL=utilisateur@example.org
```

Les paramètres `EMAIL_USE_TLS` et `EMAIL_USE_SSL` doivent être adaptés au
fournisseur SMTP. `EMAIL_USE_TLS=True` est généralement utilisé avec le port
587, tandis que `EMAIL_USE_SSL=True` est généralement utilisé avec le port
465. En l'absence de `EMAIL_HOST`, les mails sont affichés dans la console
pour faciliter le développement.

### Administration Django

Pour créer un administrateur de Django, utilisez la commande `python manage.py createsuperuser`.

## Développement

### Avec Docker

Pour l'hôte de base de données dans le fichier `.env` utilisez le nom du service Docker de la base de données : `POSTGRES_HOST=patriventaire-database`

Démarrez les conteneurs avec :
`docker compose -f docker-compose-dev.yml up -d`

Docker va créér l'image `patriventaire` si elle n'existe pas et déployer un second conteneur pour la base PosgreSQL (`patriventaire-database`).

L'application est déployée avec le serveur interne de Django utilisable seulement en développement.

Lors du premier démarrage et pour appliquer de nouveaux changements, éxecuter les migrations Django :
`docker exec patriventaire python manage.py migrate`.

Les photos téléversées par les utilisateurs sont stockées dans le dossier medias sur la machine hôte.

## Déploiement en production

Voir https://docs.djangoproject.com/en/6.1/howto/deployment/.

### Avec Docker

Pour l'hôte de base de données dans le fichier `.env` utilisez le nom du service Docker de la base de données : `POSTGRES_HOST=patriventaire-database`.

Configurez la variable d'environnement `DJANGO_ALLOWED_HOSTS` pour autoriser les connexions externes. Par exemple :
```dotenv
nomdedomaine.extension,
www.nomdedomaine.extension,
patriventaire,
localhost,
127.0.0.1,
```

Configurez la variable d'environnement `CSRF_TRUSTED_ORIGINS` par exemple :
```dotenv
CSRF_TRUSTED_ORIGINS=https://nomdedomaine.extension,https://www.nomdedomaine.extension
```
Voir  ["Cross Site Request Forgery"](https://docs.djangoproject.com/en/6.1/ref/csrf/) sur la documentation de Django.

Le serveur utilisé est [Granian](https://github.com/emmett-framework/granian). Il sert aussi les fichiers statiques. Configurez les variables d'environnement de Granian pour servir les fichiers statiques :
```dotenv
GRANIAN_STATIC_PATH_ROUTE=/static
GRANIAN_STATIC_PATH_MOUNT=./staticfiles
```

Désactivez le mode DEBUG dans le *.env*:
```dotenv
DJANGO_DEBUG=False
```

Déployez les conteneurs avec :
`docker compose up -d`

Lors du premier démarrage et pour appliquer de nouveaux changements, éxecuter les migrations Django :
`docker exec patriventaire python manage.py migrate`.

Pour collecter les fichiers statiques : `docker exec patriventaire python manage.py collectstatic`.

Créez un super utilisateur avec `docker exec -it patriventaire python manage.py createsuperuser`.