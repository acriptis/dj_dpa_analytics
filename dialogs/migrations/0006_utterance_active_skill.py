# Generated by Django 3.0.1 on 2020-04-04 13:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dialogs', '0005_auto_20200109_1113'),
    ]

    operations = [
        migrations.AddField(
            model_name='utterance',
            name='active_skill',
            field=models.CharField(blank=True, max_length=2064, null=True),
        ),
    ]
