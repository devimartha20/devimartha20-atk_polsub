from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control
from django.core.management import BaseCommand
import csv
from decimal import *

from django.contrib import messages
from .forms import *
from .models import *
import datetime

from abc_analysis import abc_analysis
import pandas as pd
import numpy as np
from darts import TimeSeries

# Create your views here.

# AUTHENTICATION
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def loginUser(request):
    
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    form = loginForm(request.POST or None)
    msg = None
    if request.method == 'POST':
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')
            else:
                msg= 'Kredensial tidak valid'
        else:
            msg = 'Validasi formulir error'
    context = {'form': form, 'msg': msg}
    return render(request, 'atk/login.html', context)

def resetPassword(request):
    return HttpResponse('reset password')

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='login')
def logoutUser(request):
    logout(request)
    return redirect('login')

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='login')
def dashboard(request):
    if request.user.is_admin:
        context = {}
        return render(request, 'atk/admin/dashboard.html', context)
    elif request.user.is_adminunit:
        context = {}
        return render(request, 'atk/adminunit/dashboard.html', context)
    elif request.user.is_wadir:
        context = {}
        return render(request, 'atk/wadir/dashboard.html', context)
    elif request.user.is_pimpinanunit:
        context = {}
        return render(request, 'atk/admin/dashboard.html', context)
    else:
        return HttpResponse('Kredensial tidak valid')

@login_required(login_url='login')
def addUser(request):
    if request.user.is_admin == False:
        return HttpResponse('Kredensial tidak valid')
            
    msg = None
    if request.method == 'POST':
        form = addUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            msg = 'Pengguna berhasil ditambahkan!'
            return redirect('add-user')
        else:
            msg = 'form is not valid'
    else:
        form = addUserForm()
    context = {'form': form,'msg': msg}
    return render(request,'atk/add_user.html', context)

#WADIR
@login_required(login_url='login')
def kelolaPengajuan(request):
    if request.user.is_wadir:
        unit = Unit.objects.all()
        
        jadwalSekarang = Jadwal.objects.filter(
            tahun = datetime.datetime.now().year
        ).first()
        
        addjadwalForm = formJadwal()
        editjadwalForm = formJadwal(instance=jadwalSekarang)
        
        context = {'jadwalForm': addjadwalForm, 'editjadwalForm': editjadwalForm,'unit': unit, 'jadwalSekarang':jadwalSekarang}
        return render(request, 'atk/wadir/pengajuan.html', context)
    else:
        raise Http404
    
@login_required(login_url='login')
def addJadwal(request):
    if request.user.is_wadir:
        jadwalForm = formJadwal(request.POST)
        if jadwalForm.is_valid():
            jadwal = jadwalForm.save()
            periode = jadwal.tahun
            messages.success(request, f'Jadwal Pengajuan Periode {periode} Berhasil Dibuat!')
            return redirect('kelola-pengajuan')
        else:
            messages.error(request, f'Terjadi Kesalahan')
            return redirect('kelola-pengajuan')
    else:
        raise Http404

    
@login_required(login_url='login')
def editJadwal(request, pk):
    if request.user.is_wadir:
        id = int(pk)
        instance = Jadwal.objects.get(id=id)
        jadwalForm = formJadwal(request.POST or None, instance=instance)
        if jadwalForm.is_valid():
            jadwalForm = jadwalForm.save()
            messages.success(request, f'Jadwal Pengajuan Berhasil Diubah!')
            return redirect('kelola-pengajuan')
        else:
            messages.error(request, f'Terjadi Kesalahan')
            return redirect('kelola-pengajuan')
    else:
        raise Http404
    
@login_required(login_url='login')
def deleteJadwal(request, pk):
    if request.user.is_wadir:
        return HttpResponse('delete jadwal')
    else:
        raise Http404
    
# ADMIN UNIT
@login_required(login_url='login')
def pengajuan(request):
    if request.user.is_adminunit:
        
        today = datetime.date.today()
        tahun = today.year
        jadwal = Jadwal.objects.filter(tahun=tahun)[:1].first()
        
        pengajuan = Pengajuan.objects.filter(
            unit= request.user.unit,
            jadwal=jadwal
        ).first()
        
        riwayat = Pengajuan.objects.filter(
            unit=request.user.unit
        )
        
        status = None
        context = {'jadwal': jadwal, 'status':status, 'pengajuan': pengajuan, 'riwayat': riwayat}
        return render(request, 'atk/adminunit/pengajuan/pengajuan.html', context)
    else:
        raise Http404

@login_required(login_url='login')
def addPengajuan(request):
    if request.user.is_adminunit:
        
        today = datetime.date.today()
        tahun = today.year
        jadwal = Jadwal.objects.filter(tahun=tahun)[:1].first()
        
        pengajuan = Pengajuan.objects.filter(
            unit= request.user.unit,
            jadwal=jadwal
        ).first()
        
        if request.method == 'POST':
            pengajuan = Pengajuan.objects.create(
                jadwal=jadwal,
                unit=request.user.unit,
                no_surat=request.POST.get('no_surat'),
                keterangan=request.POST.get('keterangan')
            )  
            messages.success(request, 'Pengajuan berhasil dibuat!')
            return redirect('add-pengajuan')

        isiPengajuan = Isi_pengajuan.objects.filter(
            pengajuan= pengajuan
        )   
        isiPengajuanForm = formIsiPengajuan()
            
        atk = Barang_ATK.objects.all()
        
        context = {'isiPengajuanForm': isiPengajuanForm,
                   'pengajuan': pengajuan,
                   'isi_pengajuan': isiPengajuan,
                   'atk': atk
                   }
        return render(request, 'atk/adminunit/pengajuan/addPengajuan.html', context)
    else:
        raise Http404

login_required(login_url='login')  
def editPengajuan(request, pk):
    if request.user.is_adminunit:
        id = int(pk)
        pengajuan = Pengajuan.objects.filter(id=id)
        if pengajuan is not None:
            pengajuan = pengajuan.update(
                no_surat = request.POST.get('no_surat'),
                keterangan = request.POST.get('keterangan')
            )
            messages.success(request, "Pengajuan berhasil diubah!")
            return redirect('add-pengajuan')
        else:
            messages.error(request, 'Terjadi kesalahan!')
    else:
        raise Http404

login_required(login_url='login')  
def deletePengajuan(request, pk):
    if request.user.is_adminunit:
        id = int(pk)
        pengajuan = Pengajuan.objects.filter(id=id)
        if pengajuan is not None:
            pengajuan = pengajuan.delete()
            messages.success(request, "Pengajuan berhasil dihapus!")
            return redirect('add-pengajuan')
        else:
            messages.error(request, 'Terjadi kesalahan!')
    else:
        raise Http404
    
login_required(login_url='login')
def addIsiPengajuan(request, pk):
    if request.user.is_adminunit:
        isiPengajuanForm = formIsiPengajuan(request.POST)
        if isiPengajuanForm.is_valid():
            id = int(pk)
            pengajuan = Pengajuan.objects.get(id=id)
            isiPengajuan = isiPengajuanForm.save(commit=False)
            isiPengajuan.pengajuan = pengajuan
            save = isiPengajuan.save()
            messages.success(request, "Data berhasil ditambahkan!")
            return redirect('add-pengajuan')
        else:
            messages.error(request, 'Terjadi kesalahan!')
            return redirect('add-pengajuan')
    else:
        raise Http404

login_required(login_url='login')
def editIsiPengajuan(request, pk):
    if request.user.is_adminunit:
        id = int(pk)
        isi_pengajuan = Isi_pengajuan.objects.filter(id=id).first()
        
        if isi_pengajuan is not None:
            isi_pengajuan.update(
                atk=request.POST.get('atk'),
                jumlah=request.POST.get('jumlah'),
                keterangan=request.POST.get('keterangan')
            )
            messages.success(request, f'Data berhasil diubah!')
            return redirect('add-pengajuan')
        else:
            messages.error(request, 'Terjadi kesalahan!')
    else:
        raise Http404

login_required(login_url='login')
def deleteIsiPengajuan(request, pk):
    if request.user.is_adminunit:
        id = int(pk)
        isi_pengajuan = Isi_pengajuan.objects.filter(id=id).first()
        
        if isi_pengajuan is not None:
            atk = isi_pengajuan.atk
            jumlah = isi_pengajuan.jumlah
            
            isi_pengajuan.delete()
            messages.success(request, f'Pengajuan {atk} sejumlah {jumlah} berhasil dihapus!')
            return redirect('add-pengajuan')
        else:
            messages.error(request, 'Terjadi kesalahan!')
    else:
        raise Http404

@login_required(login_url='login')
def ajukan(request, pk):
    if request.user.is_adminunit:
        id = int(pk)
        pengajuan = Pengajuan.objects.filter(id=id).update(progress='K')
        return redirect('add-pengajuan')
    else:
        raise Http404
    
#stok
@login_required(login_url='login')
def stok(request):
    if request.user.is_adminunit:
        stok = StokATK.objects.filter(
            unit = request.user.unit
        )
        stokMasuk = PenambahanStok.objects.filter(unit=request.user.unit)
        stokKeluar = PenggunaanStok.objects.filter(unit=request.user.unit)
        stokKeluarForm = formStokKeluar()
        stokMasukForm = formStokMasuk()
        context = {'stok': stok, 'stokMasuk': stokMasuk, 'stokKeluar': stokKeluar,'stokKeluarForm': stokKeluarForm, 'stokMasukForm': stokMasukForm}
        return render(request, 'atk/adminunit/stok/stok.html', context)
    else:
        raise Http404

@login_required(login_url='login')
def addPenggunaanStok(request):
    if request.user.is_adminunit:
        stokKeluarForm = formStokKeluar(request.POST)
        if stokKeluarForm.is_valid():
            
            atk=stokKeluarForm.data.get('atk')
            jumlah=stokKeluarForm.cleaned_data.get('jumlah')
            
            stok = StokATK.objects.filter(id=atk).first()
            print(atk, request.user.unit)
            stok.jumlah = stok.jumlah-jumlah
            stok.save(update_fields=['jumlah'])
            
            stokKeluar = stokKeluarForm.save(commit=False)
            stokKeluar.unit = request.user.unit
            stokKeluar.save()
            messages.success(request, "Data berhasil ditambahkan!")
            return redirect('stok')
        else:
            messages.error(request, 'Terjadi kesalahan!')
            return redirect('stok')
    else:
        raise Http404
    
@login_required(login_url='login')
def editPenggunaanStok(request, pk):
    if request.user.is_adminunit:
        id = int(pk)
        stok = PenggunaanStok.objects.get(id=id)
        stokKeluarForm = formStokKeluar(request.POST, instance=stok)
        if stokKeluarForm.is_valid():
            stokKeluarForm.save()
            messages.success(request, "Data berhasil diubah!")
            return redirect('stok')
        else:
            messages.error(request, 'Terjadi kesalahan!')
            return redirect('stok')
    else:
        raise Http404
    
@login_required(login_url='login')
def deletePenggunaanStok(request, pk):
    if request.user.is_adminunit:
        id = int(pk)
        stok = PenggunaanStok.objects.filter(id=id).first()
        if stok is not None:
            stok.delete()
            messages.success(request, "Data berhasil dihapus!")
            return redirect('stok')
        else:
            messages.error(request, 'Terjadi kesalahan!')
            return redirect('stok')
    else:
        raise Http404
    
@login_required(login_url='login')
def addPenambahanStok(request):
    if request.user.is_adminunit:
        stokMasukForm = formStokMasuk(request.POST)
        if stokMasukForm.is_valid():
            
            atk=stokMasukForm.cleaned_data.get('atk')
            jumlah=stokMasukForm.cleaned_data.get('jumlah')
            
            stok = StokATK.objects.filter(unit=request.user.unit, atk=atk).first()
            
            if stok is None:
                stok = StokATK.objects.create(
                    atk=atk,
                    jumlah=jumlah,
                    unit=request.user.unit
                )
            else:
                stok.jumlah = stok.jumlah + jumlah
                stok.save(
                    update_fields=['jumlah']
                )
            
            tambahStok = stokMasukForm.save(commit=False)
            tambahStok.unit = request.user.unit
            tambahStok.save()
            messages.success(request, "Data berhasil ditambahkan!")
            return redirect('stok')
        else:
            messages.error(request, 'Terjadi kesalahan!')
            return redirect('stok')
    else:
        raise Http404
    
@login_required(login_url='login')
def editPenambahanStok(request, pk):
    if request.user.is_adminunit:
        id = int(pk)
        stok = PenambahanStok.objects.get(id=id)
        stokMasukForm = formStokMasuk(request.POST, instance=stok)
        if stokMasukForm.is_valid():
            stokMasukForm.save()
            messages.success(request, "Data berhasil diubah!")
            return redirect('stok')
        else:
            messages.error(request, 'Terjadi kesalahan!')
            return redirect('stok')
    else:
        raise Http404
    
@login_required(login_url='login')
def deletePenambahanStok(request, pk):
    if request.user.is_adminunit:
        id = int(pk)
        stok = PenambahanStok.objects.filter(id=id).first()
        if stok is not None:
            stok.delete()
            messages.success(request, "Data berhasil dihapus!")
            return redirect('stok')
        else:
            messages.error(request, 'Terjadi kesalahan!')
            return redirect('stok')
    else:
        raise Http404

#PIMPINAN UNIT
@login_required(login_url='login')
def konfirPengajuan(request):
    if request.user.is_pimpinanunit:
        
        today = datetime.date.today()
        tahun = today.year
        jadwal = Jadwal.objects.filter(tahun=tahun)[:1].first()
        
        pengajuan = Pengajuan.objects.filter(
            unit= request.user.unit,
            jadwal=jadwal
        ).first()
        
        riwayat_pengajuan = Pengajuan.objects.filter(
            unit = request.user.unit,
            is_aktif = False
        )
    
        context = {'jadwal': jadwal, 'pengajuan': pengajuan, 'riwayat_pengajuan':riwayat_pengajuan}
        return render(request, 'atk/pimpinanunit/pengajuan.html', context)
    else:
        raise Http404
    
@login_required(login_url='login')
def detailPengajuan(request, pk):
    if request.user.is_pimpinanunit or request.user.is_adminunit:
        id = int(pk)
        
        pengajuan = Pengajuan.objects.filter(id=id).first()
        
        isi_pengajuan = Isi_pengajuan.objects.filter(
            pengajuan = pengajuan
        )
        
        context = {'pengajuan': pengajuan, 'isi_pengajuan': isi_pengajuan}
        return render(request, 'atk/detailpengajuan.html', context)
    else:
        raise Http404
    
# METODE
# ABC analisis
@login_required(login_url='login')
def atk_abc_analysis(request):  
    
    
    context = {}
    return render(request, 'atk/adminunit/metode/abc_analysis.html', context)
    
    cek = pengajuanABCCek.objects.all().order_by('id')
    list_total_harga = []
    print(cek.count())
    for cek in cek:
        list_total_harga.append(cek.total_harga)
    print(list_total_harga)
    abc = abc_analysis(list_total_harga)
    print(abc)
    return HttpResponse(abc)
# Peramalan

def importcsv(request):
    df=pd.read_csv('atkjmi.csv', engine='python', header=0, sep=';')
    for i, row in df.iterrows():
        pengajuanABCCek.objects.create(
            atk = str(row['atk']),
            jumlah = int(row['jumlah']),
            harga = int(row['harga']),
            total_harga = int(row['total_harga']),
        )
    print (df.iterrows())
    return HttpResponse(df.iterrows())
