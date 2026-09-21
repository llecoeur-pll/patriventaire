import base64

from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError
from django.core import mail
from django.test import TestCase
from django.urls import reverse

from .forms import ElementForm, PhotographieFormSet
from .models import Element, Photographie


class ElementModelTests(TestCase):
	"""Tests for the heritage element model."""

	def test_element_generates_a_unique_edit_token_and_timestamp(self) -> None:
		element = Element.objects.create(**self._element_data())

		self.assertTrue(element.jeton_ecriture)
		self.assertEqual(len(element.jeton_ecriture), 43)
		self.assertIsNotNone(element.date_ajout)
		self.assertEqual(str(element), f"{element.numero} - Ancien lavoir")

		second_element = Element.objects.create(**self._element_data(libelle="Une mare"))
		self.assertNotEqual(element.jeton_ecriture, second_element.jeton_ecriture)

	def test_coordinates_outside_allowed_ranges_are_invalid(self) -> None:
		element = Element(**self._element_data(latitude=91, longitude=-181))

		with self.assertRaises(ValidationError):
			element.full_clean()

	def test_deleting_element_deletes_its_photographs(self) -> None:
		element = Element.objects.create(**self._element_data())
		Photographie.objects.create(
			element=element,
			fichier=SimpleUploadedFile(
				"patrimoine.png",
				base64.b64decode(
					"iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk"
					"+A8AAQUBAScY42YAAAAASUVORK5CYII="
				),
			),
		)

		element.delete()

		self.assertFalse(Photographie.objects.exists())

	@staticmethod
	def _element_data(**extra: object) -> dict[str, object]:
		data = {
			"libelle": "Ancien lavoir",
			"nom_deposant": "Alex Martin",
			"courriel_deposant": "alex@example.com",
			"telephone_deposant": "0600000000",
			"categorie": Element.Category.LAVOIR,
			"commune_deleguee": Element.Commune.RABODANGES,
			"latitude": 48.75,
			"longitude": -0.25,
			"description": "Un ancien lavoir communal.",
			"histoire": "Construit au XIXe siècle.",
		}
		data.update(extra)
		return data


class ElementFormTests(TestCase):
	"""Tests for the heritage element form."""

	def test_form_is_valid_with_complete_data(self) -> None:
		form = ElementForm(data=self._form_data())

		self.assertTrue(form.is_valid(), form.errors)

	def test_form_requires_the_main_fields(self) -> None:
		form = ElementForm(data={})

		self.assertFalse(form.is_valid())
		for field_name in (
			"libelle",
			"nom_deposant",
			"categorie",
			"commune_deleguee",
			"latitude",
			"longitude",
			"description",
		):
			self.assertIn(field_name, form.errors)

	def test_form_accepts_blank_optional_contact_and_history(self) -> None:
		data = self._form_data()
		data.update(
			{
				"courriel_deposant": "",
				"telephone_deposant": "",
				"histoire": "",
			}
		)
		form = ElementForm(data=data)

		self.assertTrue(form.is_valid(), form.errors)

	def test_form_rejects_invalid_email_and_coordinates(self) -> None:
		data = self._form_data(
			courriel_deposant="adresse-invalide",
			latitude="91",
			longitude="-181",
		)
		form = ElementForm(data=data)

		self.assertFalse(form.is_valid())
		self.assertIn("courriel_deposant", form.errors)
		self.assertIn("latitude", form.errors)
		self.assertIn("longitude", form.errors)

	@staticmethod
	def _form_data(**extra: str) -> dict[str, str]:
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
		}
		data.update(extra)
		return data


class PhotographieFormSetTests(TestCase):
	"""Tests for the required photograph formset."""

	def test_formset_requires_at_least_one_photograph(self) -> None:
		element = Element.objects.create(**ElementModelTests._element_data())
		formset = PhotographieFormSet(
			data={
				"photographies-TOTAL_FORMS": "1",
				"photographies-INITIAL_FORMS": "0",
				"photographies-MIN_NUM_FORMS": "0",
				"photographies-MAX_NUM_FORMS": "1000",
			},
			instance=element,
		)

		self.assertFalse(formset.is_valid())
		self.assertIn("Ajoutez au moins une photographie", str(formset.non_form_errors()))

	def test_formset_accepts_a_photograph(self) -> None:
		element = Element.objects.create(**ElementModelTests._element_data())
		formset = PhotographieFormSet(
			data={
				"photographies-TOTAL_FORMS": "1",
				"photographies-INITIAL_FORMS": "0",
				"photographies-MIN_NUM_FORMS": "0",
				"photographies-MAX_NUM_FORMS": "1000",
				"photographies-0-commentaire": "Vue principale",
			},
			files={
				"photographies-0-fichier": SimpleUploadedFile(
					"patrimoine.png",
					base64.b64decode(
						"iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk"
						"+A8AAQUBAScY42YAAAAASUVORK5CYII="
					),
					content_type="image/png",
				)
			},
			instance=element,
		)

		self.assertTrue(formset.is_valid(), formset.errors)


class AjouterElementViewTests(TestCase):
	"""Tests for the public element creation form."""

	def test_index_displays_the_element_form(self) -> None:
		response = self.client.get(reverse("element:index"))

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "Ajouter un élément de patrimoine")

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
					base64.b64decode(
						"iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk"
						"+A8AAQUBAScY42YAAAAASUVORK5CYII="
					),
					content_type="image/png",
				),
				"photographies-0-commentaire": "Vue principale",
			}
		)
		response = self.client.post(
			reverse("element:ajouter"),
			data,
		)

		self.assertRedirects(
			response,
			reverse("element:ajouter"),
			fetch_redirect_response=False,
		)
		self.assertEqual(Element.objects.count(), 1)
		self.assertEqual(Photographie.objects.count(), 1)

	def test_creation_sends_links_and_prefills_next_form(self) -> None:
		data = self._element_data(
			**{
				"photographies-TOTAL_FORMS": "1",
				"photographies-INITIAL_FORMS": "0",
				"photographies-0-fichier": SimpleUploadedFile(
					"patrimoine.png",
					base64.b64decode(
						"iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk"
						"+A8AAQUBAScY42YAAAAASUVORK5CYII="
					),
					content_type="image/png",
				),
			}
		)

		response = self.client.post(reverse("element:ajouter"), data)
		element = Element.objects.get()

		self.assertRedirects(
			response,
			reverse("element:ajouter"),
			fetch_redirect_response=False,
		)
		self.assertEqual(len(mail.outbox), 1)
		self.assertIn(
			reverse("element:consulter", kwargs={"numero": element.numero}),
			mail.outbox[0].body,
		)
		self.assertIn(
			reverse(
				"element:modifier",
				kwargs={"jeton_ecriture": element.jeton_ecriture},
			),
			mail.outbox[0].body,
		)

		follow_up = self.client.get(response.url)

		self.assertContains(follow_up, 'value="Alex Martin"')
		self.assertContains(follow_up, 'value="alex@example.com"')
		self.assertContains(follow_up, 'value="0600000000"')
		self.assertContains(follow_up, 'value="Rabodanges"')

	def test_element_can_be_viewed_by_number_and_edited_by_token(self) -> None:
		element = Element.objects.create(**ElementModelTests._element_data())

		read_response = self.client.get(
			reverse("element:consulter", kwargs={"numero": element.numero})
		)
		edit_response = self.client.get(
			reverse(
				"element:modifier",
				kwargs={"jeton_ecriture": element.jeton_ecriture},
			)
		)

		self.assertEqual(read_response.status_code, 200)
		self.assertContains(read_response, element.libelle)
		self.assertEqual(edit_response.status_code, 200)
		self.assertContains(edit_response, "Modifier un élément de patrimoine")

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
