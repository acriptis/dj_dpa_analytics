# Generated by Django 3.0.1 on 2023-05-03 14:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dialogs', '0009_dialog_dialog_json'),
    ]

    operations = [
        migrations.AlterField(
            model_name='utterancehypothesis',
            name='text',
            field=models.CharField(max_length=4064),
        ),
    ]