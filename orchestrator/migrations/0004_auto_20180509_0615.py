# Generated by Django 2.0.5 on 2018-05-09 06:15

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orchestrator', '0003_auto_20180509_0612'),
    ]

    operations = [
        migrations.AlterField(
            model_name='testrequest',
            name='errors',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.TextField(), null=True, size=None),
        ),
        migrations.AlterField(
            model_name='testrequest',
            name='failures',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.TextField(), null=True, size=None),
        ),
    ]