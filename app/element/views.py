"""Views for submitting heritage elements."""

from __future__ import annotations

from typing import Any

from django.core.mail import send_mail
from django.db import transaction
from django.contrib import messages
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .forms import ElementForm, PhotographieFormSet
from .models import Element


def ajouter_element(request: HttpRequest) -> HttpResponse:
	"""Display and process the public heritage element form."""

	if request.method == "POST":
		element_form = ElementForm(request.POST)
		photographie_formset = PhotographieFormSet(
			request.POST,
			request.FILES,
		)
		if element_form.is_valid() and photographie_formset.is_valid():
			with transaction.atomic():
				element = element_form.save()
				photographie_formset.instance = element
				photographie_formset.save()
			_send_confirmation_email(request, element)
			messages.success(
				request,
				"L'élément a bien été ajouté. Un mail de confirmation a été envoyé."
			)
			request.session["element_form_initial"] = {
				"nom_deposant": element.nom_deposant,
				"courriel_deposant": element.courriel_deposant,
				"telephone_deposant": element.telephone_deposant,
				"commune_deleguee": element.commune_deleguee,
			}
			return redirect("element:ajouter")
	else:
		element_form = ElementForm(
			initial=request.session.pop("element_form_initial", None)
		)
		photographie_formset = PhotographieFormSet()

	context: dict[str, Any] = {
		"element_form": element_form,
		"photographie_formset": photographie_formset,
		"existing_elements": _map_elements_data(),
	}
	return render(request, "element/ajouter.html", context)


def carte(request: HttpRequest) -> HttpResponse:
	"""Display the map page for public heritage elements."""

	return render(
		request,
		"element/carte.html",
		{"existing_elements": _map_elements_data()},
	)


def consulter_element(request: HttpRequest, numero: int) -> HttpResponse:
	"""Display an element using its public number."""

	element = get_object_or_404(Element, numero=numero)
	return render(request, "element/consulter.html", {"element": element})


def modifier_element(request: HttpRequest, jeton_ecriture: str) -> HttpResponse:
	"""Display and process an element form using its private edit token."""

	element = get_object_or_404(Element, jeton_ecriture=jeton_ecriture)
	if request.method == "POST":
		element_form = ElementForm(request.POST, instance=element)
		photographie_formset = PhotographieFormSet(
			request.POST,
			request.FILES,
			instance=element,
		)
		if element_form.is_valid() and photographie_formset.is_valid():
			with transaction.atomic():
				element_form.save()
				photographie_formset.save()
			return redirect(
				"element:modifier",
				jeton_ecriture=element.jeton_ecriture,
			)
	else:
		element_form = ElementForm(instance=element)
		photographie_formset = PhotographieFormSet(instance=element)

	return render(
		request,
		"element/ajouter.html",
		{
			"element_form": element_form,
			"photographie_formset": photographie_formset,
			"page_title": "Modifier un élément de patrimoine",
			"submit_label": "Enregistrer les modifications",
		},
	)


def _send_confirmation_email(request: HttpRequest, element: Element) -> None:
	if not element.courriel_deposant:
		return

	read_url = request.build_absolute_uri(
		reverse("element:consulter", kwargs={"numero": element.numero})
	)
	edit_url = request.build_absolute_uri(
		reverse(
			"element:modifier",
			kwargs={"jeton_ecriture": element.jeton_ecriture},
		)
	)
	send_mail(
		subject="Votre élément de patrimoine a bien été enregistré",
		message=(
			f"Merci pour votre contribution.\n\n"
			f"Consulter la fiche : {read_url}\n"
			f"Modifier la fiche : {edit_url}"
		),
		from_email=None,
		recipient_list=[element.courriel_deposant],
		fail_silently=False,
	)


def _map_elements_data() -> list[dict[str, Any]]:
	"""Return public fields used to display existing elements on the map."""

	map_elements = []
	for element in Element.objects.prefetch_related("photographies").all():
		photo = element.photographies.first()
		map_elements.append(
			{
				"numero": element.numero,
				"libelle": element.libelle,
				"categorie": element.categorie.libelle,
				"categorie_icone": element.categorie.icone,
				"categorie_couleur": element.categorie.couleur,
				"latitude": float(element.latitude),
				"longitude": float(element.longitude),
				"photo_url": photo.fichier.url if photo else None,
			}
		)
	return map_elements
