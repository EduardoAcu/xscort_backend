from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0004_alter_customuser_foto_documento_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='privacy_version',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='customuser',
            name='terms_version',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.CreateModel(
            name='LegalDocument',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo', models.CharField(choices=[('terms', 'Términos y Condiciones'), ('privacy', 'Política de Privacidad')], max_length=20)),
                ('version', models.CharField(max_length=50)),
                ('body', models.TextField()),
                ('is_current', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['-created_at'],
                'unique_together': {('tipo', 'version')},
            },
        ),
        migrations.CreateModel(
            name='AgeConsentLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('accepted_at', models.DateTimeField(auto_now_add=True)),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('user_agent', models.TextField(blank=True, null=True)),
                ('terms_version', models.CharField(blank=True, max_length=50, null=True)),
                ('privacy_version', models.CharField(blank=True, max_length=50, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='age_consents', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-accepted_at'],
            },
        ),
    ]
