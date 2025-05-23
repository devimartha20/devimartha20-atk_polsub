# Generated by Django 4.2 on 2023-05-21 13:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('atk', '0013_alter_pengajuan_progress'),
    ]

    operations = [
        migrations.CreateModel(
            name='StokATK',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('jumlah', models.BigIntegerField()),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('atk', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='atk.barang_atk')),
                ('unit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='atk.unit')),
            ],
            options={
                'ordering': ['-updated', '-created'],
            },
        ),
        migrations.CreateModel(
            name='PenggunaanStok',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('jumlah', models.BigIntegerField()),
                ('tanggal', models.DateField()),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('atk', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='atk.barang_atk')),
                ('unit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='atk.unit')),
            ],
            options={
                'ordering': ['-updated', '-created'],
            },
        ),
        migrations.CreateModel(
            name='abc_analysis',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tahun', models.IntegerField()),
                ('harga', models.FloatField(blank=True, null=True)),
                ('dana', models.FloatField(blank=True, null=True)),
                ('presentase_dana', models.FloatField(blank=True, null=True)),
                ('presentase_kumulatif_dana', models.FloatField(blank=True, null=True)),
                ('presentase_item', models.FloatField(blank=True, null=True)),
                ('presentase_kumulatif_item', models.FloatField(blank=True, null=True)),
                ('prioritas', models.CharField(blank=True, choices=[('A', 'Tinggi'), ('B', 'Sedang'), ('C', 'Rendah')], max_length=20, null=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('atk', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='atk.barang_atk')),
                ('unit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='atk.unit')),
            ],
            options={
                'ordering': ['-updated', '-created'],
            },
        ),
        migrations.AddConstraint(
            model_name='stokatk',
            constraint=models.UniqueConstraint(fields=('atk', 'unit'), name='unique_atk_unit_stok'),
        ),
        migrations.AddConstraint(
            model_name='abc_analysis',
            constraint=models.UniqueConstraint(fields=('atk', 'unit', 'tahun'), name='unique_atk_unit_tahun_abc'),
        ),
    ]
