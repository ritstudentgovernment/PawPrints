# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-16 18:27
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Petition',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=80)),
                ('description', models.TextField()),
                ('signatures', models.PositiveIntegerField(default=0)),
                ('created_at', models.DateTimeField()),
                ('status', models.PositiveSmallIntegerField(default=0)),
                ('expires', models.DateTimeField()),
                ('last_signed', models.DateTimeField(blank=True, default=None, null=True)),
                ('has_response', models.BooleanField(default=False)),
                ('in_progress', models.BooleanField(null=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Response',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField()),
                ('created_at', models.DateTimeField()),
                ('author', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Update',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField()),
                ('created_at', models.DateTimeField()),
            ],
        ),
        migrations.AddField(
            model_name='petition',
            name='response',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='petitions.Response'),
        ),
        migrations.AddField(
            model_name='petition',
            name='tags',
            field=models.ManyToManyField(to='petitions.Tag'),
        ),
        migrations.AddField(
            model_name='petition',
            name='updates',
            field=models.ManyToManyField(default=None, to='petitions.Update'),
        ),
    ]
