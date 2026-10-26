"""Tests for the element views."""

from pathlib import Path

from django.core import mail
from django.test import override_settings
from django.urls import reverse

from ..models import Element, Photographie
from .utils import MediaTestCase, element_data, form_data, image_upload


class AjouterElementViewTests(MediaTestCase):
	@override_settings(DEBUG=False)
	def test_unknown_url_displays_custom_not_found_page(self) -> None:
		response = self.client.get("/chemin-introuvable/")

		self.assertEqual(response.status_code, 404)
		self.assertTemplateUsed(response, "404.html")
		self.assertContains(
			response,
			"Cette page est introuvable, mais pas de panique : même les panneaux "
			"se trompent parfois de chemin dans le Val d'Orne.",
			status_code=404,
		)
		self.assertContains(response, "Retrouver la carte", status_code=404)

	def test_map_page_is_displayed(self) -> None:
		response = self.client.get(reverse("element:carte"))

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "<h1>Carte</h1>", html=True)
		self.assertContains(response, 'id="map-widget"')
		self.assertContains(response, "openstreetmap.org")
		self.assertContains(response, "existing-elements-data")

	def test_map_uses_thumbnail_for_existing_public_elements(self) -> None:
		element = Element.objects.create(**element_data(is_valide=True))
		photo = Photographie.objects.create(element=element, fichier=image_upload())

		response = self.client.get(reverse("element:carte"))

		self.assertContains(response, element.libelle)
		self.assertContains(response, "photo_url")
		thumbnail_name = f"mini_{photo.fichier.name.rsplit('/', 1)[-1]}"
		self.assertTrue(response.context["existing_elements"][0]["photo_url"].endswith(thumbnail_name))

	@override_settings(DEBUG=False)
	def test_uploaded_media_is_served_when_debug_is_disabled(self) -> None:
		element = Element.objects.create(**element_data())
		photo = Photographie.objects.create(element=element, fichier=image_upload())

		response = self.client.get(photo.fichier.url)

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response["Content-Type"], "image/png")
		self.assertGreater(len(b"".join(response.streaming_content)), 0)

	def test_map_excludes_unvalidated_elements(self) -> None:
		unvalidated_element = Element.objects.create(**element_data())
		validated_element = Element.objects.create(
			**element_data(libelle="Élément validé", is_valide=True)
		)

		response = self.client.get(reverse("element:carte"))

		map_elements = response.context["existing_elements"]
		map_labels = {element["libelle"] for element in map_elements}

		self.assertNotIn(unvalidated_element.libelle, map_labels)
		self.assertIn(validated_element.libelle, map_labels)

	def test_index_displays_the_element_form(self) -> None:
		response = self.client.get(reverse("element:index"))

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "<h1>Carte</h1>", html=True)
		self.assertContains(response, 'id="map-widget"')

	def test_form_is_displayed(self) -> None:
		response = self.client.get(reverse("element:ajouter"))

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "Ajouter un élément de patrimoine")
		self.assertContains(response, 'class="alert alert-info"')
		self.assertContains(response, "plan local d'urbanisme intercommunal")
		self.assertContains(response, "partager votre expérience avec cet élément")
		self.assertContains(response, "Description et histoire")
		self.assertContains(response, "photographies-TOTAL_FORMS")
		self.assertContains(response, 'id="map-widget"')
		self.assertContains(response, 'id="geolocate-button"')
		self.assertContains(response, 'aria-label="Me localiser"')
		self.assertContains(response, "📍")
		self.assertContains(response, 'aria-live="polite"')
		self.assertContains(response, "openstreetmap.org")
		self.assertContains(response, 'name="referrer"')
		self.assertContains(response, "strict-origin-when-cross-origin")
		self.assertContains(response, "referrerPolicy")
		self.assertContains(response, 'type="hidden" name="latitude"')
		self.assertContains(response, 'type="hidden" name="longitude"')
		self.assertContains(response, "existing-elements-data")
		self.assertContains(response, "🌊 Mare")
		self.assertContains(response, "🧼 Lavoir")
		self.assertContains(response, 'class="btn btn-primary"')
		self.assertContains(response, 'class="row g-3 deposant-fields"')
		self.assertContains(response, 'class="col-12 mb-0"')
		self.assertContains(response, 'class="honeypot-field"')
		self.assertContains(response, 'id="camera-button"')
		self.assertContains(response, 'capture="environment"')
		self.assertNotContains(response, 'id="camera-viewfinder"')
		self.assertNotContains(response, "webcamjs")

	def test_map_contains_existing_public_elements(self) -> None:
		element = Element.objects.create(**element_data(is_valide=True))
		Photographie.objects.create(element=element, fichier=image_upload())

		response = self.client.get(reverse("element:ajouter"))

		self.assertContains(response, "Ancien lavoir")
		self.assertContains(response, "Lavoir")
		self.assertContains(response, "categorie_icone")
		self.assertContains(response, "photo_url")
		self.assertContains(response, "/media/photos/")

	def test_element_requires_a_photograph(self) -> None:
		response = self.client.post(
			reverse("element:ajouter"),
			form_data(
				**{
					"photographies-TOTAL_FORMS": "1",
					"photographies-INITIAL_FORMS": "0",
					"photographies-MIN_NUM_FORMS": "0",
					"photographies-MAX_NUM_FORMS": "1000",
				}
			),
		)

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "Ajoutez au moins une photographie")
		self.assertFalse(Element.objects.exists())

	def test_element_and_photograph_are_created(self) -> None:
		data = form_data(
			**{
				"photographies-TOTAL_FORMS": "1",
				"photographies-INITIAL_FORMS": "0",
				"photographies-MIN_NUM_FORMS": "0",
				"photographies-MAX_NUM_FORMS": "1000",
			}
		)
		data.update(
			{
				"photographies-0-fichier": image_upload(),
			}
		)
		response = self.client.post(reverse("element:ajouter"), data)

		self.assertRedirects(
			response,
			reverse("element:ajouter"),
			fetch_redirect_response=False,
		)
		self.assertEqual(Element.objects.count(), 1)
		self.assertEqual(Photographie.objects.count(), 1)
		element = Element.objects.get()
		photographie = Photographie.objects.get()
		photo_directory = Path(self.media_directory.name) / "photos" / str(element.pk)
		self.assertTrue(photo_directory.is_dir())
		self.assertEqual(
			Path(photographie.fichier.name).parts[:2],
			("photos", str(element.pk)),
		)

	def test_creation_sends_confirmation_email_and_prefills_next_form(self) -> None:
		data = form_data(
			**{
				"photographies-TOTAL_FORMS": "1",
				"photographies-INITIAL_FORMS": "0",
				"photographies-MIN_NUM_FORMS": "0",
				"photographies-MAX_NUM_FORMS": "1000",
			}
		)
		data["photographies-0-fichier"] = image_upload()

		response = self.client.post(reverse("element:ajouter"), data)
		element = Element.objects.get()

		self.assertRedirects(
			response,
			reverse("element:ajouter"),
			fetch_redirect_response=False,
		)
		self.assertEqual(len(mail.outbox), 1)
		self.assertEqual(
			mail.outbox[0].subject,
			"Merci pour votre contribution à l'inventaire patrimonial",
		)
		self.assertIn(
			reverse("element:consulter", kwargs={"numero": element.numero}),
			mail.outbox[0].body,
		)
		self.assertNotIn("Modifier la fiche", mail.outbox[0].body)
		self.assertNotIn(element.jeton_ecriture, mail.outbox[0].body)

		follow_up = self.client.get(response.url)

		self.assertContains(
			follow_up,
			f"Merci ! L'élément {element.libelle} a été ajouté. "
			"Il sera révisé par un modérateur avant publication sur la carte.",
			html=True,
		)
		self.assertContains(follow_up, 'value="alex@example.com"')
		self.assertContains(follow_up, 'value="7" selected')

	def test_element_can_be_viewed_by_number_and_edited_by_token(self) -> None:
		element = Element.objects.create(**element_data())
		Photographie.objects.create(element=element, fichier=image_upload())

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
		self.assertContains(read_response, 'class="element-photos"')
		self.assertContains(read_response, 'alt="Ancien lavoir"')
		self.assertEqual(edit_response.status_code, 200)
		self.assertContains(edit_response, "Modifier un élément de patrimoine")