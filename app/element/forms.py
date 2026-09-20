"""Forms for submitting heritage elements and their photographs."""

from __future__ import annotations

from django import forms
from django.forms import BaseInlineFormSet, inlineformset_factory

from .models import Element, Photographie


class ElementForm(forms.ModelForm):
	"""Public form used to create a heritage element."""

	class Meta:
		model = Element
		fields = (
			"libelle",
			"nom_deposant",
			"courriel_deposant",
			"telephone_deposant",
			"categorie",
			"commune_deleguee",
			"latitude",
			"longitude",
			"description",
			"histoire",
		)
		widgets = {
			"description": forms.Textarea(attrs={"rows": 5}),
			"histoire": forms.Textarea(attrs={"rows": 4}),
			"latitude": forms.NumberInput(attrs={"step": "0.000001"}),
			"longitude": forms.NumberInput(attrs={"step": "0.000001"}),
		}


class PhotographiesFormSet(BaseInlineFormSet):
	"""Require at least one photograph for every submitted element."""

	def clean(self) -> None:
		super().clean()
		if any(self.errors):
			return
		if not any(form.cleaned_data and not form.cleaned_data.get("DELETE") for form in self.forms):
			raise forms.ValidationError(
				"Ajoutez au moins une photographie de l'élément."
			)


PhotographieFormSet = inlineformset_factory(
	Element,
	Photographie,
	formset=PhotographiesFormSet,
	fields=("fichier", "commentaire"),
	extra=1,
	can_delete=False,
)