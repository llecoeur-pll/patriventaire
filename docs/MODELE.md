# Modèle de données

Ce document décrit le modèle de données de Patriventaire à partir des
spécifications fonctionnelles. Le modèle couvre la saisie publique d'un
élément de patrimoine et les photographies qui lui sont rattachées.

## Vue d'ensemble

Le modèle minimal contient deux entités :

```text
Element 1 ──────── N Photographie
```

- Un `Element` possède un numéro unique et les informations saisies par le
  déposant.
- Un `Element` possède également un jeton aléatoire unique, utilisé pour
  accéder à sa fiche en écriture sans authentification.
- Une `Photographie` appartient à un seul `Element`.
- Un élément doit posséder au moins une photographie. Cette règle est
  contrôlée au niveau de la validation du formulaire ou du service de
  création, car elle ne peut pas être garantie par une simple contrainte de
  base de données.

Il n'y a pas de table `Utilisateur` dans le périmètre actuel : l'interface de
saisie est publique et ne demande aucune authentification. Les coordonnées du
déposant sont donc conservées sur chaque élément.

## Entité `Element`

| Champ | Type Django recommandé | Obligatoire | Contraintes / rôle |
| --- | --- | --- | --- |
| `numero` | `BigAutoField` | Oui | Identifiant primaire et numéro unique communiqué au déposant |
| `jeton_ecriture` | `CharField(max_length=64, unique=True, editable=False)` | Oui | Suite aléatoire unique utilisée pour l'accès en écriture |
| `libelle` | `CharField(max_length=255)` | Oui | Nom ou libellé de l'élément |
| `nom_deposant` | `CharField(max_length=255)` | Oui | Nom et prénom, ou pseudonyme |
| `courriel_deposant` | `EmailField(blank=True)` | Non | Adresse utilisée pour le message de confirmation |
| `telephone_deposant` | `CharField(max_length=30, blank=True)` | Non | Téléphone du déposant |
| `categorie` | `CharField(choices=...)` | Oui | Une valeur de la liste des catégories autorisées |
| `commune_deleguee` | `CharField(choices=...)` | Oui | Une commune déléguée de la liste de référence |
| `latitude` | `DecimalField(max_digits=9, decimal_places=6)` | Oui | Latitude GPS en degrés décimaux, de -90 à 90 |
| `longitude` | `DecimalField(max_digits=9, decimal_places=6)` | Oui | Longitude GPS en degrés décimaux, de -180 à 180 |
| `description` | `TextField()` | Oui | Description de l'élément |
| `histoire` | `TextField(blank=True)` | Non | Histoire ou anecdote liée à l'élément |
| `date_ajout` | `DateTimeField(auto_now_add=True)` | Oui | Date et heure de création, renseignées automatiquement en base |

### Catégories autorisées

Les valeurs stockées doivent être stables et distinctes du libellé affiché,
afin de permettre une évolution de l'interface sans modifier les données.

| Valeur interne proposée | Libellé affiché |
| --- | --- |
| `mare` | Mare |
| `puit_fontaine` | Puit ou fontaine |
| `ruine_batisse_ancienne` | Ruine ou Bâtisse ancienne |
| `lavoir` | Lavoir |
| `arbre_remarquable` | Arbre remarquable |
| `autre` | Autre |

### Communes déléguées

Les choix sont présentés par ordre alphabétique :

1. Chênedouit
2. La-Forêt-Auvray
3. La-Fresnaye-Aux-Sauvages
4. Les-Rotours
5. Ménil-Jean
6. Putanges-Pont-Ecrepin
7. Rabodanges
8. Saint-Aubert
9. Sainte-Croix-Sur-Orne

La valeur enregistrée doit rester une valeur contrôlée par choix (`choices`),
plutôt qu'un texte libre, pour garantir la cohérence des recherches et des
exports.

## Accès à une fiche

Le modèle distingue deux URL qui ne donnent pas les mêmes droits :

- **Lecture seule** : l'URL contient `numero`, qui identifie publiquement la
  fiche à consulter.
- **Écriture** : l'URL contient `jeton_ecriture`, qui autorise l'accès au
  formulaire de modification de la fiche.

Le `jeton_ecriture` doit être généré côté serveur avec une source aléatoire
cryptographiquement sûre, par exemple `secrets.token_urlsafe(32)`. Il ne doit
pas être déduit du numéro, du nom du déposant ou d'une autre donnée connue.
Il est transmis uniquement dans le lien de modification envoyé au déposant
et ne doit pas être affiché dans l'URL de lecture seule.

## Entité `Photographie`

| Champ | Type Django recommandé | Obligatoire | Contraintes / rôle |
| --- | --- | --- | --- |
| `id` | `BigAutoField` | Oui | Identifiant technique |
| `element` | `ForeignKey(Element, on_delete=CASCADE)` | Oui | Élément auquel la photographie est rattachée |
| `fichier` | `ImageField(upload_to=...)` | Oui | Fichier image associé |
| `commentaire` | `TextField(blank=True)` | Non | Commentaire ou précision sur la photographie |

La suppression d'un élément supprime ses photographies rattachées
(`CASCADE`). Le chemin du fichier est stocké en base ; le contenu binaire est
stocké dans le stockage média configuré par Django.

## Règles d'intégrité et de validation

- `numero` est généré automatiquement et ne peut pas être réutilisé.
- `jeton_ecriture` est généré automatiquement, est unique et ne doit jamais
  être réutilisé pour une autre fiche.
- `latitude` et `longitude` sont obligatoires et doivent respecter leurs
  bornes géographiques.
- `categorie` et `commune_deleguee` n'acceptent que les choix définis dans ce
  document.
- `courriel_deposant` et `telephone_deposant` sont facultatifs, mais le
  courriel doit être valide lorsqu'il est fourni.
- Un élément ne peut être validé que s'il contient au moins une photographie.
- Les formats, tailles maximales et dimensions acceptés pour les images
  doivent être contrôlés à l'import afin de limiter les fichiers dangereux ou
  trop volumineux.
- Les champs contenant des données personnelles (`nom_deposant`, courriel et
  téléphone) doivent être protégés dans l'administration et les exports, avec
  une durée de conservation à définir dans le cadre du RGPD.

## Comportements applicatifs liés au modèle

### Confirmation après validation

Après la création réussie d'un élément :

1. Le numéro `numero` est récupéré.
2. Le `jeton_ecriture` est récupéré.
3. Si `courriel_deposant` est renseigné, un courriel de remerciement est
  envoyé avec :
  - un lien de lecture seule contenant `numero` ;
  - un lien vers le formulaire de modification contenant
    `jeton_ecriture`.
4. Le déposant est redirigé vers le formulaire de saisie.

### Pré-remplissage du formulaire

Le formulaire suivant est pré-rempli avec les valeurs du dernier élément
créé pour le même déposant et la même commune :

- `nom_deposant` ;
- `courriel_deposant` ;
- `telephone_deposant` ;
- `commune_deleguee`.

En l'absence de compte utilisateur, cette correspondance repose sur les
coordonnées saisies par le déposant. Le service de recherche devra donc
définir explicitement sa règle de correspondance, par exemple une égalité
normalisée sur le nom et le courriel lorsqu'il est disponible.

## Évolutions hors périmètre initial

Le rôle d'agent (correction, compilation et export) pourra nécessiter plus
tard :

- un champ d'état de traitement (`soumis`, `à corriger`, `validé`, `exporté`) ;
- les dates et auteurs des corrections ;
- une authentification pour les agents ;
- un journal des modifications.

Ces éléments ne sont pas ajoutés au modèle minimal tant que leurs règles
fonctionnelles ne sont pas précisées.