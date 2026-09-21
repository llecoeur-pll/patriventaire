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
			"nom_deposant",
			"categorie",
			"commune_deleguee",
			"latitude",
			"longitude",
			"description",
		):
			self.assertIn(field_name, form.errors)

	def test_form_accepts_blank_optional_contact_and_history(self) -> None:
		data = form_data(
			courriel_deposant="",
			telephone_deposant="",
			histoire="",
		)
		form = ElementForm(data=data)

		self.assertTrue(form.is_valid(), form.errors)

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
	def test_formset_requires_at_least_one_photograph(self) -> None:
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

		self.assertFalse(formset.is_valid())
		self.assertIn("Ajoutez au moins une photographie", str(formset.non_form_errors()))

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