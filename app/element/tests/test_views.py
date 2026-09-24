"""Tests for the element views."""

from django.core import mail
from django.urls import reverse

from ..models import Element, Photographie
from .utils import MediaTestCase, element_data, form_data, image_upload


class AjouterElementViewTests(MediaTestCase):
	def test_map_page_is_displayed(self) -> None:
		response = self.client.get(reverse("element:carte"))

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "<h1>Carte</h1>", html=True)
		self.assertContains(response, 'id="map-widget"')
		self.assertContains(response, "openstreetmap.org")
		self.assertContains(response, "existing-elements-data")

	def test_map_contains_existing_public_elements(self) -> None:
		element = Element.objects.create(**element_data(is_valide=True))
		Photographie.objects.create(element=element, fichier=image_upload())

		response = self.client.get(reverse("element:carte"))

		self.assertContains(response, element.libelle)
		self.assertContains(response, "photo_url")

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
		self.assertContains(response, "photographies-TOTAL_FORMS")
		self.assertContains(response, 'id="map-widget"')
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
		self.assertContains(response, 'class="col-12 col-md-4 mb-0"')
		self.assertContains(response, 'class="honeypot-field"')
		self.assertContains(response, 'id="camera-button"')
		self.assertContains(response, 'id="camera-viewfinder"')
		self.assertContains(response, 'capture="environment"')
		self.assertContains(response, "webcamjs/1.0.26/webcam.min.js")

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

	def test_creation_sends_links_and_prefills_next_form(self) -> None:
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

		self.assertContains(
			follow_up,
			"L'élément a bien été ajouté. Un mail de confirmation a été envoyé.",
			html=True,
		)
		self.assertContains(follow_up, 'value="Alex Martin"')
		self.assertContains(follow_up, 'value="alex@example.com"')
		self.assertContains(follow_up, 'value="0600000000"')
		self.assertContains(follow_up, 'value="7" selected')

	def test_element_can_be_viewed_by_number_and_edited_by_token(self) -> None:
		element = Element.objects.create(**element_data())

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