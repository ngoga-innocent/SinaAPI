# Generated by Django 5.1.5 on 2025-02-04 17:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Auths', '0002_alter_user_options_alter_user_managers_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_staff',
            field=models.BooleanField(default=False),
        ),
    ]
