# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2017-04-13 12:36
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('courses', '0012_auto_20161004_0927'),
    ]

    operations = [
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=60)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='courses.Course')),
                ('members', models.ManyToManyField(blank=True, related_name='course_groups', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['course', 'title'],
            },
        ),
    ]
