# Generated by Django 5.1.3 on 2024-11-19 13:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0003_option_points'),
    ]

    operations = [
        migrations.RenameField(
            model_name='scenario',
            old_name='category',
            new_name='age_category',
        ),
    ]