# Generated by Django 5.1.7 on 2025-03-20 20:29

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Convidado',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=255)),
                ('cpf', models.CharField(max_length=11, unique=True)),
                ('email', models.CharField(max_length=50, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Evento',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=255)),
                ('descricao', models.TextField(blank=True)),
                ('data', models.DateTimeField()),
                ('local', models.CharField(max_length=255)),
                ('criado_em', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Confirmacao',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('confirmado', models.BooleanField(default=False)),
                ('restricoes_alimentares', models.TextField(blank=True, null=True)),
                ('convidado', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='evento.convidado')),
            ],
        ),
        migrations.AddField(
            model_name='convidado',
            name='evento',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='evento.evento'),
        ),
    ]
