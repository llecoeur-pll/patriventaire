"""Views for submitting heritage elements."""

from __future__ import annotations

from typing import Any

from django.core.mail import send_mail
from django.db import transaction
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
	}
	return render(request, "element/ajouter.html", context)


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
