# Generated by Django 2.2 on 2020-02-18 15:34

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mydiplom', '0009_auto_20200218_1720'),
    ]

    operations = [
        migrations.AddField(
            model_name='claim',
            name='restore_request',
            field=models.BooleanField(default=False, verbose_name='Запрос на восстановление'),
        ),
        migrations.AlterField(
            model_name='myuser',
            name='birthday',
            field=models.DateField(default=datetime.datetime(1990, 2, 18, 5, 34, 34, 921570), verbose_name='Дата рождения'),
        ),
    ]
