# Generated by Django 5.0.2 on 2024-04-17 01:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0004_employees'),
    ]

    operations = [
        migrations.AddField(
            model_name='employees',
            name='staff_status',
            field=models.BooleanField(default=False),
        ),
    ]
