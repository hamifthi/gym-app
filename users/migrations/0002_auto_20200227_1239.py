# Generated by Django 3.0.3 on 2020-02-27 09:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='person',
            name='email',
            field=models.EmailField(max_length=100, null=True, unique=True),
        ),
    ]