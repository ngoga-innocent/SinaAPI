# Generated by Django 5.1.5 on 2025-04-05 17:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Auths', '0009_user_country'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='profile',
            field=models.ImageField(blank=True, default='profile_images/defaultProfile.jpg', null=True, upload_to='profile_images/'),
        ),
    ]
