# Generated by Django 2.2 on 2020-02-10 09:58

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mydiplom', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='myuser',
            name='birthday',
            field=models.DateField(default=datetime.datetime(1990, 2, 9, 23, 58, 29, 398586), verbose_name='Дата рождения'),
        ),
    ]