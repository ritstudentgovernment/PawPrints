# Generated by Django 2.0.1 on 2018-01-26 19:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('petitions', '0002_auto_20180124_2016'),
    ]

    operations = [
        migrations.AddField(
            model_name='petition',
            name='old_id',
            field=models.CharField(blank=True, default=None, max_length=20, null=True),
        ),
    ]