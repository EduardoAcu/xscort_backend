from django.db import migrations, models
import django.db.models.deletion


SERVICIOS_SEED = [
    {"nombre": "Acompañamiento a eventos", "permite_custom": False},
    {"nombre": "Cenas", "permite_custom": False},
    {"nombre": "Viajes", "permite_custom": False},
    {"nombre": "Servicio exclusivo", "permite_custom": True},
]


def seed_servicios(apps, schema_editor):
    Catalogo = apps.get_model("perfiles", "ServicioCatalogo")
    for item in SERVICIOS_SEED:
        Catalogo.objects.get_or_create(nombre=item["nombre"], defaults={"permite_custom": item["permite_custom"], "activo": True})


def migrate_servicios(apps, schema_editor):
    Catalogo = apps.get_model("perfiles", "ServicioCatalogo")
    Servicio = apps.get_model("perfiles", "Servicio")
    # Intentar mapear por nombre exacto
    name_map = {c.nombre.lower(): c for c in Catalogo.objects.all()}
    for svc in Servicio.objects.all():
        nombre = getattr(svc, "nombre", "") or ""
        catalogo = name_map.get(nombre.lower())
        if catalogo:
            svc.catalogo = catalogo
            svc.custom_text = None
        else:
            svc.custom_text = nombre
        svc.save(update_fields=["catalogo", "custom_text"])


class Migration(migrations.Migration):

    dependencies = [
        ("perfiles", "0011_ciudad_catalogo_fk"),
    ]

    operations = [
        migrations.CreateModel(
            name="ServicioCatalogo",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("nombre", models.CharField(max_length=120, unique=True)),
                ("activo", models.BooleanField(default=True)),
                ("permite_custom", models.BooleanField(default=False)),
            ],
            options={
                "verbose_name": "Servicio de catálogo",
                "verbose_name_plural": "Servicios de catálogo",
                "ordering": ["nombre"],
            },
        ),
        migrations.AddField(
            model_name="servicio",
            name="catalogo",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="servicios", to="perfiles.serviciocatalogo"),
        ),
        migrations.AddField(
            model_name="servicio",
            name="custom_text",
            field=models.CharField(blank=True, max_length=120, null=True),
        ),
        migrations.RunPython(seed_servicios, migrations.RunPython.noop),
        migrations.RunPython(migrate_servicios, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name="servicio",
            name="nombre",
        ),
    ]
