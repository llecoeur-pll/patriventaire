from django.db import migrations


def add_calvaire_category(apps, schema_editor):
	"""Add the Calvaire category when it is not already present."""

	Categorie = apps.get_model("element", "Categorie")
	Categorie.objects.get_or_create(
		libelle="Calvaire",
		defaults={
			"icone": "✝️",
			"couleur": "#8D6E63",
		},
	)


def remove_calvaire_category(apps, schema_editor):
	"""Remove Calvaire when reversing this migration."""

	Categorie = apps.get_model("element", "Categorie")
	Categorie.objects.filter(libelle="Calvaire").delete()


class Migration(migrations.Migration):

	dependencies = [
		("element", "0005_element_is_valide_element_element_is_valide_idx"),
	]

	operations = [
		migrations.RunPython(add_calvaire_category, remove_calvaire_category),
	]