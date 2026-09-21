"""URLs for the heritage element application."""

from django.urls import path

from . import views

app_name = "element"

urlpatterns = [
	path("", views.ajouter_element, name="index"),
	path("ajouter/", views.ajouter_element, name="ajouter"),
	path("element/<int:numero>/", views.consulter_element, name="consulter"),
	path(
		"element/modifier/<str:jeton_ecriture>/",
		views.modifier_element,
		name="modifier",
	),
]