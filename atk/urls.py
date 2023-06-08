from django.urls import path
from . import views
from django.http import HttpResponse


urlpatterns = [
    
    path('forecast/', views.forecast, name='forecast'),
    path('forecastUnit/<str:pk>', views.forecastUnit, name='forecast-unit'),
    #AUTHENTICATION
    path('login/', views.loginUser, name='login'),
    path('reset-password/', views.resetPassword, name='reset-password'),
    path('logout/', views.logoutUser, name='logout'),
    
    # DASHBOARD
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # ADMIN
    path('adduser/', views.addUser, name='add-user'),
    
    # ADMIN UNIT
    path('pengajuan/', views.pengajuan, name='pengajuan'),
    
    path('addPengajuan/', views.addPengajuan, name='add-pengajuan'),
    path('editPengajuan/<str:pk>', views.editPengajuan, name='edit-pengajuan'),
    path('deletePengajuan/<str:pk>', views.deletePengajuan, name='delete-pengajuan'),
    
    path('addIsiPengajuan/<str:pk>', views.addIsiPengajuan, name='add-isi-pengajuan'),
    path('editIsiPengajuan/<str:pk>', views.editIsiPengajuan, name='edit-isi-pengajuan'),
    path('deleteIsiPengajuan/<str:pk>', views.deleteIsiPengajuan, name='delete-isi-pengajuan'),
    
    path('ajukan/<str:pk>', views.ajukan, name='ajukan'),
    
    path('stok/', views.stok, name='stok'),
    
    path('addPenggunaanStok/', views.addPenggunaanStok, name='add-penggunaan-stok'),
    path('editPenggunaanStok/<str:pk>', views.editPenggunaanStok, name='edit-penggunaan-stok'),
    path('deletePenggunaanStok/<str:pk>', views.deletePenggunaanStok, name='delete-penggunaan-stok'),
    path('detailStokKeluar/<str:pk>', views.detailStokKeluar, name='detail-stok-keluar'),
    
    path('addPenambahanStok/', views.addPenambahanStok, name='add-penambahan-stok'),
    path('editPenambahanStok/<str:pk>', views.editPenambahanStok, name='edit-penambahan-stok'),
    path('deletePenambahanStok/<str:pk>', views.deletePenambahanStok, name='delete-penambahan-stok'),
    path('detailStokMasuk/<str:pk>', views.detailStokMasuk, name='detail-stok-masuk'),
    
    path('addguna/', views.addGuna, name='add-guna'),
    path('editguna/<str:pk>', views.editGuna, name='edit-guna'),
    path('deleteguna/<str:pk>', views.deleteGuna, name='delete-guna'),
    path('detailguna/<str:pk>', views.detailGuna, name='detail-guna'),
    
    
    # PIMPINAN UNIT
    path('tinjaupengajuan/', views.tinjauPengajuan, name='tinjau-pengajuan'),
    path('konfirpengajuan/<str:pk>', views.konfirPengajuan, name='konfir-pengajuan'),
    path('addPerbaikan/<str:pk>', views.addPerbaikan, name='add-perbaikan'),
    path('kirimPengajuan/<str:pk>', views.kirimPengajuan, name='kirim-pengajuan'),
    
    # WADIR
    path('kelolapengajuan/', views.kelolaPengajuan, name='kelola-pengajuan'),
    path('totalPengajuan/<str:pk>', views.totalPengajuan, name='total-pengajuan'),
    
    path('addJadwal/', views.addJadwal, name='add-jadwal'),
    path('jadwal/edit/<str:pk>', views.editJadwal, name='edit-jadwal'),
    path('jadwal/delete/<str:pk>', views.deleteJadwal, name='delete-jadwal'),
    
    path('', views.loginUser, name='login'),
    
    
     path('detailpengajuan/<str:pk>', views.detailPengajuan, name='detail-pengajuan'),
    # METODE
    # ABC Analysis
    path('abc/<str:scope>', views.lihat_analisis_unit, name='abc'),
    
    path('import', views.importcsv, name='import-csv'),
    
    
]