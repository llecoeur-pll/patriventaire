"""Forms for submitting heritage elements and their photographs."""

from __future__ import annotations

from django import forms
from django.forms import inlineformset_factory

from .models import Element, Photographie


class ElementForm(forms.ModelForm):
	"""Public form used to create a heritage element."""

	website = forms.CharField(
		required=False,
		label="",
		widget=forms.TextInput(
			attrs={
				"autocomplete": "off",
				"tabindex": "-1",
				"aria-hidden": "true",
			}
		),
	)

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.fields["description"].label = "Description et histoire"
		self.fields["categorie"].choices = [
			(
				category.pk,
				f"{category.icone} {category.libelle}",
			)
			for category in self.fields["categorie"].queryset
		]

	def clean_website(self) -> str:
		"""Reject submissions that fill the invisible bot trap."""

		website = self.cleaned_data["website"]
		if website:
			raise forms.ValidationError("Soumission automatique détectée.")
		return website

	class Meta:
		model = Element
		fields = (
			"website",
			"libelle",
			"courriel_deposant",
			"categorie",
			"commune",
			"latitude",
			"longitude",
			"description",
		)
		widgets = {
			"description": forms.Textarea(attrs={"rows": 5}),
			"latitude": forms.NumberInput(attrs={"step": "0.000001"}),
			"longitude": forms.NumberInput(attrs={"step": "0.000001"}),
		}


PhotographieFormSet = inlineformset_factory(
	Element,
	Photographie,
	fields=("fichier",),
	extra=1,
	can_delete=False,
)