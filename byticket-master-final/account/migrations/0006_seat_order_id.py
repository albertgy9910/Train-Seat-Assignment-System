# Generated by Django 2.0 on 2022-03-16 06:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0005_auto_20220316_1406'),
    ]

    operations = [
        migrations.AddField(
            model_name='seat',
            name='order_id',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='account.order'),
        ),
    ]
