# Generated by Django 3.0.3 on 2020-04-13 11:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_auto_20200408_1418'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='person',
            name='code',
        ),
        migrations.DeleteModel(
            name='Token',
        ),
    ]