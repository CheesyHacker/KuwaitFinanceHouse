# Generated by Django 5.0.2 on 2024-04-25 11:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0010_employees_designation'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='documents',
            name='is_private',
        ),
    ]
