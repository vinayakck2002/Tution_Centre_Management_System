# Generated by Django 5.1.1 on 2025-04-24 05:37

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stdapp', '0004_student'),
    ]

    operations = [
        migrations.CreateModel(
            name='Gender',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('men', models.CharField(max_length=250)),
                ('women', models.CharField(max_length=250)),
            ],
        ),
        migrations.AddField(
            model_name='student',
            name='gender',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='stdapp.gender'),
        ),
    ]
