# Generated by Django 2.2.9 on 2020-01-13 05:56

from django.db import migrations, models
import sberbank.sberbank_settings


class Migration(migrations.Migration):

    dependencies = [
        ('sberbank', '0007_auto_20191204_1542'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='order_number',
            field=models.CharField(default=sberbank.sberbank_settings.order_number, editable=False, max_length=64, verbose_name='Номер заказа'),
        ),
    ]
