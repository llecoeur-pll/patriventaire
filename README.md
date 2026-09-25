## Patriventaire

Patriventaire est un outil permettant un inventaire collaboratif de patrimoine.

## Configuration locale

La configuration locale est chargée depuis un fichier `.env` à la racine du
projet, au même niveau que le dossier `app`. Ce fichier est ignoré par Git et
ne doit pas être ajouté au dépôt.

### Base de données PostgreSQL

Créez `.env` avec les variables suivantes :

```dotenv
DB_NAME=patriventaire
DB_USER=patriventaire
DB_PASSWORD=mot-de-passe
DB_HOST=localhost
DB_PORT=5432
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