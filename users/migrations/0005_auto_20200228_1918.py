# Generated by Django 3.0.3 on 2020-02-28 15:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_auto_20200227_1529'),
    ]

    operations = [
        migrations.AlterField(
            model_name='financialtradeoff',
            name='code',
            field=models.CharField(max_length=10),
        ),
    ]
