# Generated by Django 3.0.1 on 2023-05-03 14:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dialogs', '0010_auto_20230503_1419'),
    ]

    operations = [
        migrations.AlterField(
            model_name='utterance',
            name='text',
            field=models.CharField(max_length=4064),
        ),
    ]
