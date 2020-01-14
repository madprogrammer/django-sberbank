# Generated by Django 2.2.8 on 2019-12-04 05:42

from django.db import migrations, models
import jsonfield.encoder
import jsonfield.fields
import sberbank.models


class Migration(migrations.Migration):

    dependencies = [
        ('sberbank', '0006_payment_method'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='payment',
            options={'ordering': ['-updated'], 'verbose_name': 'payment', 'verbose_name_plural': 'payments'},
        ),
        migrations.AlterField(
            model_name='logentry',
            name='action',
            field=models.CharField(db_index=True, max_length=100, verbose_name='action'),
        ),
        migrations.AlterField(
            model_name='logentry',
            name='bank_id',
            field=models.UUIDField(blank=True, db_index=True, null=True, verbose_name='bank payment ID'),
        ),
        migrations.AlterField(
            model_name='logentry',
            name='created',
            field=models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='created'),
        ),
        migrations.AlterField(
            model_name='logentry',
            name='payment_id',
            field=models.UUIDField(blank=True, db_index=True, null=True, verbose_name='payment ID'),
        ),
        migrations.AlterField(
            model_name='logentry',
            name='request_text',
            field=models.TextField(blank=True, null=True, verbose_name='request text'),
        ),
        migrations.AlterField(
            model_name='logentry',
            name='response_text',
            field=models.TextField(blank=True, null=True, verbose_name='response text'),
        ),
        migrations.AlterField(
            model_name='payment',
            name='amount',
            field=models.DecimalField(decimal_places=2, max_digits=128, verbose_name='amount'),
        ),
        migrations.AlterField(
            model_name='payment',
            name='bank_id',
            field=models.UUIDField(blank=True, db_index=True, null=True, verbose_name='bank ID'),
        ),
        migrations.AlterField(
            model_name='payment',
            name='client_id',
            field=models.TextField(blank=True, null=True, verbose_name='client ID'),
        ),
        migrations.AlterField(
            model_name='payment',
            name='created',
            field=models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='created'),
        ),
        migrations.AlterField(
            model_name='payment',
            name='details',
            field=jsonfield.fields.JSONField(blank=True, dump_kwargs={'cls': jsonfield.encoder.JSONEncoder, 'separators': (',', ':')}, load_kwargs={}, null=True, verbose_name='details'),
        ),
        migrations.AlterField(
            model_name='payment',
            name='error_code',
            field=models.PositiveIntegerField(blank=True, null=True, verbose_name='error code'),
        ),
        migrations.AlterField(
            model_name='payment',
            name='error_message',
            field=models.TextField(blank=True, null=True, verbose_name='error message'),
        ),
        migrations.AlterField(
            model_name='payment',
            name='status',
            field=models.PositiveSmallIntegerField(choices=[(0, 'CREATED'), (1, 'PENDING'), (2, 'SUCCEEDED'), (3, 'FAILED'), (4, 'REFUNDED')], db_index=True, default=sberbank.models.Status(0), verbose_name='status'),
        ),
        migrations.AlterField(
            model_name='payment',
            name='updated',
            field=models.DateTimeField(auto_now=True, db_index=True, verbose_name='modified'),
        ),
    ]
