# Generated by Django 2.2.4 on 2025-06-27 07:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('families_app', '0003_task_point'),
    ]

    operations = [
        migrations.RenameField(
            model_name='task',
            old_name='point',
            new_name='points',
        ),
    ]
