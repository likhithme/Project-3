# Generated by Django 5.1.2 on 2024-12-19 10:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0008_option_next_question_question_difficulty_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='option',
            name='next_question',
        ),
        migrations.AddField(
            model_name='option',
            name='explanation',
            field=models.TextField(blank=True, null=True),
        ),
    ]
