# Generated by Django 5.1.3 on 2024-11-19 13:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0004_rename_category_scenario_age_category'),
    ]

    operations = [
        migrations.RenameField(
            model_name='scenario',
            old_name='age_category',
            new_name='category',
        ),
    ]
