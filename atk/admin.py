from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(User)
admin.site.register(KategoriUnit)
admin.site.register(Unit)
admin.site.register(Jadwal)
admin.site.register(KategoriATK)
admin.site.register(SatuanATK)
admin.site.register(Barang_ATK)
admin.site.register(Harga)
admin.site.register(Pengajuan)
admin.site.register(Isi_pengajuan)