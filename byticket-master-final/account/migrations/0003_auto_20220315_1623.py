# Generated by Django 2.0 on 2022-03-15 08:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0002_seat_name_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='seat',
            name='seat_status',
            field=models.CharField(blank=True, max_length=2, null=True, verbose_name='seat status'),
        ),
        migrations.AlterField(
            model_name='seat',
            name='seat_type',
            field=models.CharField(blank=True, max_length=10, null=True, verbose_name='seat type'),
        ),
    ]