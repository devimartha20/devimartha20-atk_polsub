# Generated by Django 4.2.3 on 2023-07-19 06:36

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('atk', '0046_alter_penggunaanstok_tanggal'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='penyesuaianpengajuan',
            name='prioritas',
        ),
        migrations.RemoveField(
            model_name='penyesuaianpengajuan',
            name='rekomendasi',
        ),
        migrations.AlterField(
            model_name='penggunaanstok',
            name='tanggal',
            field=models.DateField(blank=True, default=datetime.datetime(2023, 7, 19, 6, 36, 52, 909399, tzinfo=datetime.timezone.utc)),
        ),
    ]
