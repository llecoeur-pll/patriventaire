"""URLs for the heritage element application."""

from django.urls import path

from . import views

app_name = "element"

urlpatterns = [
	path("ajouter/", views.ajouter_element, name="ajouter"),
]