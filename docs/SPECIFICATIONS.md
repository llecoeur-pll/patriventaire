Tu es un architecte logiciel Django expert.

Toi et moi allons développer une application web simple avec le framework Django permettant d'inventorier et de cartographier des éléments de patrimoine sur un secteur donné.

Un élément de patrimoine dans ce prompt sera aussi appelé simplement élément parfois.
L'utilisateur est la personne qui saisira un élément de patrimoine
L'agent est la personne qui compilera, corrigera et exportera les éléments de patrimoine listés par les utilisateurs

Les acteurs sont :
 - Utilisateur
 - Administrateur

L'interface utilisateur n'aura aucune authentification. Les utilisateurs arriveront directement sur un formulaire sans authentification ou il pourra :

 - donner un nom a l'élément de patrimoine
 - donner ses coordonnées
 - catégoriser l'élément
 - la commune déléguée
 - le placer sur une carte
 - Décrire l'élément de patrimoine
 - de manière factultative, fournir une histoire, une annecdote plus ou moins personnelle sur l'élément
 - envoyer des photos de l'élément, qui pourront être enrichies de données
 
Un élément est caractérisé par 
 - Un numéro unique
 - Une suite de caractères unique et aléatoire pour accéder a cet élément en écriture
 - Un libellé
 - Les coordonnées de la personne qui l'a posté:
    - nom et prénom, ou pseudo
    - courriel (facultatif)
    - téléphone (facultatif)
 - la catégorie de l'élément, qui peut être :
    - Mare
    - Puit ou fontaine
    - Ruine ou Bâtisse ancienne
    - Lavoir
    - Arbre remarquable
    - Autre
 - La commune déléguée, listée par ordre alphabétique :
    - Putanges-Pont-Ecrepin
    - Les-Rotours
    - Rabodanges
    - Sainte-Croix-Sur-Orne
    - Saint-Aubert
    - La-Forêt-Auvray
    - Chênedouit
    - Ménil-Jean
    - La-Fresnaye-Aux-Sauvages
 - les coordonnées GPS
 - Une description
 - une histoire
 - DUne ou plusieurs photographies
 - La date d'ajout de l'élément, remplis autotatiquement en base
 
 
 Une photographie est caractérisée par:
  - L'élément auquel il est rattaché
  - Le fichier image associé
  - Un commentaire (facultatif)


A la validation d'un élément :
 - Si un mail a été fourni, envoyer un mail de confirmation, avec un message de remerciements contenant :
   - Un lien, avec le numéro unique de l'élément, pour accéder aux données en lecture seule
   - Un autre lien, avec la suite de caractères aléatoire, pour accéder au formulaire et pouvoir modifier la fiche de l'élément.

 - Rediriger vers le formulaire pré-remplis des éléments correspondant à la personne venant de remplir : coordonnées de la personne, et commune déléguée.




---

# Identité visuelle

L'identité de l'application repose sur deux éléments forts du logo :

🟢 Le territoire, la nature et le patrimoine représentés par le vert.

🔵 L'eau, les lacs et l'Orne représentés par le bleu.

L'interface doit rester sobre et privilégier l'efficacité d'usage plutôt que les effets graphiques.

---

# Palette de couleurs

## Couleur principale

Vert territorial inspiré du logo.

```css
--primary: #78BE00;

Utilisations
Boutons principaux
Menus actifs
Liens importants
Icônes principales
Titres de sections
Couleur secondaire

Bleu inspiré de la rivière et des lacs.

--secondary: #169AEF;

Utilisations
Actions secondaires
Navigation
Informations
Éléments interactifs
Couleur d'accent

Vert foncé.

--accent: #009933;

Utilisations
Survol de boutons
Validation
Mise en avant
Couleurs neutres
--background: #F8FAFB;
--surface: #FFFFFF;
--text: #263238;
--text-light: #607D8B;
--border: #DCE3E7;

Couleurs fonctionnelles
Succès
--success: #2E7D32;

Information
--info: #169AEF;

Attention
--warning: #F4B400;

Erreur
--danger: #D93025;

Typographie
Police principale
Inter

Police moderne, extrêmement lisible sur ordinateur, tablette et téléphone.

Import CSS :

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

Police de secours
font-family:
    "Inter",
    "Roboto",
    "Segoe UI",
    sans-serif;

Hiérarchie typographique
Titre principal
font-size: 32px;
font-weight: 700;
line-height: 1.2;

Titre de page
font-size: 24px;
font-weight: 600;

Titre de section
font-size: 18px;
font-weight: 600;

Texte courant
font-size: 16px;
font-weight: 400;
line-height: 1.5;

Texte secondaire
font-size: 14px;
font-weight: 400;
color: var(--text-light);

Styles CSS de référence
Variables globales
:root {

  --primary: #78BE00;
  --secondary: #169AEF;
  --accent: #009933;

  --background: #F8FAFB;
  --surface: #FFFFFF;

  --text: #263238;
  --text-light: #607D8B;

  --border: #DCE3E7;

  --success: #2E7D32;
  --warning: #F4B400;
  --danger: #D93025;
}

Boutons
Bouton principal
.btn-primary {
    background: var(--primary);
    color: white;
    border: none;
    border-radius: 8px;
    padding: 12px 20px;
    font-weight: 600;
    cursor: pointer;
}

Survol
.btn-primary:hover {
    background: var(--accent);
}

Bouton secondaire
.btn-secondary {
    background: var(--secondary);
    color: white;
    border: none;
    border-radius: 8px;
    padding: 12px 20px;
}

Cartes

Toutes les fonctionnalités citoyennes doivent être présentées sous forme de cartes.

.card {
    background: white;
    border-radius: 12px;
    border: 1px solid var(--border);
    padding: 20px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

Formulaires
input,
select,
textarea {

    border: 1px solid var(--border);

    border-radius: 8px;

    padding: 12px;

    font-size: 16px;

    width: 100%;
}

Focus
input:focus,
textarea:focus {

    outline: none;

    border-color: var(--secondary);

    box-shadow: 0 0 0 3px rgba(22,154,239,0.15);
}

Navigation
Barre supérieure
.header {
    background: white;
    border-bottom: 1px solid var(--border);
}

Menu actif
.menu-active {

    color: var(--primary);

    border-bottom: 3px solid var(--primary);
}


