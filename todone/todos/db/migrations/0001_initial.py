# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-02-13 21:22
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Todo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.CharField(max_length=255)),
                ('folder', models.CharField(choices=[('INBOX', 'INBOX'), ('NEXT', 'NEXT'), ('TODAY', 'TODAY'), ('REMIND', 'REMIND'), ('SOMEDAY', 'SOMEDAY'), ('DONE', 'DONE'), ('CANCEL', 'CANCEL')], default='INBOX', max_length=15)),
                ('remind_date', models.DateField(blank=True, null=True)),
                ('date_completed', models.DateField(blank=True, null=True)),
                ('due_date', models.DateField(blank=True, null=True)),
                ('notes', models.TextField(blank=True)),
                ('repeat_interval', models.CharField(blank=True, max_length=10)),
            ],
        ),
    ]
