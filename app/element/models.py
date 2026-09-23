"""Models for the public heritage inventory."""

from __future__ import annotations

import secrets
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


def generate_edit_token() -> str:
	"""Return a cryptographically secure token for editing an element."""

	return secrets.token_urlsafe(32)


def photo_upload_to(instance: "Photographie", filename: str) -> str:
	"""Return a configurable directory and a unique random image filename."""

	extension = Path(filename).suffix.lower()
	return f"{settings.PHOTO_UPLOAD_DIR}/{secrets.token_urlsafe(24)}{extension}"


class Element(models.Model):
	"""A heritage item submitted by a public user."""

	class Commune(models.TextChoices):
		"""Communes deleguees covered by the inventory."""

		CHENEDOUIT = "Chênedouit", "Chênedouit"
		FORET_AUVRAY = "La-Forêt-Auvray", "La-Forêt-Auvray"
		FRESNAYE_SAUVAGES = "La-Fresnaye-Aux-Sauvages", "La-Fresnaye-Aux-Sauvages"
		LES_ROTOURS = "Les-Rotours", "Les-Rotours"
		MENIL_JEAN = "Ménil-Jean", "Ménil-Jean"
		PUTANGES_PONT_ECREPIN = "Putanges-Pont-Ecrepin", "Putanges-Pont-Ecrepin"
		RABODANGES = "Rabodanges", "Rabodanges"
		SAINT_AUBERT = "Saint-Aubert", "Saint-Aubert"
		SAINTE_CROIX_ORNE = "Sainte-Croix-Sur-Orne", "Sainte-Croix-Sur-Orne"

	numero: int = models.BigAutoField(
		primary_key=True,
		verbose_name="numéro",
	)
	jeton_ecriture: str = models.CharField(
		max_length=64,
		unique=True,
		default=generate_edit_token,
		editable=False,
		verbose_name="jeton d'écriture",
		help_text="Jeton secret permettant de modifier la fiche.",
	)
	libelle: str = models.CharField(
		max_length=255,
		verbose_name="libellé",
	)
	nom_deposant: str = models.CharField(
		max_length=255,
		verbose_name="nom du déposant",
	)
	courriel_deposant: str = models.EmailField(
		blank=True,
		verbose_name="courriel du déposant",
	)
	telephone_deposant: str = models.CharField(
		max_length=30,
		blank=True,
		verbose_name="téléphone du déposant",
	)
	categorie: "Categorie" = models.ForeignKey(
		"Categorie",
		on_delete=models.PROTECT,
		related_name="elements",
		verbose_name="catégorie",
	)
	commune_deleguee: str = models.CharField(
		max_length=32,
		choices=Commune,
		verbose_name="commune déléguée",
	)
	latitude: Decimal = models.DecimalField(
		max_digits=9,
		decimal_places=6,
		validators=[MinValueValidator(-90), MaxValueValidator(90)],
		verbose_name="latitude",
	)
	longitude: Decimal = models.DecimalField(
		max_digits=9,
		decimal_places=6,
		validators=[MinValueValidator(-180), MaxValueValidator(180)],
		verbose_name="longitude",
	)
	description: str = models.TextField(
		verbose_name="description",
	)
	histoire: str = models.TextField(
		blank=True,
		verbose_name="histoire ou anecdote",
	)
	date_ajout: datetime = models.DateTimeField(
		auto_now_add=True,
		verbose_name="date d'ajout",
	)
	is_valide: bool = models.BooleanField(
		default=False,
		verbose_name="validé",
		help_text="Indique si l'élément peut être affiché publiquement.",
	)

	class Meta:
		"""Database metadata and integrity rules for an element."""

		ordering = ("-date_ajout",)
		verbose_name = "élément de patrimoine"
		verbose_name_plural = "éléments de patrimoine"
		indexes = (
			models.Index(fields=("categorie",), name="element_categorie_idx"),
			models.Index(
				fields=("commune_deleguee",),
				name="element_commune_idx",
			),
			models.Index(fields=("date_ajout",), name="element_date_ajout_idx"),
			models.Index(fields=("is_valide",), name="element_is_valide_idx"),
			models.Index(
				fields=("latitude", "longitude"),
				name="element_coordonnees_idx",
			),
		)
		constraints = (
			models.CheckConstraint(
				condition=models.Q(latitude__gte=-90)
				& models.Q(latitude__lte=90),
				name="element_latitude_valid",
			),
			models.CheckConstraint(
				condition=models.Q(longitude__gte=-180)
				& models.Q(longitude__lte=180),
				name="element_longitude_valid",
			),
		)

	def __str__(self) -> str:
		"""Return a human-readable identifier."""

		return f"{self.numero} - {self.libelle}"


class Categorie(models.Model):
	"""A category used to classify heritage elements."""

	id: int = models.BigAutoField(primary_key=True)
	libelle: str = models.CharField(max_length=100, unique=True, verbose_name="libellé")
	icone: str = models.CharField(max_length=8, unique=True, verbose_name="icône")
	couleur: str = models.CharField(max_length=7, unique=True, verbose_name="couleur")

	class Meta:
		ordering = ("libelle",)
		verbose_name = "catégorie"
		verbose_name_plural = "catégories"

	def __str__(self) -> str:
		return self.libelle


class Photographie(models.Model):
	"""An image attached to a heritage element."""

	id: int = models.BigAutoField(
		primary_key=True,
		verbose_name="identifiant",
	)
	element: Element = models.ForeignKey(
		Element,
		on_delete=models.CASCADE,
		related_name="photographies",
		verbose_name="élément de patrimoine",
	)
	fichier: str = models.ImageField(
		upload_to=photo_upload_to,
		verbose_name="fichier image",
	)

	class Meta:
		"""Database metadata for an element photograph."""

		ordering = ("id",)
		verbose_name = "photographie"
		verbose_name_plural = "photographies"
		indexes = (
			models.Index(fields=("element",), name="photo_element_idx"),
		)

	def __str__(self) -> str:
		"""Return a human-readable identifier."""

		return f"Photographie de l'élément {self.element_id}"
