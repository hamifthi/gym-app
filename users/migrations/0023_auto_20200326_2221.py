# Generated by Django 3.0.3 on 2020-03-26 22:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0022_auto_20200326_1408'),
    ]

    operations = [
        migrations.AlterField(
            model_name='athlete',
            name='sport_field',
            field=models.CharField(choices=[('Aerobic', 'Aerobic'), ('Fitness', 'Fitness'), ('TRX', 'TRX'), ('Bodybuilding', 'Bodybuilding'), ('Physic', 'Physic'), ('Crossfit', 'Crossfit')], max_length=12, null=True),
        ),
        migrations.AlterField(
            model_name='coach',
            name='sport_field',
            field=models.CharField(choices=[('Aerobic', 'Aerobic'), ('Fitness', 'Fitness'), ('TRX', 'TRX'), ('Bodybuilding', 'Bodybuilding'), ('Physic', 'Physic'), ('Crossfit', 'Crossfit')], max_length=12, null=True),
        ),
    ]