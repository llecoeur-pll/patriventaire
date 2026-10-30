"""Tests for the element forms."""

from ..forms import ElementForm, PhotographieFormSet
from ..models import Element
from .utils import MediaTestCase, element_data, form_data, image_upload


class ElementFormTests(MediaTestCase):
	def test_form_is_valid_with_complete_data(self) -> None:
		form = ElementForm(data=form_data())

		self.assertTrue(form.is_valid(), form.errors)

	def test_form_requires_the_main_fields(self) -> None:
		form = ElementForm(data={})

		self.assertFalse(form.is_valid())
		for field_name in (
			"libelle",
			"categorie",
			"commune",
			"latitude",
			"longitude",
			"description",
		):
			self.assertIn(field_name, form.errors)

	def test_form_accepts_blank_optional_email(self) -> None:
		data = form_data(courriel_deposant="")
		form = ElementForm(data=data)

		self.assertTrue(form.is_valid(), form.errors)

	def test_form_does_not_expose_removed_fields(self) -> None:
		form = ElementForm()

		self.assertNotIn("nom_deposant", form.fields)
		self.assertNotIn("histoire", form.fields)

	def test_form_rejects_a_filled_honeypot(self) -> None:
		form = ElementForm(data=form_data(website="https://spam.example"))

		self.assertFalse(form.is_valid())
		self.assertIn("website", form.errors)

	def test_form_rejects_invalid_email_and_coordinates(self) -> None:
		form = ElementForm(
			data=form_data(
				courriel_deposant="adresse-invalide",
				latitude="91",
				longitude="-181",
			)
		)

		self.assertFalse(form.is_valid())
		self.assertIn("courriel_deposant", form.errors)
		self.assertIn("latitude", form.errors)
		self.assertIn("longitude", form.errors)


class PhotographieFormSetTests(MediaTestCase):
	def test_formset_accepts_no_photograph(self) -> None:
		element = Element.objects.create(**element_data())
		formset = PhotographieFormSet(
			data={
				"photographies-TOTAL_FORMS": "1",
				"photographies-INITIAL_FORMS": "0",
				"photographies-MIN_NUM_FORMS": "0",
				"photographies-MAX_NUM_FORMS": "1000",
			},
			instance=element,
		)

		self.assertTrue(formset.is_valid(), formset.errors)

	def test_formset_accepts_a_photograph(self) -> None:
		element = Element.objects.create(**element_data())
		formset = PhotographieFormSet(
			data={
				"photographies-TOTAL_FORMS": "1",
				"photographies-INITIAL_FORMS": "0",
				"photographies-MIN_NUM_FORMS": "0",
				"photographies-MAX_NUM_FORMS": "1000",
			},
			files={"photographies-0-fichier": image_upload()},
			instance=element,
		)

		self.assertTrue(formset.is_valid(), formset.errors)