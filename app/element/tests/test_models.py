"""Tests for the element models."""

from django.core.exceptions import ValidationError
from ..models import Element, Photographie
from .utils import MediaTestCase, element_data, image_upload


class ElementModelTests(MediaTestCase):
	def test_element_generates_a_unique_edit_token_and_timestamp(self) -> None:
		element = Element.objects.create(**element_data())

		self.assertTrue(element.jeton_ecriture)
		self.assertEqual(len(element.jeton_ecriture), 43)
		self.assertIsNotNone(element.date_ajout)
		self.assertEqual(str(element), f"{element.numero} - Ancien lavoir")

		second_element = Element.objects.create(**element_data(libelle="Une mare"))
		self.assertNotEqual(element.jeton_ecriture, second_element.jeton_ecriture)

	def test_coordinates_outside_allowed_ranges_are_invalid(self) -> None:
		element = Element(**element_data(latitude=91, longitude=-181))

		with self.assertRaises(ValidationError):
			element.full_clean()

	def test_deleting_element_deletes_its_photographs(self) -> None:
		element = Element.objects.create(**element_data())
		Photographie.objects.create(element=element, fichier=image_upload())

		element.delete()

		self.assertFalse(Photographie.objects.exists())