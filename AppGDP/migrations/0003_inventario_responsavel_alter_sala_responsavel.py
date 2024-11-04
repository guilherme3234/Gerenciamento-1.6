# Generated by Django 5.1.1 on 2024-10-22 18:49

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('AppGDP', '0002_sala_quantidade_itens'),
    ]

    operations = [
        migrations.AddField(
            model_name='inventario',
            name='responsavel',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='AppGDP.sala', to_field='responsavel'),
        ),
        migrations.AlterField(
            model_name='sala',
            name='responsavel',
            field=models.CharField(max_length=50, unique=True),
        ),
    ]
