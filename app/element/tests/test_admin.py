"""Tests for the element administration interface."""

from pathlib import PurePosixPath

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from .utils import MediaTestCase, element_data, image_upload
from ..models import Categorie, Element, Photographie


class ElementAdminTests(MediaTestCase):
	def setUp(self) -> None:
		super().setUp()
		self.client = Client(enforce_csrf_checks=True)
		admin_user = get_user_model().objects.create_superuser(
			username="admin",
			email="admin@example.com",
			password="password",
		)
		self.client.force_login(admin_user)
		self.changelist_url = reverse("admin:element_element_changelist")

	def test_unvalidated_element_can_be_validated_from_its_row(self) -> None:
		element = Element.objects.create(**element_data())
		Element.objects.create(**element_data(libelle="Déjà validé", is_valide=True))

		response = self.client.get(self.changelist_url)

		self.assertContains(response, f'name="_validate_element" value="{element.pk}"')
		self.assertContains(response, "48.750000")
		self.assertContains(response, "-0.250000")
		self.assertContains(response, "Valider", count=1)
		csrf_token = response.cookies["csrftoken"].value

		get_response = self.client.get(
			self.changelist_url,
			{"_validate_element": element.pk},
		)
		self.assertRedirects(get_response, f"{self.changelist_url}?e=1")
		element.refresh_from_db()
		self.assertFalse(element.is_valide)

		post_response = self.client.post(
			self.changelist_url,
			{
				"_validate_element": element.pk,
				"csrfmiddlewaretoken": csrf_token,
			},
		)

		self.assertRedirects(post_response, self.changelist_url)
		element.refresh_from_db()
		self.assertTrue(element.is_valide)
		self.assertNotContains(self.client.get(self.changelist_url), "Valider")

	def test_changelist_displays_photograph_count_for_each_element(self) -> None:
		element_with_photos = Element.objects.create(**element_data())
		for _ in range(2):
			Photographie.objects.create(
				element=element_with_photos,
				fichier=image_upload(),
			)
		element_without_photos = Element.objects.create(
			**element_data(libelle="Élément sans photographie")
		)

		response = self.client.get(self.changelist_url)

		self.assertContains(
			response,
			'<td class="field-photograph_count">2</td>',
			html=True,
		)
		self.assertContains(
			response,
			'<td class="field-photograph_count">0</td>',
			html=True,
		)

	def test_element_change_page_displays_each_associated_photo(self) -> None:
		element = Element.objects.create(**element_data())
		photo_one = Photographie.objects.create(
			element=element,
			fichier=image_upload(),
		)
		photo_two = Photographie.objects.create(
			element=element,
			fichier=image_upload(),
		)
		Photographie.objects.create(
			element=Element.objects.create(**element_data(libelle="Autre élément")),
			fichier=image_upload(),
		)

		response = self.client.get(
			reverse("admin:element_element_change", args=(element.pk,))
		)
		thumbnail_paths = (
			str(
				PurePosixPath(photo.fichier.name).with_name(
					f"mini_{PurePosixPath(photo.fichier.name).name}"
				)
			)
			for photo in (photo_one, photo_two)
		)
		thumbnail_urls = [
			photo_one.fichier.storage.url(path) for path in thumbnail_paths
		]

		for thumbnail_url in thumbnail_urls:
			self.assertContains(response, f'src="{thumbnail_url}"')
			thumbnail_response = self.client.get(thumbnail_url)
			self.assertEqual(thumbnail_response.status_code, 200)
			self.assertEqual(thumbnail_response["Content-Type"], "image/png")
		self.assertContains(response, "max-height: 120px;")


class CategorieAdminTests(TestCase):
	def setUp(self) -> None:
		self.client = Client()
		admin_user = get_user_model().objects.create_superuser(
			username="admin",
			email="admin@example.com",
			password="test-password",
		)
		self.client.force_login(admin_user)

	def test_category_color_is_displayed_as_a_swatch(self) -> None:
		Categorie.objects.create(
			libelle="Catégorie de test",
			icone="🧪",
			couleur="#123456",
		)

		response = self.client.get(reverse("admin:element_categorie_changelist"))

		self.assertContains(response, "background-color: #123456;")
		self.assertContains(response, 'aria-label="Couleur #123456"')
		self.assertNotContains(response, '<td class="field-couleur_preview">#123456</td>')

	def test_invalid_color_is_displayed_as_escaped_text(self) -> None:
		Categorie.objects.create(
			libelle="Couleur invalide",
			icone="⚠️",
			couleur='"><sc',
		)

		response = self.client.get(reverse("admin:element_categorie_changelist"))

		self.assertContains(response, "&quot;&gt;&lt;sc")
		self.assertNotContains(response, 'background-color: "><sc;')