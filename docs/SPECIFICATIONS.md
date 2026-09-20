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



