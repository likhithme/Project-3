# Generated by Django 5.1.3 on 2024-11-19 13:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0005_rename_age_category_scenario_category'),
    ]

    operations = [
        migrations.RenameField(
            model_name='scenario',
            old_name='category',
            new_name='age_category',
        ),
    ]
