# Generated by Django 4.0.6 on 2022-07-12 07:24

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0004_task_todo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='created',
            field=models.DateTimeField(default=datetime.datetime.now),
        ),
    ]
