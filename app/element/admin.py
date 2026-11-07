import re
from typing import Any

from django.contrib import admin, messages
from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.utils.html import format_html

from .models import Categorie, Commune, Element, Photographie


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
		"commune",
		"latitude",
		"longitude",
		"is_valide",
		"validation_action",
		"date_ajout",
	)
	list_display_links = ("numero", "libelle")
	list_filter = ("is_valide", "categorie", "commune", "date_ajout")
	search_fields = (
		"libelle",
		"courriel_deposant",
		"description",
	)
	readonly_fields = ("numero", "jeton_ecriture", "date_ajout")
	inlines = (PhotographieInline,)
	list_select_related = ("categorie",)
	date_hierarchy = "date_ajout"
	ordering = ("-date_ajout",)

	def changelist_view(
		self,
		request: HttpRequest,
		extra_context: dict[str, Any] | None = None,
	) -> HttpResponse:
		if request.method == "POST" and "_validate_element" in request.POST:
			if not self.has_change_permission(request):
				raise PermissionDenied

			element = self.get_object(request, request.POST["_validate_element"])
			if element is None:
				raise Http404
			if not self.has_change_permission(request, element):
				raise PermissionDenied

			if not element.is_valide:
				element.is_valide = True
				element.save(update_fields=("is_valide",))
				messages.success(request, f"L'élément « {element.libelle} » a été validé.")
			return redirect(request.get_full_path())

		return super().changelist_view(request, extra_context)

	@admin.display(description="Action")
	def validation_action(self, element: Element) -> str:
		if element.is_valide:
			return ""
		return format_html(
			'<button type="submit" class="button" name="_validate_element" '
			'value="{}">Valider</button>',
			element.pk,
		)


@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
	"""Admin interface for adding and editing categories."""

	list_display = ("libelle", "icone", "couleur_preview", "element_count")
	search_fields = ("libelle", "icone", "couleur")
	ordering = ("libelle",)

	@admin.display(description="couleur")
	def couleur_preview(self, categorie: Categorie) -> str:
		if not re.fullmatch(r"#[0-9A-Fa-f]{6}", categorie.couleur):
			return format_html("{}", categorie.couleur)
		return format_html(
			'<span title="{}" aria-label="Couleur {}" '
			'style="display: inline-block; width: 1em; height: 1em; '
			'background-color: {}; border: 1px solid #888; '
			'border-radius: 50%; vertical-align: middle;"></span>',
			categorie.couleur,
			categorie.couleur,
			categorie.couleur,
		)

	@admin.display(description="éléments")
	def element_count(self, categorie: Categorie) -> int:
		"""Return the number of elements using this category."""

		return categorie.elements.count()


@admin.register(Commune)
class CommuneAdmin(admin.ModelAdmin):
	"""Admin interface for adding and editing communes."""

	list_display = ("libelle", "element_count")
	search_fields = ("libelle",)
	ordering = ("libelle",)

	@admin.display(description="éléments")
	def element_count(self, commune: Commune) -> int:
		"""Return the number of elements using this commune."""

		return commune.elements.count()


@admin.register(Photographie)
class PhotographieAdmin(admin.ModelAdmin):
	"""Admin interface for standalone photograph management."""

	list_display = ("thumbnail", "id", "element", "fichier")
	search_fields = ("element__libelle",)
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
