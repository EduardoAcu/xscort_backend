from django.db import migrations, models
import django.db.models.deletion


CITIES = [
    "Rancagua",
    "Curicó",
    "Talca",
    "Linares",
    "Chillán",
    "Los Ángeles",
    "Concepción",
    "Temuco",
    "Pucón",
    "Valdivia",
    "Osorno",
    "Puerto Montt",
]


def seed_ciudades(apps, schema_editor):
    Ciudad = apps.get_model("perfiles", "Ciudad")
    for order, name in enumerate(CITIES):
        Ciudad.objects.get_or_create(nombre=name, defaults={"ordering": order, "activa": True})


def migrate_perfiles_ciudad_fk(apps, schema_editor):
    Ciudad = apps.get_model("perfiles", "Ciudad")
    PerfilModelo = apps.get_model("perfiles", "PerfilModelo")
    SolicitudCambioCiudad = apps.get_model("perfiles", "SolicitudCambioCiudad")

    # Map city name to Ciudad instance
    name_to_city = {c.nombre: c for c in Ciudad.objects.all()}
    
    # Get default ciudad (first in list)
    default_ciudad = Ciudad.objects.first()
    if not default_ciudad:
        return  # No cities to assign

    for perfil in PerfilModelo.objects.all():
        old_name = getattr(perfil, "ciudad", None)
        ciudad_obj = name_to_city.get(old_name) if old_name else None
        # Assign default ciudad if no valid ciudad found
        perfil.ciudad_fk = ciudad_obj if ciudad_obj else default_ciudad
        perfil.save(update_fields=["ciudad_fk"])

    for solicitud in SolicitudCambioCiudad.objects.all():
        old_name = getattr(solicitud, "ciudad_nueva", None)
        ciudad_obj = name_to_city.get(old_name) if old_name else None
        # Assign default ciudad if no valid ciudad found
        solicitud.ciudad_nueva_fk = ciudad_obj if ciudad_obj else default_ciudad
        solicitud.save(update_fields=["ciudad_nueva_fk"])


class Migration(migrations.Migration):

    dependencies = [
        ("perfiles", "0010_alter_galeriafoto_imagen_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="Ciudad",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("nombre", models.CharField(max_length=120, unique=True)),
                ("ordering", models.PositiveIntegerField(default=0)),
                ("activa", models.BooleanField(default=True)),
            ],
            options={
                "verbose_name": "Ciudad",
                "verbose_name_plural": "Ciudades",
                "ordering": ["ordering", "nombre"],
            },
        ),
        migrations.AddField(
            model_name="perfilmodelo",
            name="ciudad_fk",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="+", to="perfiles.ciudad"),
        ),
        migrations.AddField(
            model_name="solicitudcambiociudad",
            name="ciudad_nueva_fk",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="+", to="perfiles.ciudad"),
        ),
        migrations.RunPython(seed_ciudades, migrations.RunPython.noop),
        migrations.RunPython(migrate_perfiles_ciudad_fk, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name="perfilmodelo",
            name="ciudad",
        ),
        migrations.RemoveField(
            model_name="solicitudcambiociudad",
            name="ciudad_nueva",
        ),
        migrations.RenameField(
            model_name="perfilmodelo",
            old_name="ciudad_fk",
            new_name="ciudad",
        ),
        migrations.RenameField(
            model_name="solicitudcambiociudad",
            old_name="ciudad_nueva_fk",
            new_name="ciudad_nueva",
        ),
        migrations.AlterField(
            model_name="perfilmodelo",
            name="ciudad",
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="perfiles", to="perfiles.ciudad"),
        ),
        migrations.AlterField(
            model_name="solicitudcambiociudad",
            name="ciudad_nueva",
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="solicitudes_cambio_ciudad", to="perfiles.ciudad"),
        ),
    ]
