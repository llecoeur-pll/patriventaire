"""Views for submitting heritage elements."""

from __future__ import annotations

from typing import Any

from django.db import transaction
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from .forms import ElementForm, PhotographieFormSet


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
			return redirect("element:ajouter")
	else:
		element_form = ElementForm()
		photographie_formset = PhotographieFormSet()

	context: dict[str, Any] = {
		"element_form": element_form,
		"photographie_formset": photographie_formset,
	}
	return render(request, "element/ajouter.html", context)
