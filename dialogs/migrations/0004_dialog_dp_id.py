# Generated by Django 3.0.1 on 2019-12-31 08:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dialogs', '0003_auto_20191231_0810'),
    ]

    operations = [
        migrations.AddField(
            model_name='dialog',
            name='dp_id',
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
    ]
