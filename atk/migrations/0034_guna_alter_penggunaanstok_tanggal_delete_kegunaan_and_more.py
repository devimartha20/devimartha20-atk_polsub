# Generated by Django 4.2 on 2023-06-05 09:10

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('atk', '0033_remove_isi_pengajuan_rekomendasi_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='guna',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('kegunaan', models.CharField(max_length=200)),
                ('keterangan', models.TextField(blank=True, max_length=1000, null=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('unit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='atk.unit')),
            ],
            options={
                'ordering': ['-updated', '-created'],
            },
        ),
        migrations.AlterField(
            model_name='penggunaanstok',
            name='tanggal',
            field=models.DateField(blank=True, default=datetime.datetime(2023, 6, 5, 9, 9, 57, 701594, tzinfo=datetime.timezone.utc)),
        ),
        migrations.DeleteModel(
            name='Kegunaan',
        ),
        migrations.AddField(
            model_name='penggunaanstok',
            name='guna',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='atk.guna'),
        ),
    ]
