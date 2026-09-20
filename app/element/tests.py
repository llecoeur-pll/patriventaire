from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from .models import Element, Photographie


class AjouterElementViewTests(TestCase):
	"""Tests for the public element creation form."""

	def test_form_is_displayed(self) -> None:
		response = self.client.get(reverse("element:ajouter"))

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "Ajouter un élément de patrimoine")
		self.assertContains(response, "photographies-TOTAL_FORMS")

	def test_element_requires_a_photograph(self) -> None:
		response = self.client.post(
			reverse("element:ajouter"),
			self._element_data(),
		)

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "Ajoutez au moins une photographie")
		self.assertFalse(Element.objects.exists())

	def test_element_and_photograph_are_created(self) -> None:
		data = self._element_data(
			**{
				"photographies-TOTAL_FORMS": "1",
				"photographies-INITIAL_FORMS": "0",
			}
		)
		data.update(
			{
				"photographies-0-fichier": SimpleUploadedFile(
					"patrimoine.png",
					b"\x89PNG\r\n\x1a\n",
					content_type="image/png",
				),
				"photographies-0-commentaire": "Vue principale",
			}
		)
		response = self.client.post(
			reverse("element:ajouter"),
			data,
		)

		self.assertRedirects(response, reverse("element:ajouter"))
		self.assertEqual(Element.objects.count(), 1)
		self.assertEqual(Photographie.objects.count(), 1)

	@staticmethod
	def _element_data(**extra: str) -> dict[str, str]:
		data = {
			"libelle": "Ancien lavoir",
			"nom_deposant": "Alex Martin",
			"courriel_deposant": "alex@example.com",
			"telephone_deposant": "0600000000",
			"categorie": Element.Category.LAVOIR,
			"commune_deleguee": Element.Commune.RABODANGES,
			"latitude": "48.750000",
			"longitude": "-0.250000",
			"description": "Un ancien lavoir communal.",
			"histoire": "Construit au XIXe siècle.",
			"photographies-TOTAL_FORMS": "1",
			"photographies-INITIAL_FORMS": "0",
			"photographies-MIN_NUM_FORMS": "0",
			"photographies-MAX_NUM_FORMS": "1000",
		}
		data.update(extra)
		return data
