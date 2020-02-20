# Generated by Django 2.2 on 2020-02-20 20:53

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mydiplom', '0010_auto_20200218_1734'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='myuser',
            name='user_IP',
        ),
        migrations.AlterField(
            model_name='claim',
            name='finally_rejected_comment',
            field=models.TextField(default='Заявку невозможно обработать', max_length=10000, verbose_name='Причина окончательного отклонения'),
        ),
        migrations.AlterField(
            model_name='claim',
            name='restore_request_text',
            field=models.TextField(default='Просьба восстановить заявку', max_length=10000, verbose_name='Причина восстановления'),
        ),
        migrations.AlterField(
            model_name='myuser',
            name='birthday',
            field=models.DateField(default=datetime.datetime(1990, 2, 20, 10, 53, 10, 722479), verbose_name='Дата рождения'),
        ),
    ]
