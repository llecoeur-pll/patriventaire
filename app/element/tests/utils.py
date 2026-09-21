"""Shared fixtures for element tests."""

import base64
from tempfile import TemporaryDirectory

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings

from ..models import Categorie, Element


class MediaTestCase(TestCase):
	"""Run each test with an isolated temporary media directory."""

	def setUp(self) -> None:
		super().setUp()
		self.media_directory = TemporaryDirectory()
		self.media_settings = override_settings(MEDIA_ROOT=self.media_directory.name)
		self.media_settings.enable()

	def tearDown(self) -> None:
		self.media_settings.disable()
		self.media_directory.cleanup()
		super().tearDown()


def element_data(**extra: object) -> dict[str, object]:
	data = {
		"libelle": "Ancien lavoir",
		"nom_deposant": "Alex Martin",
		"courriel_deposant": "alex@example.com",
		"telephone_deposant": "0600000000",
		"categorie": Categorie.objects.get(libelle="Lavoir"),
		"commune_deleguee": Element.Commune.RABODANGES,
		"latitude": 48.75,
		"longitude": -0.25,
		"description": "Un ancien lavoir communal.",
		"histoire": "Construit au XIXe siècle.",
	}
	data.update(extra)
	return data


def form_data(**extra: str) -> dict[str, str]:
	data = {
		"libelle": "Ancien lavoir",
		"nom_deposant": "Alex Martin",
		"courriel_deposant": "alex@example.com",
		"telephone_deposant": "0600000000",
		"categorie": Categorie.objects.get(libelle="Lavoir").pk,
		"commune_deleguee": Element.Commune.RABODANGES,
		"latitude": "48.750000",
		"longitude": "-0.250000",
		"description": "Un ancien lavoir communal.",
		"histoire": "Construit au XIXe siècle.",
	}
	data.update(extra)
	return data


def image_upload() -> SimpleUploadedFile:
	return SimpleUploadedFile(
		"patrimoine.png",
		base64.b64decode(
			"iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk"
			"+A8AAQUBAScY42YAAAAASUVORK5CYII="
		),
		content_type="image/png",
	)