from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
import datetime
from django.utils import timezone

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
    for r in range(2022, (datetime.datetime.now().year+5)):
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
    
    @property
    def pengajuan(self):
        return Pengajuan.objects.filter(jadwal=self)

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
  status=models.BooleanField(default=True)
  updated = models.DateTimeField(auto_now=True)
  created= models.DateTimeField(auto_now_add=True)
    
  class Meta:
    ordering=['-updated', '-created']

  def __str__(self):
    return self.atk
class Harga(models.Model):
  harga=models.IntegerField()
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
    
  def __str__(self):
      obj = str(str(self.atk.atk)+" : Rp"+str(self.harga)+" | Periode : "+str(self.periode_mulai)+"-"+str(self.periode_selesai))
      return obj
    
class Pengajuan(models.Model):
  class ProgressPengajuan(models.TextChoices):
    DIRANCANG = "D", _("Dirancang")
    KONFIR_UNIT = "K", _("Konfirmasi Unit")
    DIAJUKAN = "A", _("Diajukan")
    PERBAIKAN = "P", _("Perbaikan")
  
  jadwal=models.ForeignKey(Jadwal, on_delete=models.CASCADE, null=True)
  unit=models.ForeignKey(Unit, on_delete=models.CASCADE)
  no_surat=models.CharField(max_length=200, null=True, blank=True)
  keterangan = models.TextField(null=True, blank=True)
  progress = models.CharField(
        max_length=20,
        choices=ProgressPengajuan.choices,
        default=ProgressPengajuan.DIRANCANG,
    )
  perbaikan = models.IntegerField(default=0)
  is_terlambat = models.BooleanField('is terlambat', default=False)
  is_aktif = models.BooleanField('is aktif', default=True)
  tanggal_konfirmasi=models.DateTimeField(null=True, blank=True)
  updated = models.DateTimeField(auto_now=True)
  created= models.DateTimeField(auto_now_add=True)
    
  class Meta:
    constraints = [
        models.UniqueConstraint(fields=['unit', 'jadwal'], name='unique_unit_jadwal'),
    ]
    ordering=['-updated', '-created']
    
# class hasil_prediksi_unit(models.Model):
#   class metode(models.TextChoices):
#         EXPONENTIAL_SMOOTHING = "ES", _("EXPONENTIAL_SMOOTHING")
#         NAIVE = "N", _("NAIVE")
#         ARIMA = "A", _("ARIMA")
#   atk=models.ForeignKey(Barang_ATK, on_delete=models.CASCADE)
#   periode=models.IntegerField()
#   unit=models.ForeignKey(Unit, on_delete=models.SET_NULL, null=True)
#   metode=models.CharField(
#         max_length=50,
#         choices=metode.choices,
#   )
#   pred=models.FloatField()
#   smap=models.FloatField()
#   updated = models.DateTimeField(auto_now=True)
#   created= models.DateTimeField(auto_now_add=True)
  
#   class Meta:
#     constraints = [
#         models.UniqueConstraint(fields=['atk','periode', 'unit'], name='unique_atk_periode_unit_prediksi'),
#     ]
#     ordering=['-updated', '-created']
    
# class hasil_prediksi_general(models.Model):
#   class metode(models.TextChoices):
#         EXPONENTIAL_SMOOTHING = "ES", _("EXPONENTIAL_SMOOTHING")
#         NAIVE = "N", _("NAIVE")
#         ARIMA = "A", _("ARIMA")
#   atk=models.ForeignKey(Barang_ATK, on_delete=models.CASCADE)
#   periode=models.IntegerField()
#   metode=models.CharField(
#         max_length=50,
#         choices=metode.choices,
#   )
#   pred=models.FloatField()
#   smap=models.FloatField()
#   updated = models.DateTimeField(auto_now=True)
#   created= models.DateTimeField(auto_now_add=True)
  
#   class Meta:
#     constraints = [
#         models.UniqueConstraint(fields=['atk','periode'], name='unique_atk_periode_prediksi'),
#     ]
#     ordering=['-updated', '-created']

class total_pengajuan(models.Model):
  jadwal = models.ForeignKey(Jadwal, on_delete=models.CASCADE)
  atk=models.ForeignKey(Barang_ATK, on_delete=models.SET_NULL, null=True)
  jumlah=models.IntegerField()
  rekomendasi=models.IntegerField(null=True, blank=True)
  # rekomendasi=models.ForeignKey(hasil_prediksi_general, on_delete=models.SET_NULL, null=True)
  harga=models.ForeignKey(Harga, on_delete=models.SET_NULL, null=True)
  total_dana=models.IntegerField()
  updated = models.DateTimeField(auto_now=True)
  created= models.DateTimeField(auto_now_add=True)
  
  class Meta:
    constraints = [
        models.UniqueConstraint(fields=['atk','jadwal'], name='unique_atk_jadwal'),
    ]
    ordering=['-updated', '-created']
    


class Isi_pengajuan(models.Model):
  pengajuan=models.ForeignKey(Pengajuan, on_delete=models.CASCADE)
  atk=models.ForeignKey(Barang_ATK, on_delete=models.SET_NULL, null=True)
  jumlah=models.IntegerField()
  rekomendasi=models.FloatField(null=True)
  # rekomendasi=models.ForeignKey(hasil_prediksi_unit, on_delete=models.SET_NULL, null=True)
  keterangan=models.TextField(max_length=200)
  updated = models.DateTimeField(auto_now=True)
  created= models.DateTimeField(auto_now_add=True)
    
  class Meta:
    constraints = [
        models.UniqueConstraint(fields=['atk','pengajuan'], name='unique_atk_pengajuan'),
    ]
    ordering=['-updated', '-created']

class PerbaikanPengajuan(models.Model):
  pengajuan=models.ForeignKey(Pengajuan, on_delete=models.CASCADE)
  keterangan=models.TextField(max_length=1000)
  updated = models.DateTimeField(auto_now=True)
  created= models.DateTimeField(auto_now_add=True)
  
  class Meta:
     ordering=['-updated', '-created']
     
     
class guna(models.Model):
  kegunaan = models.CharField(max_length=200, unique=True)
  keterangan=models.TextField(max_length=1000, null=True, blank=True)
  unit=models.ForeignKey(Unit, on_delete=models.CASCADE)
  updated = models.DateTimeField(auto_now=True)
  created= models.DateTimeField(auto_now_add=True)
  
  class Meta:
     ordering=['-updated', '-created']
     
  def __str__(self):
    return self.kegunaan
    
class StokATK(models.Model):
  atk=models.ForeignKey(Barang_ATK, on_delete=models.SET_NULL, null=True)
  jumlah=models.IntegerField()
  jml_masuk=models.IntegerField(null=True, blank=True, default=0)
  jml_keluar=models.IntegerField(null=True, blank=True, default=0)
  unit=models.ForeignKey(Unit, on_delete=models.CASCADE)
  updated = models.DateTimeField(auto_now=True)
  created= models.DateTimeField(auto_now_add=True)

  class Meta:
    constraints = [
        models.UniqueConstraint(fields=['atk','unit'], name='unique_atk_unit_stok'),
    ]
    ordering=['-updated', '-created']
    
  def __str__(self):
    return self.atk.atk
    
class PenggunaanStok(models.Model):
  class Penerima(models.TextChoices):
    MAHASISWA = 'M', _("Mahasiswa")
    DOSEN = 'D', _("Dosen")
    STAFF = 'S', _("Staff")
    LAINNYA = 'L', _("Lainnya")
  
  atk=models.ForeignKey(StokATK, on_delete=models.SET_NULL, null=True)
  jumlah=models.IntegerField()
  unit=models.ForeignKey(Unit, on_delete=models.CASCADE)
  penerima = models.CharField(
        max_length=20,
        choices=Penerima.choices,
        default=Penerima.MAHASISWA
    )
  guna=models.ForeignKey(guna, on_delete=models.SET_NULL, null=True)
  keterangan=models.CharField(max_length=200, null=True, blank=True)
  tanggal=models.DateField(default=timezone.now(), blank=True)
  updated = models.DateTimeField(auto_now=True)
  created= models.DateTimeField(auto_now_add=True)
  
  class Meta:
    ordering=['-tanggal', '-updated', '-created']
    
class PenambahanStok(models.Model):
  atk=models.ForeignKey(Barang_ATK, on_delete=models.SET_NULL, null=True)
  jumlah=models.IntegerField()
  tanggal=models.DateField()
  unit=models.ForeignKey(Unit, on_delete=models.CASCADE)
  keterangan=models.CharField(max_length=200, null=True, blank=True)
  updated = models.DateTimeField(auto_now=True)
  created= models.DateTimeField(auto_now_add=True)
  
  class Meta:
    ordering=['-tanggal', '-updated', '-created']
    
class abc_analysis_model(models.Model):
  class Prioritas(models.TextChoices):
      TINGGI = "A", _("Tinggi")  
      SEDANG = "B", _("Sedang")
      RENDAH = "C", _("Rendah")
  
  atk=models.ForeignKey(Barang_ATK, on_delete=models.SET_NULL, null=True)
  unit=models.ForeignKey(Unit, on_delete=models.CASCADE)
  tahun=models.IntegerField()
  jumlah=models.IntegerField(null=True, blank=True)
  harga=models.IntegerField(null=True, blank=True)
  dana=models.IntegerField(null=True, blank=True)
  persentase_item=models.FloatField(null=True, blank=True)
  persentase_kumulatif_item=models.FloatField(null=True, blank=True)
  persentase_dana=models.FloatField(null=True, blank=True)
  persentase_kumulatif_dana=models.FloatField(null=True, blank=True)
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
  
class abc_analysis_model_more(models.Model):
  pass

class abc_analysis_model_general(models.Model):
  class Prioritas(models.TextChoices):
      TINGGI = "A", _("Tinggi")  
      SEDANG = "B", _("Sedang")
      RENDAH = "C", _("Rendah")
  
  atk=models.ForeignKey(Barang_ATK, on_delete=models.SET_NULL, null=True)
  tahun=models.IntegerField()
  jumlah=models.IntegerField(null=True, blank=True)
  harga=models.IntegerField(null=True, blank=True)
  dana=models.IntegerField(null=True, blank=True)
  persentase_item=models.FloatField(null=True, blank=True)
  persentase_kumulatif_item=models.FloatField(null=True, blank=True)
  persentase_dana=models.FloatField(null=True, blank=True)
  persentase_kumulatif_dana=models.FloatField(null=True, blank=True)
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
        models.UniqueConstraint(fields=['atk', 'tahun'], name='unique_atk_tahun_abc'),
    ]
    ordering=['-updated', '-created']
    
  def __str__(self):
    return self.prioritas
    



class pengajuanABCCek(models.Model):
  
  class Prioritas(models.TextChoices):
      TINGGI = "A", _("Tinggi")  
      SEDANG = "B", _("Sedang")
      RENDAH = "C", _("Rendah")
      
  atk=models.CharField(max_length=50)
  jumlah=models.IntegerField()
  harga=models.IntegerField()
  total_harga=models.IntegerField()
  dana=models.IntegerField(null=True, blank=True)
  persentase_item=models.FloatField(null=True, blank=True)
  persentase_kumulatif_item=models.FloatField(null=True, blank=True)
  persentase_dana=models.FloatField(null=True, blank=True)
  persentase_kumulatif_dana=models.FloatField(null=True, blank=True)
  prioritas = models.CharField(
        max_length=20,
        choices=Prioritas.choices,
        null=True,
        blank=True
    )
  updated = models.DateTimeField(auto_now=True)
  created= models.DateTimeField(auto_now_add=True)
  
  class Meta:
    ordering=['-updated', '-created']