"""Tests for the element models."""

from io import BytesIO
from pathlib import Path

from PIL import Image
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings

from ..models import Categorie, Element, Histoire, Photographie
from .utils import MediaTestCase, element_data, image_upload


class ElementModelTests(MediaTestCase):
	def test_element_generates_a_unique_edit_token_and_timestamp(self) -> None:
		element = Element.objects.create(**element_data())

		self.assertTrue(element.jeton_ecriture)
		self.assertEqual(len(element.jeton_ecriture), 43)
		self.assertEqual(element.photo_miniature, "")
		self.assertIsNotNone(element.date_ajout)
		self.assertEqual(str(element), f"{element.numero} - Ancien lavoir")

		second_element = Element.objects.create(**element_data(libelle="Une mare"))
		self.assertNotEqual(element.jeton_ecriture, second_element.jeton_ecriture)

	def test_element_stores_thumbnail_location(self) -> None:
		element = Element.objects.create(
			**element_data(photo_miniature="miniatures/ancien-lavoir.jpg")
		)

		element.refresh_from_db()

		self.assertEqual(element.photo_miniature, "miniatures/ancien-lavoir.jpg")

	def test_histoire_defaults_to_unvalidated_and_records_creation_time(self) -> None:
		element = Element.objects.create(**element_data())

		histoire = Histoire.objects.create(element=element, histoire="Un récit.")

		self.assertFalse(histoire.valide)
		self.assertIsNotNone(histoire.created)
		self.assertEqual(element.histoires.get(), histoire)
		self.assertEqual(str(histoire), f"Histoire de l'élément {element.pk}")

	def test_deleting_element_deletes_its_histories(self) -> None:
		element = Element.objects.create(**element_data())
		histoire = Histoire.objects.create(element=element, histoire="Un récit.")

		element.delete()

		self.assertFalse(Histoire.objects.filter(pk=histoire.pk).exists())

	def test_coordinates_outside_allowed_ranges_are_invalid(self) -> None:
		element = Element(**element_data(latitude=91, longitude=-181))

		with self.assertRaises(ValidationError):
			element.full_clean()

	def test_deleting_element_deletes_its_photographs(self) -> None:
		element = Element.objects.create(**element_data())
		photo = Photographie.objects.create(element=element, fichier=image_upload())
		other_element = Element.objects.create(
			**element_data(libelle="Autre élément")
		)
		other_photo = Photographie.objects.create(
			element=other_element,
			fichier=image_upload(),
		)
		original_path = photo.fichier.name
		thumbnail_path = Path(photo.fichier.path).with_name(
			f"mini_{Path(photo.fichier.path).name}"
		)
		storage = photo.fichier.storage
		other_thumbnail_path = Path(other_photo.fichier.path).with_name(
			f"mini_{Path(other_photo.fichier.path).name}"
		)

		with self.captureOnCommitCallbacks(execute=True):
			element.delete()

		self.assertEqual(Photographie.objects.count(), 1)
		self.assertFalse(storage.exists(original_path))
		self.assertFalse(thumbnail_path.exists())
		self.assertTrue(other_photo.fichier.storage.exists(other_photo.fichier.name))
		self.assertTrue(other_thumbnail_path.exists())

	def test_deleting_photo_record_removes_original_and_thumbnail(self) -> None:
		element = Element.objects.create(**element_data())
		photo = Photographie.objects.create(element=element, fichier=image_upload())
		other_photo = Photographie.objects.create(element=element, fichier=image_upload())
		original_path = photo.fichier.name
		thumbnail_path = Path(photo.fichier.path).with_name(
			f"mini_{Path(photo.fichier.path).name}"
		)
		storage = photo.fichier.storage
		other_thumbnail_path = Path(other_photo.fichier.path).with_name(
			f"mini_{Path(other_photo.fichier.path).name}"
		)

		with self.captureOnCommitCallbacks(execute=True):
			photo.delete()

		self.assertFalse(storage.exists(original_path))
		self.assertFalse(thumbnail_path.exists())
		self.assertTrue(other_photo.fichier.storage.exists(other_photo.fichier.name))
		self.assertTrue(other_thumbnail_path.exists())

	def test_bulk_deleting_photos_removes_each_original_and_thumbnail(self) -> None:
		element = Element.objects.create(**element_data())
		other_element = Element.objects.create(
			**element_data(libelle="Autre élément")
		)
		photos = [
			Photographie.objects.create(element=element, fichier=image_upload())
			for _ in range(2)
		]
		other_photo = Photographie.objects.create(
			element=other_element,
			fichier=image_upload(),
		)
		other_thumbnail_path = Path(other_photo.fichier.path).with_name(
			f"mini_{Path(other_photo.fichier.path).name}"
		)
		paths = [
			(
				photo.fichier.storage,
				photo.fichier.name,
				Path(photo.fichier.path).with_name(
					f"mini_{Path(photo.fichier.path).name}"
				),
			)
			for photo in photos
		]

		with self.captureOnCommitCallbacks(execute=True):
			Photographie.objects.filter(element=element).delete()

		for storage, original_path, thumbnail_path in paths:
			self.assertFalse(storage.exists(original_path))
			self.assertFalse(thumbnail_path.exists())
		self.assertTrue(other_photo.fichier.storage.exists(other_photo.fichier.name))
		self.assertTrue(other_thumbnail_path.exists())

	def test_photos_use_configured_directory_and_random_names(self) -> None:
		element = Element.objects.create(**element_data())

		with override_settings(PHOTO_UPLOAD_DIR="custom-photos"):
			first_photo = Photographie.objects.create(
				element=element,
				fichier=image_upload(),
			)
			second_photo = Photographie.objects.create(
				element=element,
				fichier=image_upload(),
			)

		self.assertTrue(first_photo.fichier.name.startswith("custom-photos/"))
		self.assertTrue(second_photo.fichier.name.startswith("custom-photos/"))
		self.assertTrue(first_photo.fichier.name.endswith(".png"))
		self.assertNotEqual(first_photo.fichier.name, second_photo.fichier.name)

	def test_photo_is_resized_to_1920_pixels_and_keeps_its_ratio(self) -> None:
		element = Element.objects.create(**element_data())
		image_buffer = BytesIO()
		Image.new("RGB", (2400, 1200), color="red").save(
			image_buffer,
			format="PNG",
		)
		image_buffer.seek(0)
		photo = Photographie.objects.create(
			element=element,
			fichier=SimpleUploadedFile(
				"panorama.png",
				image_buffer.read(),
				content_type="image/png",
			),
		)

		with Image.open(photo.fichier.path) as saved_image:
			self.assertEqual(saved_image.size, (1920, 960))

		thumbnail_path = Path(photo.fichier.path).with_name(
			f"mini_{Path(photo.fichier.path).name}"
		)
		self.assertTrue(thumbnail_path.is_file())
		with Image.open(thumbnail_path) as thumbnail:
			self.assertEqual(thumbnail.size, (180, 90))


class CategorieModelTests(MediaTestCase):
	def test_migration_seeds_the_seven_categories(self) -> None:
		self.assertEqual(Categorie.objects.count(), 7)
		self.assertEqual(
			set(Categorie.objects.values_list("libelle", flat=True)),
			{
				"Mare",
				"Puit ou fontaine",
				"Ruine ou bâtisse ancienne",
				"Lavoir",
				"Arbre remarquable",
				"Calvaire",
				"Autre",
			},
		)
		self.assertEqual(Categorie.objects.values_list("icone", flat=True).distinct().count(), 7)
		self.assertEqual(Categorie.objects.values_list("couleur", flat=True).distinct().count(), 7)