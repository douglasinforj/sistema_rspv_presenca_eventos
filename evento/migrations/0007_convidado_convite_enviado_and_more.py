# Generated by Django 5.1.7 on 2025-04-13 09:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('evento', '0006_alter_convidado_unique_together_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='convidado',
            name='convite_enviado',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='convidado',
            name='data_envio_convite',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
