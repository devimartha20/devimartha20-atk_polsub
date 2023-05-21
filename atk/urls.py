from django.urls import path
from . import views
from django.http import HttpResponse


urlpatterns = [
    
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
    
    # PIMPINAN UNIT
    path('konfirpengajuan/', views.konfirPengajuan, name='konfir-pengajuan'),
    
    path('detailpengajuan/<str:pk>', views.detailPengajuan, name='detail-pengajuan'),
    
    # WADIR
    path('kelolapengajuan/', views.kelolaPengajuan, name='kelola-pengajuan'),
    path('addJadwal/', views.addJadwal, name='add-jadwal'),
    path('jadwal/edit/<str:pk>', views.editJadwal, name='edit-jadwal'),
    path('jadwal/delete/<str:pk>', views.deleteJadwal, name='delete-jadwal'),
    
    path('', views.loginUser, name='login')
]