# Generated by Django 5.1.7 on 2025-03-26 12:53

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='SystemeConfiguration',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cle', models.CharField(max_length=100, unique=True)),
                ('valeur', models.TextField()),
                ('description', models.TextField(blank=True, null=True)),
                ('date_modification', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Configuration système',
                'verbose_name_plural': 'Configurations système',
                'ordering': ['cle'],
            },
        ),
        migrations.CreateModel(
            name='ImportLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('source', models.CharField(choices=[('ORASS', 'ORASS'), ('HELIOS', 'HELIOS'), ('RH', 'Ressources Humaines'), ('MANUEL', 'Import manuel')], max_length=50)),
                ('fichier', models.FileField(blank=True, null=True, upload_to='imports/')),
                ('date_import', models.DateTimeField(auto_now_add=True)),
                ('nombre_enregistrements', models.IntegerField(default=0)),
                ('reussi', models.BooleanField(default=False)),
                ('message_erreur', models.TextField(blank=True, null=True)),
                ('utilisateur', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='imports', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': "Journal d'importation",
                'verbose_name_plural': 'Journal des importations',
                'ordering': ['-date_import'],
            },
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titre', models.CharField(max_length=255)),
                ('message', models.TextField()),
                ('niveau', models.CharField(choices=[('info', 'Information'), ('success', 'Succès'), ('warning', 'Avertissement'), ('error', 'Erreur')], default='info', max_length=20)),
                ('pour_tous', models.BooleanField(default=False)),
                ('lue', models.BooleanField(default=False)),
                ('date_creation', models.DateTimeField(auto_now_add=True)),
                ('date_expiration', models.DateTimeField(blank=True, null=True)),
                ('destinataire', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Notification',
                'verbose_name_plural': 'Notifications',
                'ordering': ['-date_creation'],
            },
        ),
    ]
