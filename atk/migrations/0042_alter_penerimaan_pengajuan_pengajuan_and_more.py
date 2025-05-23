# Generated by Django 4.2.3 on 2023-07-14 10:44

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('atk', '0041_alter_penggunaanstok_tanggal'),
    ]

    operations = [
        migrations.AlterField(
            model_name='penerimaan_pengajuan',
            name='pengajuan',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='atk.pengajuan', unique=True),
        ),
        migrations.AlterField(
            model_name='penggunaanstok',
            name='tanggal',
            field=models.DateField(blank=True, default=datetime.datetime(2023, 7, 14, 10, 44, 37, 742554, tzinfo=datetime.timezone.utc)),
        ),
    ]
