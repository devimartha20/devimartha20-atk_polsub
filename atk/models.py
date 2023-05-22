from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
import datetime
# Create your models here.

class KategoriUnit(models.Model):
    KategoriUnit= models.CharField(max_length=200)
    updated = models.DateTimeField(auto_now=True)
    created= models.DateTimeField(auto_now_add=True)
    
    class Meta:
      ordering=['-updated', '-created']

    def __str__(self):
      return self.KategoriUnit
    
class Unit(models.Model): 
    unit= models.CharField(max_length=200)
    kategori= models.ForeignKey(KategoriUnit, on_delete=models.SET_NULL, null=True, blank=True)
    updated = models.DateTimeField(auto_now=True)
    created= models.DateTimeField(auto_now_add=True)
    
    class Meta:
      ordering=['-updated', '-created']

    def __str__(self):
      return self.unit
class User(AbstractUser):
    is_admin= models.BooleanField('is admin', default=False)
    is_wadir= models.BooleanField('is wadir', default=False)
    is_pimpinanunit= models.BooleanField('is pimpinan_unit', default=False)
    is_adminunit= models.BooleanField('is adminunit', default=False)
    unit=models.ForeignKey(Unit, on_delete=models.SET_NULL, null=True, blank=True)
    
class Jadwal(models.Model):
    class StatusJadwal(models.TextChoices):
        DIBUKA = "B", _("Dibuka")
        DITUTUP = "T", _("Ditutup")
  
    YEAR_CHOICES = []
    for r in range(2023, (datetime.datetime.now().year+5)):
        YEAR_CHOICES.append((r,r))

    tahun = models.IntegerField(('year'), choices=YEAR_CHOICES, default=datetime.datetime.now().year)
    pengajuan_mulai=models.DateField(unique=True)
    pengajuan_selesai=models.DateField(unique=True)
    status = models.CharField(
        max_length=10,
        choices=StatusJadwal.choices,
        default=StatusJadwal.DIBUKA,
    )
    keterangan=models.TextField(max_length=200, null=True, blank=True)
    updated = models.DateTimeField(auto_now=True)
    created= models.DateTimeField(auto_now_add=True)
    
    class Meta:
      ordering=['-updated', '-created']
      
class pengumpulanPengajuan(models.Model):
  
    class statusPengumpulan(models.TextChoices):
      SELESAI = "S", _("Selesai diajukan")
      BELUM = "B", _("Tidak/belum diajukan")
  
    jadwal=models.ForeignKey(Jadwal, on_delete=models.CASCADE, null=True)
    unit=models.ForeignKey(Unit, on_delete=models.CASCADE, null=True, blank=True)
    status=models.CharField(
      max_length=10,
      choices=statusPengumpulan.choices,
      default=statusPengumpulan.BELUM
    )
    tanggalPengumpulan=models.DateField()
    updated = models.DateTimeField(auto_now=True)
    created= models.DateTimeField(auto_now_add=True)
    
    class Meta:
      ordering=['-updated', '-created']
      
class KategoriATK(models.Model):
  KategoriATK=models.CharField(max_length=200)
  updated = models.DateTimeField(auto_now=True)
  created= models.DateTimeField(auto_now_add=True)
    
  class Meta:
    ordering=['-updated', '-created']

  def __str__(self):
    return self.KategoriATK

class SatuanATK(models.Model):
  satuan=models.CharField(max_length=200)
  updated = models.DateTimeField(auto_now=True)
  created= models.DateTimeField(auto_now_add=True)
    
  class Meta:
    ordering=['-updated', '-created']

  def __str__(self):
    return self.satuan

class Barang_ATK(models.Model):
  atk=models.CharField(max_length=200, unique=True)
  keterangan = models.TextField(null=True, blank=True)
  kategori=models.ForeignKey(KategoriATK, on_delete=models.SET_NULL, null=True)
  satuan=models.ForeignKey(SatuanATK, on_delete=models.SET_NULL, null=True)
  jumlah_per_satuan=models.IntegerField(default=1)
  updated = models.DateTimeField(auto_now=True)
  created= models.DateTimeField(auto_now_add=True)
    
  class Meta:
    ordering=['-updated', '-created']

  def __str__(self):
    return self.atk
class Harga(models.Model):
  harga=models.DecimalField(max_digits=6, decimal_places=5, default=0)
  atk=models.ForeignKey(Barang_ATK, on_delete=models.SET_NULL, null=True, blank=True)
  periode_mulai=models.DateField()
  periode_selesai=models.DateField(null=True, blank=True)
  updated = models.DateTimeField(auto_now=True)
  created= models.DateTimeField(auto_now_add=True)

  class Meta:
    constraints = [
        models.UniqueConstraint(fields=['atk','periode_mulai', 'periode_selesai'], name='unique_periode_harga'),
    ]
    ordering=['-updated', '-created']
    
class Pengajuan(models.Model):
  class ProgressPengajuan(models.TextChoices):
    DIRANCANG = "D", _("Dirancang")
    KONFIR_UNIT = "K", _("Konfirmasi Unit")
    DIAJUKAN = "A", _("Diajukan")
    PERBAIKAN = "P", _("Perbaikan")
    SELESAI = "S", _("Selesai") 
    
  class HasilPengajuan(models.TextChoices):
    DITERIMA = "Y", _("Diterima")
    DITOLAK = "N", _("Ditolak")
  
  jadwal=models.ForeignKey(Jadwal, on_delete=models.CASCADE, null=True)
  unit=models.ForeignKey(Unit, on_delete=models.CASCADE)
  no_surat=models.CharField(max_length=200, null=True, blank=True)
  keterangan = models.TextField(null=True, blank=True)
  progress = models.CharField(
        max_length=20,
        choices=ProgressPengajuan.choices,
        default=ProgressPengajuan.DIRANCANG,
    )
  hasil = models.CharField(
        max_length=20,
        choices=HasilPengajuan.choices,
        null=True,
        blank=True
    )
  perbaikan = models.IntegerField(default=0)
  is_terlambat = models.BooleanField('is terlambat', default=False)
  is_aktif = models.BooleanField('is aktif', default=True)
  updated = models.DateTimeField(auto_now=True)
  created= models.DateTimeField(auto_now_add=True)
    
  class Meta:
    constraints = [
        models.UniqueConstraint(fields=['unit', 'jadwal'], name='unique_unit_jadwal'),
    ]
    ordering=['-updated', '-created']

class Isi_pengajuan(models.Model):
  pengajuan=models.ForeignKey(Pengajuan, on_delete=models.CASCADE)
  atk=models.ForeignKey(Barang_ATK, on_delete=models.SET_NULL, null=True)
  jumlah=models.BigIntegerField()
  rekomendasi=models.BigIntegerField(null=True, blank=True)
  keterangan=models.TextField(max_length=200)
  perbaikan=models.TextField(max_length=200, null=True, blank=True)
  updated = models.DateTimeField(auto_now=True)
  created= models.DateTimeField(auto_now_add=True)
    
  class Meta:
    constraints = [
        models.UniqueConstraint(fields=['atk','pengajuan'], name='unique_atk_pengajuan'),
    ]
    ordering=['-updated', '-created']
    
class StokATK(models.Model):
  atk=models.ForeignKey(Barang_ATK, on_delete=models.SET_NULL, null=True)
  jumlah=models.BigIntegerField()
  unit=models.ForeignKey(Unit, on_delete=models.CASCADE)
  updated = models.DateTimeField(auto_now=True)
  created= models.DateTimeField(auto_now_add=True)

  class Meta:
    constraints = [
        models.UniqueConstraint(fields=['atk','unit'], name='unique_atk_unit_stok'),
    ]
    ordering=['-updated', '-created']
    
class PenggunaanStok(models.Model):
  atk=models.ForeignKey(Barang_ATK, on_delete=models.SET_NULL, null=True)
  jumlah=models.BigIntegerField()
  unit=models.ForeignKey(Unit, on_delete=models.CASCADE)
  tanggal=models.DateField()
  updated = models.DateTimeField(auto_now=True)
  created= models.DateTimeField(auto_now_add=True)
  
  class Meta:
    ordering=['-updated', '-created']
    
# class PengambahanStok(models.Model):
#   pass
    
class abc_analysis(models.Model):
  class Prioritas(models.TextChoices):
      TINGGI = "A", _("Tinggi")  
      SEDANG = "B", _("Sedang")
      RENDAH = "C", _("Rendah")
  
  atk=models.ForeignKey(Barang_ATK, on_delete=models.SET_NULL, null=True)
  unit=models.ForeignKey(Unit, on_delete=models.CASCADE)
  tahun=models.IntegerField()
  harga=models.FloatField(null=True, blank=True)
  dana=models.FloatField(null=True, blank=True)
  presentase_dana=models.FloatField(null=True, blank=True)
  presentase_kumulatif_dana=models.FloatField(null=True, blank=True)
  presentase_item=models.FloatField(null=True, blank=True)
  presentase_kumulatif_item=models.FloatField(null=True, blank=True)
  prioritas = models.CharField(
        max_length=20,
        choices=Prioritas.choices,
        null=True,
        blank=True
    )
  updated = models.DateTimeField(auto_now=True)
  created= models.DateTimeField(auto_now_add=True)
  
  class Meta:
    constraints = [
        models.UniqueConstraint(fields=['atk','unit', 'tahun'], name='unique_atk_unit_tahun_abc'),
    ]
    ordering=['-updated', '-created']
    
  def __str__(self):
    return self.prioritas
  
# class metode_prediksi(models.Model):
#   metode=models.CharField(max_length=200, unique=True)
  