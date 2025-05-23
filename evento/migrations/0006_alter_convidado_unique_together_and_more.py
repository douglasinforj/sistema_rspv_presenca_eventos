# Generated by Django 5.1.7 on 2025-03-31 11:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('evento', '0005_alter_convidado_cpf_alter_convidado_email_and_more'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='convidado',
            unique_together=set(),
        ),
        migrations.AddConstraint(
            model_name='convidado',
            constraint=models.UniqueConstraint(fields=('cpf', 'evento'), name='unique_cpf_evento'),
        ),
    ]
