from django.contrib import admin
from django.utils.html import format_html

from .models import Categorie, Element, Photographie


class PhotographieInline(admin.TabularInline):
	"""Manage an element's photographs from its admin page."""

	model = Photographie
	extra = 1
	fields = ("fichier",)


@admin.register(Element)
class ElementAdmin(admin.ModelAdmin):
	"""Admin interface for heritage elements."""

	list_display = (
		"numero",
		"libelle",
		"categorie",
		"commune_deleguee",
		"nom_deposant",
		"is_valide",
		"date_ajout",
	)
	list_display_links = ("numero", "libelle")
	list_filter = ("is_valide", "categorie", "commune_deleguee", "date_ajout")
	search_fields = (
		"libelle",
		"nom_deposant",
		"courriel_deposant",
		"telephone_deposant",
		"description",
		"histoire",
	)
	readonly_fields = ("numero", "jeton_ecriture", "date_ajout")
	inlines = (PhotographieInline,)
	list_select_related = ("categorie",)
	date_hierarchy = "date_ajout"
	ordering = ("-date_ajout",)


@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
	"""Admin interface for adding and editing categories."""

	list_display = ("libelle", "icone", "couleur", "element_count")
	search_fields = ("libelle", "icone", "couleur")
	ordering = ("libelle",)

	@admin.display(description="éléments")
	def element_count(self, categorie: Categorie) -> int:
		"""Return the number of elements using this category."""

		return categorie.elements.count()


@admin.register(Photographie)
class PhotographieAdmin(admin.ModelAdmin):
	"""Admin interface for standalone photograph management."""

	list_display = ("thumbnail", "id", "element", "fichier")
	search_fields = ("element__libelle", "element__nom_deposant")
	list_select_related = ("element",)

	@admin.display(description="aperçu")
	def thumbnail(self, photographie: Photographie) -> str:
		"""Return a proportional thumbnail for the admin list."""

		if not photographie.fichier:
			return "-"
		return format_html(
			'<img src="{}" alt="{}" style="max-height: 40px; width: auto;">',
			photographie.fichier.url,
			str(photographie),
		)
