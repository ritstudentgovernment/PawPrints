# Generated by Django 2.1.3 on 2019-02-12 19:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profile', '0002_auto_20180126_1900'),
    ]

    operations = [
        migrations.CreateModel(
            name='GlobalAlert',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('active', models.BooleanField(default=True)),
                ('content', models.TextField()),
            ],
        ),
    ]
