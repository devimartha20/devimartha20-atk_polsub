from django.contrib import admin
from .models import *
from django_plotly_dash.models import StatelessApp, DashApp
from django.contrib.auth.models import Group

# Register your models here.
admin.site.register(User)
admin.site.register(KategoriUnit)
admin.site.register(Unit)
admin.site.register(Jadwal)
admin.site.register(KategoriATK)
admin.site.register(SatuanATK)
admin.site.register(Barang_ATK)

admin.site.register(Pengajuan)
# admin.site.register(Isi_pengajuan)
admin.site.register(StokATK)
admin.site.register(PenambahanStok)
admin.site.register(PenggunaanStok)
# admin.site.register(pengajuanABCCek)
# admin.site.register(abc_analysis_model)
# admin.site.register(abc_analysis_model_general)
admin.site.register(total_pengajuan)
# admin.site.register(PerbaikanPengajuan)
# admin.site.register(guna)

admin.site.unregister(StatelessApp)
admin.site.unregister(DashApp)
admin.site.unregister(Group)



