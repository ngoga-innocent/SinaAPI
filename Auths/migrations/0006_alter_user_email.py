# Generated by Django 5.1.5 on 2025-02-04 17:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Auths', '0005_alter_user_email'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(blank=True, max_length=255, null=True),
        ),
    ]
