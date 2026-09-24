from django.db import migrations, models
import django.db.models.deletion


COMMUNES = (
    "Chênedouit",
    "La-Forêt-Auvray",
    "La-Fresnaye-Aux-Sauvages",
    "Les-Rotours",
    "Ménil-Jean",
    "Putanges-Pont-Ecrepin",
    "Rabodanges",
    "Saint-Aubert",
    "Sainte-Croix-Sur-Orne",
)


def seed_communes(apps, schema_editor):
    Commune = apps.get_model("element", "Commune")
    for libelle in COMMUNES:
        Commune.objects.get_or_create(libelle=libelle)


def migrate_element_communes(apps, schema_editor):
    Element = apps.get_model("element", "Element")
    Commune = apps.get_model("element", "Commune")
    commune_ids = {
        commune.libelle: commune.pk
        for commune in Commune.objects.all()
    }
    for element in Element.objects.all().iterator():
        element.commune_temp_id = commune_ids[element.commune_deleguee]
        element.save(update_fields=("commune_temp",))


class Migration(migrations.Migration):

    dependencies = [
        ("element", "0007_alter_element_courriel_deposant_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="Commune",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "libelle",
                    models.CharField(
                        max_length=100,
                        unique=True,
                        verbose_name="libellé",
                    ),
                ),
            ],
            options={
                "ordering": ("libelle",),
                "verbose_name": "commune",
                "verbose_name_plural": "communes",
            },
        ),
        migrations.RunPython(seed_communes, migrations.RunPython.noop),
        migrations.AddField(
            model_name="element",
            name="commune_temp",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to="element.commune",
                verbose_name="commune temporaire",
            ),
        ),
        migrations.RunPython(
            migrate_element_communes,
            migrations.RunPython.noop,
        ),
        migrations.RemoveIndex(
            model_name="element",
            name="element_commune_idx",
        ),
        migrations.RemoveField(
            model_name="element",
            name="commune_deleguee",
        ),
        migrations.RenameField(
            model_name="element",
            old_name="commune_temp",
            new_name="commune",
        ),
        migrations.AlterField(
            model_name="element",
            name="commune",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="elements",
                to="element.commune",
                verbose_name="commune",
            ),
        ),
        migrations.AddIndex(
            model_name="element",
            index=models.Index(
                fields=["commune"],
                name="element_commune_idx",
            ),
        ),
    ]
