from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404
from django.utils.html import escape
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control
from django.db.models import *
import csv
from decimal import *
import math

from django.core.mail import send_mail
from django.conf import settings

from django.contrib import messages
from .forms import *
from .models import *
import datetime

from abc_analysis import *
import pandas as pd
import numpy as np

from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.seasonal import seasonal_decompose

import sktime
from sktime import datasets
from sktime.forecasting.naive import NaiveForecaster
from sktime.forecasting.model_selection import temporal_train_test_split
from sktime.performance_metrics.forecasting import mean_absolute_percentage_error
from sktime.performance_metrics.forecasting import MeanAbsoluteError
from sktime.forecasting.exp_smoothing import ExponentialSmoothing

from matplotlib import *
from plotly.offline import plot
import plotly.express as px
import plotly.io as pio
# import plotly
import plotly.graph_objs as go

import xlwt

# Create your views here.

def kirim_email(request):
    message = "cek email"
    email = request.user.email
    name = 'ATK Polsub'
    send_mail(
        name, #subject
        message, #message
        'settings.EMAIL_HOST_USER', #sender
        [email], #receiver
        fail_silently=False
    )
    return HttpResponse('email terkirim')


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
    elif request.user.is_adminunit or request.user.is_pimpinanunit:
        tahun = datetime.datetime.now().year
        
        # untuk di notifikasi
        jadwal = Jadwal.objects.filter(tahun=tahun)[:1].first()
        
        pengajuan = Pengajuan.objects.filter(
            unit= request.user.unit,
            jadwal=jadwal
        ).first()
        
        aktivitas_pengeluaran = PenggunaanStok.objects.filter(unit=request.user.unit, tanggal__year=tahun).order_by('-tanggal')[:5]
        sisa_stok = StokATK.objects.filter(unit=request.user.unit).order_by('-updated')[:5]
        
        atk_keluar_terbaru = PenggunaanStok.objects.filter(unit=request.user.unit, tanggal__year=tahun).latest('tanggal')
        atk_keluar_terbanyak = StokATK.objects.filter(unit=request.user.unit).order_by('-jml_keluar').first()
        atk_hampir_habis = StokATK.objects.filter(unit=request.user.unit).order_by('-jumlah').first()
        atk_masuk_terbaru = PenambahanStok.objects.filter(unit=request.user.unit).latest('tanggal')
       
        penggunaan = PenggunaanStok.objects.filter(unit=request.user.unit, tanggal__year=tahun)
        list_id_atk =  penggunaan.values('atk').annotate(jumlah=Sum('jumlah')).order_by()
        atk_list = [StokATK.objects.filter(id=i['atk']).first() for i in list_id_atk]
        print(atk_list)
        stok = StokATK.objects.filter(unit=request.user.unit)
        
        list_nama_atk = [stok.atk.atk for stok in stok]
        list_jumlah = [stok.jumlah for stok in stok] 
        
        penggunaan_with_kegunaan = penggunaan.exclude(guna__isnull=True)
        guna_list = [pwk.guna.kegunaan for pwk in penggunaan_with_kegunaan]
        atk_keluar_list= [pwk.atk.atk.atk for pwk in penggunaan_with_kegunaan]
        jumlah_list= [pwk.jumlah for pwk in penggunaan_with_kegunaan]
       
        pie_chart = 'Data tidak cukup untuk menampilkan grafik sisa stok'
        bar_chart = 'Data tidak cukup untuk menampilkan grafik kegunaan ATK'
    #    VALIDASI DATA SEBELUM DIPROSES CHART
        if list_jumlah != [] and list_nama_atk != [] and guna_list != [] and jumlah_list != [] and atk_keluar_list != []:
            fig_pie = px.pie(values=list_jumlah, names=list_nama_atk)
            pie_chart = fig_pie.to_html

            fig_bar = px.bar(x=guna_list, y=jumlah_list, color=atk_keluar_list).update_layout(
            )
            bar_chart = fig_bar.to_html

        
        context = { 'pie_chart': pie_chart,
                   'bar_chart': bar_chart,
                   'atk_keluar_terbaru': atk_keluar_terbaru,
                   'atk_keluar_terbanyak': atk_keluar_terbanyak,
                   'atk_hampir_habis': atk_hampir_habis,
                   'atk_masuk_terbaru': atk_masuk_terbaru,
                   'aktivitas_pengeluaran': aktivitas_pengeluaran,
                   'sisa_stok': sisa_stok,
                   
                #    untuk notifikasi
                   'jadwal': jadwal,
                   'pengajuan': pengajuan,
                   }
        return render(request, 'atk/dashboardunit.html', context)
    
    elif request.user.is_wadir:
        tahun = datetime.datetime.now().year
        penggunaan = PenggunaanStok.objects.filter(tanggal__year=tahun)
        
        atk_keluar_terbanyak=StokATK.objects.all().values('atk__atk', 'atk__satuan__satuan', 'updated').annotate(sum=Sum('jml_keluar')).order_by('-jml_keluar').first()
        atk_sisa_tersedikit=StokATK.objects.all().values('atk__atk', 'atk__satuan__satuan', 'updated').annotate(sum=Sum('jumlah')).order_by('jumlah').first()
        unit_pencatatan_tersering=PenggunaanStok.objects.all().values('unit__unit').annotate(id_count=Count('id')).order_by('-id_count').first()
        unit_pencatatan_terjarang=PenggunaanStok.objects.all().values('unit__unit').annotate(id_count=Count('id')).order_by('id_count').first()        
        aktivitas_pengeluaran_stok=PenggunaanStok.objects.all().order_by('-tanggal')[:5]
        
        print(unit_pencatatan_terjarang)
        
        penggunaan_with_kegunaan = penggunaan.exclude(guna__isnull=True)
        
        guna_list = [pwk.guna.kegunaan for pwk in penggunaan_with_kegunaan]
        atk_keluar_list= [pwk.atk.atk.atk for pwk in penggunaan_with_kegunaan]
        jumlah_list= [pwk.jumlah for pwk in penggunaan_with_kegunaan]
        
        fig_bar = px.bar(x=guna_list, y=jumlah_list, color=atk_keluar_list).update_layout(xaxis_title="Kegunaan", yaxis_title="Jumlah Stok Keluar (Dalam satuan masing2 ATK)")
        bar_chart = fig_bar.to_html
        
        context = {'bar_chart': bar_chart,
                   'atk_keluar_terbanyak': atk_keluar_terbanyak,
                   'atk_sisa_tersedikit': atk_sisa_tersedikit,
                   'unit_pencatatan_tersering': unit_pencatatan_tersering,
                   'unit_pencatatan_terjarang': unit_pencatatan_terjarang,
                   'aktivitas_pengeluaran_stok': aktivitas_pengeluaran_stok,
                   }
        return render(request, 'atk/wadir/dashboard.html', context)
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
def kelolaPengajuan(request, error_messages=''):
    if request.user.is_wadir:
        unit = Unit.objects.all()
        
        jadwalSekarang = Jadwal.objects.filter(
            tahun = datetime.datetime.now().year
        ).first()
        
        addjadwalForm = formJadwal()
        editjadwalForm = formJadwal(instance=jadwalSekarang)
        
        jadwal = Jadwal.objects.all()
        pengajuanTerbaru = Pengajuan.objects.filter(jadwal=jadwalSekarang, progress='A')[:2]
        pengajuanSekarang = Pengajuan.objects.filter(jadwal=jadwalSekarang, progress='A')
        
        context = {'jadwal':jadwal,
                   'pengajuanSekarang': pengajuanSekarang,
                   'pengajuanTerbaru':pengajuanTerbaru, 
                   'addjadwalForm': addjadwalForm, 
                   'editjadwalForm': editjadwalForm,
                   'unit': unit, 
                   'jadwalSekarang':jadwalSekarang,
                   'error_messages': error_messages,
                   }
        return render(request, 'atk/wadir/pengajuan/pengajuan.html', context)
    else:
        raise Http404
    
@login_required(login_url='login')
def addJadwal(request):
    if request.user.is_wadir:
        jadwalForm = formJadwal(request.POST)
        if jadwalForm.is_valid():
            jadwal = jadwalForm.save()
            periode = jadwal.tahun
            
            # kirim email
            subject = 'Jadwal Pengajuan Barang Habis Pakai'
            message = f"Wakil Direktur II telah mengatur Jadwal Pengajuan Barang Habis Pakai dimulai pada {request.POST.get('pengajuan_mulai')} dan ditutup pada tanggal {request.POST.get('pengajuan_selesai')}"
            email = User.objects.filter(Q(is_adminunit=True) | Q(is_pimpinanunit=True))
            receiver = [e.email for e in email]
            print(receiver)
            
            kirim_email = send_mail(
                subject, #subject
                message, #message
                'settings.EMAIL_HOST_USER', #sender
                receiver, #receiver
                fail_silently=True
            )
            print(kirim_email)
            
            messages.success(request, f'Jadwal Pengajuan Periode {periode} Berhasil Dibuat!')
            return redirect('kelola-pengajuan')
        else:
            error_msg = dict(jadwalForm.errors)
            em = ''
            for e in error_msg['__all__']:
                if em != '':
                    em = em + ', ' + e
                else:
                    em = e
            messages.error(request, em)
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
            
            # kirim email
            subject = 'Perubahan Jadwal Pengajuan Barang Habis Pakai'
            message = f"Wakil Direktur II telah merubah Jadwal Pengajuan Barang Habis Pakai dimulai pada {request.POST.get('pengajuan_mulai')} dan ditutup pada tanggal {request.POST.get('pengajuan_selesai')}"
            email = User.objects.filter(Q(is_adminunit=True) | Q(is_pimpinanunit=True))
            receiver = [e.email for e in email]
            print(receiver)
            
            kirim_email = send_mail(
                subject, #subject
                message, #message
                'settings.EMAIL_HOST_USER', #sender
                receiver, #receiver
                fail_silently=True
            )
            print(kirim_email)
            
            messages.success(request, f'Jadwal Pengajuan Berhasil Diubah!')
            return redirect('kelola-pengajuan')
        else:
            error_msg = dict(jadwalForm.errors)
            em = ''
            for e in error_msg['__all__']:
                if em != '':
                    em = em + ', ' + e
                else:
                    em = e
            messages.error(request, em)
            return redirect('kelola-pengajuan')
    else:
        raise Http404
    
@login_required(login_url='login')
def deleteJadwal(request, pk):
    if request.user.is_wadir:
        return HttpResponse('delete jadwal')
    else:
        raise Http404

@login_required(login_url='login')
def totalPengajuan(request, pk):
    if request.user.is_wadir:
        id=int(pk)
        jadwal = Jadwal.objects.filter(id=id).first()
        totalPengajuan = total_pengajuan.objects.filter(jadwal=jadwal).order_by('-total_dana')
        
        context = {'totalPengajuan': totalPengajuan}
        return render(request, 'atk/wadir/pengajuan/total_pengajuan.html', context)
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
            unit=request.user.unit,
            progress='A'
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
        
        revisi = PerbaikanPengajuan.objects.filter(pengajuan=pengajuan).first()
        
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
                   'atk': atk,
                   'revisi':revisi
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
            return redirect('add-pengajuan')
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

def hasil_ramal(request, atk, scope):
    id_atk = int(atk)
    atk = Barang_ATK.objects.filter(id=id_atk).first()
    stok = StokATK.objects.filter(atk=id_atk).first()
    
    # Cari atk beserta jumlah kegunaannya 
    if scope == "unit":
        stokKeluar = PenggunaanStok.objects.filter(atk=stok.id, unit=request.user.unit).values('tanggal__year').annotate(jumlah=Sum('jumlah')).order_by()
    elif scope == "general":
        stokKeluar = PenggunaanStok.objects.filter(atk=stok.id).values('tanggal__year').annotate(jumlah=Sum('jumlah')).order_by()
    print(stokKeluar)
    
    temp_times = [stokKeluar['tanggal__year'] for stokKeluar in stokKeluar]
    # temp_values = [stokKeluar['jumlah'] for stokKeluar in stokKeluar]
    
    times = []
    values = []
    
    if temp_times != []:
        for i in range(temp_times[0], temp_times[-1]+1):
            times.append(i)
        
        for i in times:
            permintaan = 0
            for s in stokKeluar:
                if s['tanggal__year'] == i:
                    permintaan = s['jumlah']
            values.append(permintaan)
            
        print(values)
        print(times)
        
        times_size = len(times)
         
        # validasi jumlah ketersediaan data
        if times_size <= 0:
            return 0
        elif times_size <= 3:
            forecaster_stok = ExponentialSmoothing(optimized=True) 
        else:
            train_size = int(math.ceil(0.8 * times_size))
            test_size = int(math.ceil(0.2 * times_size))

            # ubah tipe data value yg akan diprediksi ke pandas series
            values_array = np.array(values)
            ser = pd.Series(values_array)

            train, test = temporal_train_test_split(ser, test_size=test_size)
            print(train, test)
            
            # ! BUAT DECISION PEMILIHAN METODE PREDIKSI
            # check if data is constant
            if max(values) == min(values):
                forecaster_stok = ExponentialSmoothing(optimized=True) 
            else:
                # check stationarity in data with some degree of variability.
                check_stat = adfuller(values)
                print('ADF Statistic: %f ' % check_stat[0])
                print('p-value: %f ' % check_stat[1])
                print('Critical Values:')
                for key, value in check_stat[4].items():
                    print('\t%s: %.3f' % (key, value))
            
                has_trend = False
                has_season = False
                has_resid = False
                # jika data tidak stasioner
                print('Data tidak stasioner')
                
                # DECOMPOSE
                # additive decompose
                add_dec = seasonal_decompose(ser, model='additive', period=2)
                print(add_dec.seasonal, add_dec.trend, add_dec.resid, add_dec.observed)
                # Check if the data has a clear trend
                trend = add_dec.trend
                if trend.is_monotonic_increasing or trend.is_monotonic_decreasing:
                    print("The data has a trend.")
                    has_trend = True
                else:
                    print("The data does not have a clear trend.")

                # Check if the data has significant seasonality
                seasonality = add_dec.seasonal
                if seasonality.var() != 0:
                    print("The data has seasonality.")
                    has_season = True
                else:
                    print("The data does not have significant seasonality.")
                    
                residual = add_dec.resid
                if residual.sum() != 0:
                    has_resid = True
            
                if has_trend and has_season:
                    # holt winter exponential smoothing
                    forecaster_stok = ExponentialSmoothing(trend="add", seasonal="add", optimized=True, sp=2)
                elif has_trend: 
                    # double exponential smoothing
                    forecaster_stok = ExponentialSmoothing(trend="add", optimized=True)
                elif has_season:
                    # season with no trend
                    forecaster_stok = ExponentialSmoothing(seasonal="add", optimized=True, sp=2)
                else:
                    forecaster_stok = ExponentialSmoothing(trend="add", damped_trend=True, optimized=True)
                    
                    
            forecaster_stok.fit(train)
            jml_tahun_pred = 2
            fh = np.arange(1,len(test) + 1 + jml_tahun_pred)
            fh2 = np.arange(1,len(test) + 1)
            
            # prediksi
            pred = forecaster_stok.predict(fh=fh)
            # prediksi akurasi
            pred2 = forecaster_stok.predict(fh=fh2)
            # cek akurasi
            mape=mean_absolute_percentage_error(test, pred2, symmetric=True)
            smape=mean_absolute_percentage_error(test, pred2, symmetric=True)
        
            pred_list = pred.to_list()
            rekomendasi = round(pred_list.pop())
            return rekomendasi
    
    return 0
    
    
login_required(login_url='login')
def addIsiPengajuan(request, pk):
    if request.user.is_adminunit:
        id = int(pk)
        isiPengajuanForm = formIsiPengajuan(request.POST, request=request, id_pengajuan=id)
        if isiPengajuanForm.is_valid():
            pengajuan = Pengajuan.objects.get(id=id)
            isiPengajuan = isiPengajuanForm.save(commit=False)
            
            # isi rekomendasi berdasarkan prediksi
            id_atk = request.POST.get("atk")
            rek = hasil_ramal(request, id_atk, 'unit')
            print(rek)
            
            
            isiPengajuan.rekomendasi = rek
            isiPengajuan.pengajuan = pengajuan
            save = isiPengajuan.save()
            
            messages.success(request, "Data berhasil ditambahkan!")
            return redirect('add-pengajuan')
        else:
            error_msg = dict(isiPengajuanForm.errors)
            em = ''
            for e in error_msg['__all__']:
                if em != '':
                    em = em + ', ' + e
                else:
                    em = e
            messages.error(request, em)
            return redirect('add-pengajuan')
    else:
        raise Http404

login_required(login_url='login')
def editIsiPengajuan(request, pk):
    if request.user.is_adminunit:
        id = int(pk)
        isi_pengajuan = Isi_pengajuan.objects.filter(id=id).first()
        atk = Barang_ATK.objects.get(id=request.POST.get('atk'))
        
        if isi_pengajuan is not None:
            isi_pengajuan.atk=atk
            isi_pengajuan.jumlah=int(request.POST.get('jumlah'))
            isi_pengajuan.keterangan=request.POST.get('keterangan')
            
            isi_pengajuan.save(update_fields=['atk', 'jumlah', 'keterangan'])
            
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
        pengajuan = Pengajuan.objects.filter(id=id).first()
        jml_isi = Isi_pengajuan.objects.filter(pengajuan=pengajuan).count()
        
        if jml_isi <= 0:
            messages.error(request, 'Isi pengajuan dengan minimal satu ATK') 
            return redirect('add-pengajuan')
        
        Pengajuan.objects.filter(id=id).update(progress='K', is_aktif=False)
        
        unit = request.user.unit
        pimpinan = User.objects.filter(is_pimpinanunit=True, unit=unit).first()
        
        # kirim email
        subject = 'Konfirmasi Rancangan Pengajuan Barang Habis Pakai'
        message = "Administrator unit telah mengirim rancangan pengajuan, segera lakukan konfirmasi"
        email = pimpinan.email
        
        kirim_email = send_mail(
            subject, #subject
            message, #message
            'settings.EMAIL_HOST_USER', #sender
            [email], #receiver
            fail_silently=True
        )
        print(kirim_email)
        messages.success(request, f'Pengajuan berhasil dikirim!')
        return redirect('pengajuan')
    else:
        raise Http404
    
#stok
@login_required(login_url='login')
def stok(request):
    if request.user.is_adminunit:
        
        stok = StokATK.objects.filter(
                unit = request.user.unit
            )
        tahun = datetime.datetime.now().year
        
        atkMasukAwal = {}
        atkKeluarAwal = {}
        atkAwal = {}
        atkMasuk = {}
        atkKeluar= {}
        atkAkhir = {}
        
        if request.GET.get('start') != None and request.GET.get('end') != None:
            if datetime.datetime.strptime(request.GET.get('start'), "%Y-%m-%d") <= datetime.datetime.strptime(request.GET.get('end'), "%Y-%m-%d"):
                print(datetime.datetime.strptime(request.GET.get('start'), "%Y-%m-%d"))
                start = request.GET.get('start')
                end = request.GET.get('end')
                for s in stok:
                    # stok awal
                    atkMasukAwal[s.atk_id] = int(0 
                                                if PenambahanStok.objects.filter(Q(unit=request.user.unit) &
                                                            Q(tanggal__lte=start) &
                                                            Q(atk_id=s.atk_id)
                                                            ).aggregate(Sum('jumlah'))['jumlah__sum'] is None 
                                                else 
                                                PenambahanStok.objects.filter(Q(unit=request.user.unit) &
                                                            Q(tanggal__lte=start) &
                                                            Q(atk_id=s.atk_id)
                                                            ).aggregate(Sum('jumlah'))['jumlah__sum'])
                    
                    atkKeluarAwal[s.atk_id] = int(0 if PenggunaanStok.objects.filter(Q(unit=request.user.unit) &
                                                            Q(tanggal__lte=start) &
                                                            Q(atk_id=s.atk_id)
                                                            ).aggregate(Sum('jumlah'))['jumlah__sum'] is None
                                                else
                                                PenggunaanStok.objects.filter(Q(unit=request.user.unit) &
                                                            Q(tanggal__lte=start) &
                                                            Q(atk_id=s.atk_id)
                                                            ).aggregate(Sum('jumlah'))['jumlah__sum']
                                                )
                    atkAwal[s.atk_id] = atkMasukAwal[s.atk_id] - atkKeluarAwal[s.atk_id]
                    # stok masuk
                    atkMasuk[s.atk_id] = int(0 if PenambahanStok.objects.filter(Q(unit=request.user.unit) &
                                                            Q(tanggal__gte=start) &
                                                            Q(tanggal__lte=end) &
                                                            Q(atk_id=s.atk_id)
                                                            ).aggregate(Sum('jumlah'))['jumlah__sum'] is None
                                            else
                                            PenambahanStok.objects.filter(Q(unit=request.user.unit) &
                                                            Q(tanggal__gte=start) &
                                                            Q(tanggal__lte=end) &
                                                            Q(atk_id=s.atk_id)
                                                            ).aggregate(Sum('jumlah'))['jumlah__sum']
                                            )
                    # stok keluar
                    atkKeluar[s.atk_id] = int(0 if PenggunaanStok.objects.filter(Q(unit=request.user.unit) &
                                                            Q(tanggal__gte=start) &
                                                            Q(tanggal__lte=end) &
                                                            Q(atk_id=s.atk_id)
                                                            ).aggregate(Sum('jumlah'))['jumlah__sum'] is None
                                            else
                                            PenggunaanStok.objects.filter(Q(unit=request.user.unit) &
                                                            Q(tanggal__gte=start) &
                                                            Q(tanggal__lte=end) &
                                                            Q(atk_id=s.atk_id)
                                                            ).aggregate(Sum('jumlah'))['jumlah__sum']
                                            )
                    # stok akhir
                    atkAkhir[s.atk_id] = atkAwal[s.atk_id] + atkMasuk[s.atk_id] - atkKeluar[s.atk_id]
            else:
                messages.error(request, 'Range tanggal awal dan tanggal akhir tidak valid')
                return redirect('stok')
        else:
            for s in stok:
                # stok awal
                atkMasukAwal[s.atk_id] = int(0
                                            if PenambahanStok.objects.filter(Q(unit=request.user.unit) &
                                                        Q(tanggal__year=tahun-1) &
                                                        Q(atk_id=s.atk_id)
                                                        ).aggregate(Sum('jumlah'))['jumlah__sum'] is None
                                            else
                                            PenambahanStok.objects.filter(Q(unit=request.user.unit) &
                                                        Q(tanggal__year=tahun-1) &
                                                        Q(atk_id=s.atk_id)
                                                        ).aggregate(Sum('jumlah'))['jumlah__sum'] 
                                            )
                atkKeluarAwal[s.atk_id] = int(0
                                            if PenggunaanStok.objects.filter(Q(unit=request.user.unit) &
                                                        Q(tanggal__year=tahun-1) &
                                                        Q(atk_id=s.atk_id)
                                                        ).aggregate(Sum('jumlah'))['jumlah__sum'] is None
                                            else
                                            PenggunaanStok.objects.filter(Q(unit=request.user.unit) &
                                                        Q(tanggal__year=tahun-1) &
                                                        Q(atk_id=s.atk_id)
                                                        ).aggregate(Sum('jumlah'))['jumlah__sum']
                                            )
                atkAwal[s.atk_id] = atkMasukAwal[s.atk_id] - atkKeluarAwal[s.atk_id]
                # stok masuk
                atkMasuk[s.atk_id] = int(0
                                        if  PenambahanStok.objects.filter(Q(unit=request.user.unit) &
                                                        Q(tanggal__year=tahun) &
                                                        Q(atk_id=s.atk_id)
                                                        ).aggregate(Sum('jumlah'))['jumlah__sum'] is None
                                        else
                                        PenambahanStok.objects.filter(Q(unit=request.user.unit) &
                                                        Q(tanggal__year=tahun) &
                                                        Q(atk_id=s.atk_id)
                                                        ).aggregate(Sum('jumlah'))['jumlah__sum']
                                        )
                # stok keluar
                atkKeluar[s.atk_id] = int(0 if PenggunaanStok.objects.filter(Q(unit=request.user.unit) &
                                                        Q(tanggal__year=tahun) &
                                                        Q(atk_id=s.atk_id)
                                                        ).aggregate(Sum('jumlah'))['jumlah__sum'] is None
                                          else
                                          PenggunaanStok.objects.filter(Q(unit=request.user.unit) &
                                                        Q(tanggal__year=tahun) &
                                                        Q(atk_id=s.atk_id)
                                                        ).aggregate(Sum('jumlah'))['jumlah__sum'] 
                                          )
                # stok akhir
                atkAkhir[s.atk_id] = atkAwal[s.atk_id] + atkMasuk[s.atk_id] - atkKeluar[s.atk_id]
        
        
        print(atkAwal, atkMasuk, atkKeluar, atkAkhir)
        kegunaan = guna.objects.filter(unit=request.user.unit)
        
        stokMasuk = PenambahanStok.objects.filter(unit=request.user.unit, tanggal__year=datetime.datetime.now().year)[:10]
        stokKeluar = PenggunaanStok.objects.filter(unit=request.user.unit, tanggal__year=datetime.datetime.now().year)[:10]
        
        stokMasukAll = PenambahanStok.objects.filter(unit=request.user.unit)
        stokKeluarAll = PenggunaanStok.objects.filter(unit=request.user.unit)
        
        total_masuk = PenambahanStok.objects.filter(unit=request.user.unit)
        total_keluar = PenggunaanStok.objects.filter(unit=request.user.unit)
        
        masuk = {}
        for i in total_masuk:
            if i.atk.id in masuk:
                masuk[i.atk.id] += i.jumlah
            else:
                masuk[i.atk.id] = i.jumlah
        print(masuk)
        
        keluar = {}
        for i in total_keluar:
            if i.atk.atk.id in keluar:
                keluar[i.atk.atk.id] += i.jumlah
            else:
                keluar[i.atk.atk.id] = i.jumlah
        print(keluar)
        
             # if request.GET.get('atk') != None:
        #     qatk = penggunaan.filter(atk=request.GET.get('atk')).first()
        # else:
        #     qatk = penggunaan.first()
        # if qatk is not None:
        #     atkq = qatk.atk.id
        #     qatk_name = qatk.atk
        # else:
        #     atkq = 0
        #     qatk_name = ''
        # penggunaan_sum = PenggunaanStok.objects.filter(unit=request.user.unit, tanggal__year=tahun, atk=atkq).values('tanggal').annotate(
        #     jumlah=Sum('jumlah'),
        #     ).order_by()
        
        # print(penggunaan_sum)
        # if penggunaan_sum :
        #     fig = px.line(
        #         x=[p['tanggal'] for p in penggunaan_sum], 
        #         y=[p['jumlah']for p in penggunaan_sum],
        #         title=f'Pengeluaran Stok {qatk_name}',
        #         markers=True,
        #         labels={
        #             'x': 'Tanggal',
        #             'y': 'Stok Keluar'
        #         },
        #         )
        #     line_graph_penggunaan = fig.to_html
        # else: 
        #     line_graph_penggunaan = 'Data tidak cukup untuk menampilkan grafik'
        
        stokKeluarForm = formStokKeluar(request=request)
        stokMasukForm = formStokMasuk()
        gunaForm=formGuna()
        context = {'stok': stok, 'stokMasuk': stokMasuk, 'stokKeluar': stokKeluar,
                    'atkAwal' : atkAwal,
                    'atkMasuk' : atkMasuk,
                    'atkKeluar': atkKeluar,
                    'atkAkhir' : atkAkhir,
                   
                   'stokMasukAll': stokMasukAll, 'stokKeluarAll': stokKeluarAll,
                   'stokKeluarForm': stokKeluarForm, 'stokMasukForm': stokMasukForm,
                   'total_masuk': total_masuk, 'total_keluar': total_keluar,
                   'masuk': masuk, 'keluar': keluar,
                   'kegunaan': kegunaan,
                   'gunaForm': gunaForm,
                   }
        return render(request, 'atk/adminunit/stok/stok.html', context)
    else:
        raise Http404

@login_required(login_url='login')
def addGuna(request):
    if request.user.is_adminunit:
        gunaForm = formGuna(request.POST or None)
        if gunaForm.is_valid():
            guna = gunaForm.save(commit=False)
            guna.unit = request.user.unit
            guna.save()
            messages.success(request, 'Data berhasil disimpan!')
            return redirect('stok')
        else:
            error_msg = dict(gunaForm.errors)
            em = ''
            for e in error_msg['__all__']:
                if em != '':
                    em = em + ', ' + e
                else:
                    em = e
            messages.error(request, em)
            return redirect('stok')
    else:
        raise Http404
    
@login_required(login_url='login')
def editGuna(request, pk):
    if request.user.is_adminunit:
        id = int(pk)
        kegunaan = guna.objects.filter(id=id).first()
        gunaForm = formGuna(request.POST or None, instance=kegunaan)
        if request.method == 'POST':
            if gunaForm.is_valid():
                gunaForm.save()
                messages.success(request, 'Data berhasil diubah!')
                return redirect('detail-guna', id)
            else:
                messages.error(request, 'Terjadi kesalahan!')
                return redirect('detail-guna', id)
        context = {
            'kegunaan': kegunaan,
            'gunaForm': gunaForm,
        }
        return render(request, 'atk/adminunit/stok/editkegunaan.html', context)
    else:
        raise Http404
    
@login_required(login_url='login')
def deleteGuna(request, pk):
    if request.user.is_adminunit:
        id = int(pk)
        kegunaan = guna.objects.filter(id=id).first()
        if kegunaan is not None:
            kegunaan.delete()
            messages.success(request, 'Data berhasil dihapus!')
            return redirect('stok')
        else:
            messages.error(request, 'Terjadi Kesalahan!')
            return redirect('stok')
    else:
        raise Http404
    
@login_required(login_url='login')
def detailGuna(request, pk):
    if request.user.is_adminunit: 
        id = int(pk)
        kegunaan = guna.objects.filter(id=id).first()
        context = {
            'kegunaan': kegunaan
        }
        return render(request, 'atk/adminunit/stok/detailkegunaan.html', context)
    else:
        raise Http404

@login_required(login_url='login')
def addPenggunaanStok(request):
    if request.user.is_adminunit:
        stokKeluarForm = formStokKeluar(request.POST or None, request=request)
        if stokKeluarForm.is_valid():
            
            atk=stokKeluarForm.data.get('atk')
            jumlah=stokKeluarForm.cleaned_data.get('jumlah')
            
            stok = StokATK.objects.filter(id=atk).first()
            print(atk, request.user.unit, stok)
            stok.jumlah = stok.jumlah-jumlah
            if stok.jml_keluar is None:
                stok.jml_keluar = jumlah
            else:
                stok.jml_keluar += jumlah
            stok.save(update_fields=['jumlah', 'jml_keluar'])
            
            stokKeluar = stokKeluarForm.save(commit=False)
            stokKeluar.unit = request.user.unit
            stokKeluar.save()
            messages.success(request, "Data berhasil ditambahkan!")
            return redirect('stok')
        else:
            print(dict(stokKeluarForm.errors))
            error_msg = dict(stokKeluarForm.errors)
            em = ''
            for e in error_msg['__all__']:
                if em != '':
                    em = em + ', ' + e
                else:
                    em = e
            messages.error(request, em)
            return redirect('stok')
    else:
        raise Http404
    
@login_required(login_url='login')
def editPenggunaanStok(request, pk):
    if request.user.is_adminunit:
        id = int(pk)
        # print(id)
        stokKeluar = PenggunaanStok.objects.get(id=id)
        # print(stokKeluar.atk)
        
        stokKeluarForm = formStokKeluar(request.POST or None, instance=stokKeluar, request=request)
        if request.method == 'POST':
            
            # print(stokKeluar.atk, stokKeluar.atk.id)      
            stok1 = StokATK.objects.get(id=stokKeluar.atk.id)
            stok1.jumlah += stokKeluar.jumlah
            stok1.jml_keluar -= stokKeluar.jumlah
            stok1.save(update_fields=['jumlah', 'jml_keluar'])
            # print(stok1, stok1.jumlah)
                
            if stokKeluarForm.is_valid():
                
                atk=stokKeluarForm.data.get('atk')
                jumlah=stokKeluarForm.cleaned_data.get('jumlah')     
                
                stok2 = StokATK.objects.filter(id=atk).first()
                stok2.jumlah -= jumlah
                stok2.jml_keluar += jumlah
                stok2.save(update_fields=['jumlah', 'jml_keluar'])
                # print(stok2, stok2.jumlah)
                
                stokKeluarForm.save()
                messages.success(request, "Data berhasil diubah!")
                return redirect('stok')
            else:
                error_msg = dict(stokKeluarForm.errors)
                em = ''
                for e in error_msg['__all__']:
                    if em != '':
                        em = em + ', ' + e
                    else:
                        em = e
                messages.error(request, em)
                return redirect('stok')
        context = {'stokKeluarForm': stokKeluarForm}
        return render(request, 'atk/adminunit/stok/editstokkeluar.html', context)
        
    else:
        raise Http404
    
@login_required(login_url='login')
def deletePenggunaanStok(request, pk):
    if request.user.is_adminunit:
        id = int(pk)
        stokKeluar = PenggunaanStok.objects.filter(id=id).first()

        stok = StokATK.objects.get(id=stokKeluar.atk.id)
        if stok is not None and stokKeluar is not None:
            
            print(stok.jumlah, stok.atk.atk)
            stok.jumlah += stokKeluar.jumlah
            stok.jml_keluar -= stokKeluar.jumlah
            stok.save(update_fields=['jumlah', 'jml_keluar'])
            print(stok.jumlah, stok.atk.atk)
             
            stokKeluar.delete()
            messages.success(request, "Data berhasil dihapus!")
            return redirect('stok')
        else:
            messages.error(request, 'Terjadi kesalahan!')
            return redirect('stok')
    else:
        raise Http404
    
@login_required(login_url='login')
def detailStokKeluar(request, pk):
    if request.user.is_adminunit:
        id = int(pk)
        stokKeluar = PenggunaanStok.objects.filter(id=pk).first()
        if stokKeluar.tanggal.month == datetime.datetime.now().month:
            editable = True
        else:
            editable = False
        context = {
            'stokKeluar': stokKeluar,
            'editable': editable
        }
        return render(request, 'atk/adminunit/stok/detailkeluar.html', context)
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
                    jml_masuk=jumlah,
                    unit=request.user.unit
                )
            else:
                stok.jumlah += jumlah
                stok.jml_masuk += jumlah
                stok.save(
                    update_fields=['jumlah', 'jml_masuk']
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
        stokMasuk = PenambahanStok.objects.get(id=id)
        
        stokMasukForm = formStokMasuk(request.POST or None, instance=stokMasuk)
        if request.method == 'POST':
            
            stok1 = StokATK.objects.filter(unit=request.user.unit, atk=stokMasuk.atk).first()
            stok1.jumlah -= stokMasuk.jumlah
            stok1.jml_masuk -= stokMasuk.jumlah
            stok1.save(update_fields=['jumlah', 'jml_masuk'])
            
            if stokMasukForm.is_valid():
                
                atk=stokMasukForm.cleaned_data.get('atk')
                jumlah=stokMasukForm.cleaned_data.get('jumlah')
                
                stok2 = StokATK.objects.filter(unit=request.user.unit, atk=atk).first()
                stok2.jumlah += jumlah
                stok2.jml_masuk += jumlah
                stok2.save(update_fields=['jumlah', 'jml_masuk'])
                
                stokMasukForm.save()
                messages.success(request, "Data berhasil diubah!")
                return redirect('stok')
            else:
                error_msg = dict(stokMasukForm.errors)
                em = ''
                for e in error_msg['__all__']:
                    if em != '':
                        em = em + ', ' + e
                    else:
                        em = e
                messages.error(request, em)
                return redirect('stok')
        context = {'stokMasukForm': stokMasukForm}
        return render(request, 'atk/adminunit/stok/editstokmasuk.html', context)
    else:
        raise Http404
    
@login_required(login_url='login')
def deletePenambahanStok(request, pk):
    if request.user.is_adminunit:
        id = int(pk)
        stokMasuk = PenambahanStok.objects.filter(id=id).first()
        stok = StokATK.objects.filter(unit=request.user.unit, atk=stokMasuk.atk).first()
        if stokMasuk is not None and stok is not None:
            
            stok.jumlah -= stokMasuk.jumlah
            stok.jml_masuk -= stokMasuk.jumlah
            stok.save(update_fields=['jumlah', 'jml_masuk'])
            
            stokMasuk.delete()
            messages.success(request, "Data berhasil dihapus!")
            return redirect('stok')
        else:
            messages.error(request, 'Terjadi kesalahan!')
            return redirect('stok')
    else:
        raise Http404
    
@login_required(login_url='login')
def detailStokMasuk(request, pk):
    if request.user.is_adminunit:
        id = int(pk)
        stokMasuk = PenambahanStok.objects.filter(id=id).first()
        if stokMasuk.tanggal.month == datetime.datetime.now().month:
            editable = True
        else:
            editable = False
        context = {
            'stokMasuk': stokMasuk,
            'editable': editable
        }
        return render(request, 'atk/adminunit/stok/detailmasuk.html', context)
    else:
        raise Http404

#PIMPINAN UNIT
@login_required(login_url='login')
def tinjauPengajuan(request):
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
            progress='A'
        )
    
        context = {'jadwal': jadwal, 'pengajuan': pengajuan, 'riwayat_pengajuan':riwayat_pengajuan}
        return render(request, 'atk/pimpinanunit/pengajuan/pengajuan.html', context)
    else:
        raise Http404
    
@login_required(login_url='login')
def konfirPengajuan(request, pk):
    if request.user.is_pimpinanunit:
        id = int(pk)
        pengajuan=Pengajuan.objects.filter(id=id).first()
        isi_pengajuan = Isi_pengajuan.objects.filter(pengajuan=pengajuan)
        
        perbaikanForm = formPerbaikan()
        context = {'pengajuan': pengajuan, 'isi_pengajuan': isi_pengajuan, 'perbaikanForm': perbaikanForm}
        return render(request, 'atk/pimpinanunit/pengajuan/konfirPengajuan.html', context)
    else:
        raise Http404
    
@login_required(login_url='login')
def addPerbaikan(request, pk):
    if request.user.is_pimpinanunit:
        id = int(pk)
        pengajuan=Pengajuan.objects.filter(id=id)
        
        form = formPerbaikan(request.POST)
        if form.is_valid():
            perbaikan = form.save(commit=False)
            
            perbaikan.pengajuan = pengajuan.first()
            perbaikan.save()
            
            jml_perbaikan = pengajuan.first().perbaikan + 1
            pengajuan.update(
                is_aktif=True,
                perbaikan= jml_perbaikan,
                progress = 'P'
            )
            
            unit = request.user.unit
            admin_unit = User.objects.filter(is_adminunit=True, unit=unit).first()
            
            # kirim email
            subject = 'Perintah Revisi Rancangan Pengajuan'
            message = f"Pimpinan unit memerintahkan revisi rancangan pengajuan dengan keterangan : {request.POST.get('keterangan')}"
            email = admin_unit.email
            
            kirim_email = send_mail(
                subject, #subject
                message, #message
                'settings.EMAIL_HOST_USER', #sender
                [email], #receiver
                fail_silently=True
            )
            print(kirim_email)
            
            messages.success(request, f"Perbaikan untuk pengajuan nomor surat {pengajuan.first().no_surat} berhasil dikirim!")
            return redirect('tinjau-pengajuan')
        else:
            messages.error(request, 'Terjadi Kesalahan!')
        return redirect('konfir-pengajuan', pk)
    else:
        raise Http404
    
@login_required(login_url='login')
def kirimPengajuan(request, pk):
    if request.user.is_pimpinanunit:
        id = int(pk)
        pengajuan=Pengajuan.objects.filter(id=id)
        
        pengajuan.update(
                progress = 'A',
                tanggal_konfirmasi=datetime.datetime.now()
            )
        
        isi_pengajuan = Isi_pengajuan.objects.filter(pengajuan=pengajuan.first())
        
        unit = request.user.unit
        wadir = User.objects.filter(is_wadir=True).first()
        
        # kirim email
        subject = f'Pengajuan Barang Habis Pakai Unit {unit}'
        message = f"Unit {unit} telah melakukan pengajuan barang habis pakai"
        email = wadir.email
        
        kirim_email = send_mail(
            subject, #subject
            message, #message
            'settings.EMAIL_HOST_USER', #sender
            [email], #receiver
            fail_silently=True
        )
        print(kirim_email)
        
        for isi in isi_pengajuan:
            rek = hasil_ramal(request, isi.atk.id, 'general')
            total = total_pengajuan.objects.filter(jadwal=pengajuan.first().jadwal, atk=isi.atk).first()
            harga = Harga.objects.filter(atk=isi.atk).first() #jgn lupa filter periode harga
            if total is None:
                total_pengajuan.objects.create(
                    jadwal=pengajuan.first().jadwal,
                    atk=isi.atk,
                    jumlah=isi.jumlah,
                    rekomendasi = rek,
                    harga= harga,
                    total_dana=harga.harga * (isi.jumlah)
                )
            else:
                total.rekomendasi = rek
                total.jumlah += isi.jumlah
                total.total_dana = total.jumlah * harga.harga
                total.save(update_fields=['jumlah', 'total_dana', 'rekomendasi'])
        
        messages.success(request, f"Pengajuan dengan nomor surat {pengajuan.first().no_surat} berhasil dikirim!")
        return redirect('tinjau-pengajuan')
    else:
        raise Http404

    
@login_required(login_url='login')
def detailPengajuan(request, pk):
    if request.user.is_pimpinanunit or request.user.is_adminunit or request.user.is_wadir:
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
def atk_abc_analysis_cek(request): 

    total_penggunaan = pengajuanABCCek.objects.all()
    dana = []
    id = []
    for i in total_penggunaan:
        i.dana = i.jumlah * i.harga
        i.save(update_fields=['dana'])
        dana.append(i.dana)
        id.append(i.id)
    try:
        abc = abc_analysis(dana)
        
    except ValueError:
        abc = None
    except:
        abc = None  
        
    if abc is not None:
        for a in abc['Aind']:
            id_hasil = id[a]
            hasil = pengajuanABCCek.objects.filter(id=id_hasil).first()
            print(hasil)
            hasil.prioritas = 'A'
            hasil.save(update_fields=['prioritas'])
        for b in abc['Bind']:
            id_hasil = id[b]
            hasil = pengajuanABCCek.objects.filter(id=id_hasil).first()
            hasil.prioritas = 'B'
            hasil.save(update_fields=['prioritas'])
        for c in abc['Cind']:
            id_hasil = id[c]
            hasil = pengajuanABCCek.objects.filter(id=id_hasil).first()
            hasil.prioritas = 'C'
            hasil.save(update_fields=['prioritas'])
       
    hasil = pengajuanABCCek.objects.all().order_by('-dana')
    total_dana = hasil.aggregate(Sum('dana'))
    total_item = hasil.aggregate(Count('atk'))
    id_before = None
    for i in hasil:
        i.persentase_item = 1/total_item['atk__count']
        i.persentase_dana = i.dana/total_dana['dana__sum']
        i.save(update_fields=['persentase_item', 'persentase_dana'])
        if id_before is None:
            i.persentase_kumulatif_dana = i.persentase_dana
            i.persentase_kumulatif_item = i.persentase_item
            i.save(update_fields=['persentase_kumulatif_dana', 'persentase_kumulatif_item'])
        else: 
            before = pengajuanABCCek.objects.filter(id=id_before).first()
            i.persentase_kumulatif_dana = i.persentase_dana + before.persentase_kumulatif_dana
            i.persentase_kumulatif_item = i.persentase_item + before.persentase_kumulatif_item
            i.save(update_fields=['persentase_kumulatif_dana', 'persentase_kumulatif_item'])

        id_before = i.id
        
    hasil_abc = pengajuanABCCek.objects.all().order_by('-dana')
    print(abc)
    fig = go.Figure()
    
    trace_0 = go.Scatter(
        x=[hasil_abc.persentase_kumulatif_item for hasil_abc in hasil_abc],
        y=[hasil_abc.persentase_kumulatif_dana for hasil_abc in hasil_abc],
        mode='markers+lines',
    )
    fig.add_trace(trace_0)
    
    
    # 80% Volume
    dana80 = hasil_abc.filter(prioritas='C')
    perc_item80 = dana80.aggregate(Max('persentase_kumulatif_item'))
    perc_dana80 = dana80.aggregate(Max('persentase_kumulatif_dana'))

    # # 20% SKU
    item20 = hasil_abc.filter(prioritas='B')
    perc_item20 = item20.aggregate(Max('persentase_kumulatif_item'))
    perc_dana20 = item20.aggregate(Max('persentase_kumulatif_dana'))

    # 5% SKU
    item5 = hasil_abc.filter(prioritas='A')
    perc_item5 = item5.aggregate(Max('persentase_kumulatif_item'))
    perc_dana5 = item5.aggregate(Max('persentase_kumulatif_dana'))
  
    
    # 5% SKU
    fig.add_hline(y=perc_dana5['persentase_kumulatif_dana__max'], line_width=1, line_dash="dash", line_color="red", annotation_text="PRIORITAS TINGGI")
    fig.add_vline(x=perc_item5['persentase_kumulatif_item__max'], line_width=1, line_dash="dash", line_color="red")
    
    # # 80% Volume
    fig.add_hline(y=perc_dana80['persentase_kumulatif_dana__max'], line_width=1, line_dash="dash", line_color="green", annotation_text="PRIORITAS RENDAH")
    fig.add_vline(x=perc_item80['persentase_kumulatif_item__max'], line_width=1, line_dash="dash", line_color="green")
    
    # # 20% SKU
    fig.add_hline(y=perc_dana20['persentase_kumulatif_dana__max'], line_width=1, line_dash="dash", line_color="blue", annotation_text="PRIORITAS SEDANG")
    fig.add_vline(x=perc_item20['persentase_kumulatif_item__max'], line_width=1, line_dash="dash", line_color="blue")
    
    fig.update_layout(
    xaxis_title="Kumulatif Item", yaxis_title="Kumulatif Dana")
    
    fig.layout.xaxis.tickformat = ',.0%'
    fig.layout.yaxis.tickformat = ',.0%'
    
    print(fig)
    chart = fig.to_html
    context = {'hasil_abc':hasil_abc, 'abc': abc, 'chart': chart}
    return render(request, 'atk/abc.html', context)

@login_required(login_url='login')
def atk_abc_analysis(request, scope): 
    tahun = datetime.datetime.now().year
    if scope == 'unit':
        total_penggunaan = PenggunaanStok.objects.filter(unit=request.user.unit, tanggal__year=tahun)
    elif scope == 'general':
        total_penggunaan = PenggunaanStok.objects.filter(tanggal__year=tahun)
    
    penggunaan = {}
    for i in total_penggunaan:
        if i.atk.atk.id in penggunaan:
            penggunaan[i.atk.atk.id] += i.jumlah
        else:
            penggunaan[i.atk.atk.id] = i.jumlah
    print(penggunaan)
    
    list_total_harga = []
    list_atk = []
    list_jml = []
    for (key, value) in enumerate(penggunaan.items()):
        harga = Harga.objects.filter(atk=value[0]).first() #filter juga periode harga nantinya
        total_harga = harga.harga * value[1]
        
        list_total_harga.append(total_harga)
        list_atk.append(value[0])
        list_jml.append(value[1])
    print(list_total_harga)
    if scope == 'unit':
        abc_analysis_model.objects.filter(unit=request.user.unit, tahun=tahun).delete()
    elif scope == 'general':
        abc_analysis_model_general.objects.filter(tahun=tahun).delete()
    
    try:
        abc = abc_analysis(list_total_harga)
    except ValueError:
        abc = None
    except:
        abc = None
    else:
        for a in abc['Aind']:
            atk = Barang_ATK.objects.filter(id=list_atk[a]).first()
            harga = Harga.objects.filter(atk=list_atk[a]).first()
            if scope == 'unit':
                abc_analysis_model.objects.create(
                    atk=atk,
                    harga=harga.harga,
                    dana=list_total_harga[a],
                    prioritas='A',
                    jumlah = list_jml[a],
                    
                    tahun=tahun,
                    unit=request.user.unit
                )
            elif scope == 'general':
                abc_analysis_model_general.objects.create(
                    atk=atk,
                    harga=harga.harga,
                    dana=list_total_harga[a],
                    prioritas='A',
                    jumlah = list_jml[a],
                    
                    tahun=tahun,
                )
        for b in abc['Bind']:
            atk = Barang_ATK.objects.filter(id=list_atk[b]).first()
            harga = Harga.objects.filter(atk=list_atk[b]).first()
            if scope == 'unit':
                abc_analysis_model.objects.create(
                    atk=atk,
                    harga=harga.harga,
                    dana=list_total_harga[b],
                    prioritas='B',
                    jumlah = list_jml[b],
                    
                    tahun=tahun,
                    unit=request.user.unit
                )
            elif scope == 'general':
                abc_analysis_model_general.objects.create(
                    atk=atk,
                    harga=harga.harga,
                    dana=list_total_harga[b],
                    prioritas='B',
                    jumlah = list_jml[b],
                    
                    tahun=tahun,        
                )
        for c in abc['Cind']:
            atk = Barang_ATK.objects.filter(id=list_atk[c]).first()
            harga = Harga.objects.filter(atk=list_atk[c]).first()
            if scope == 'unit':
                abc_analysis_model.objects.create(
                    atk=atk,
                    harga=harga.harga,
                    dana=list_total_harga[c],
                    prioritas='C',
                    jumlah = list_jml[c],
                    
                    tahun=tahun,
                    unit=request.user.unit
                )
            elif scope == 'general':
                abc_analysis_model_general.objects.create(
                    atk=atk,
                    harga=harga.harga,
                    dana=list_total_harga[c],
                    prioritas='C',
                    jumlah = list_jml[c],
                    
                    tahun=tahun,
                )
        if scope == 'unit':
            hasil = abc_analysis_model.objects.filter(unit=request.user.unit, tahun=tahun).order_by('-dana')
        elif scope == 'general':
            hasil = abc_analysis_model_general.objects.filter(tahun=tahun).order_by('-dana')
        total_dana = hasil.aggregate(Sum('dana'))
        total_item = hasil.aggregate(Count('atk'))
        id_before = None
        for i in hasil:
            i.persentase_item = 1/total_item['atk__count']
            i.persentase_dana = i.dana/total_dana['dana__sum']
            i.save(update_fields=['persentase_item', 'persentase_dana'])
            if id_before is None:
                i.persentase_kumulatif_dana = i.persentase_dana
                i.persentase_kumulatif_item = i.persentase_item
                i.save(update_fields=['persentase_kumulatif_dana', 'persentase_kumulatif_item'])
            else: 
                if scope == 'unit':
                    before = abc_analysis_model.objects.filter(id=id_before).first()
                elif scope == 'general':
                    before = abc_analysis_model_general.objects.filter(id=id_before).first()
                i.persentase_kumulatif_dana = i.persentase_dana + before.persentase_kumulatif_dana
                i.persentase_kumulatif_item = i.persentase_item + before.persentase_kumulatif_item
                i.save(update_fields=['persentase_kumulatif_dana', 'persentase_kumulatif_item'])

            id_before = i.id
            
    print(abc)
    return(abc)

@login_required(login_url='login')
def check_abc_unit(request, unit):
    if request.user.is_wadir:
        tahun = datetime.datetime.now().year
        id_unit = int(unit)
        unit = Unit.objects.filter(id=id_unit).first()
        
        hasil_abc = abc_analysis_model.objects.filter(unit=unit, tahun=tahun).order_by('-dana')
        
        print(hasil_abc)
        if hasil_abc.count() == 0:
            context = {'hasil_abc':hasil_abc, 'unit': unit}
            return render(request, 'atk/wadir/analisis/abc_unit.html', context)
        
        fig = go.Figure()
        
        trace_0 = go.Scatter(
            x=[hasil_abc.persentase_kumulatif_item for hasil_abc in hasil_abc],
            y=[hasil_abc.persentase_kumulatif_dana for hasil_abc in hasil_abc],
            mode='markers+lines',
        )
        fig.add_trace(trace_0)
        
        # 80% Volume
        dana80 = hasil_abc.filter(prioritas='C')
        perc_item80 = dana80.aggregate(Max('persentase_kumulatif_item'))
        perc_dana80 = dana80.aggregate(Max('persentase_kumulatif_dana'))

        # # 20% SKU
        item20 = hasil_abc.filter(prioritas='B')
        perc_item20 = item20.aggregate(Max('persentase_kumulatif_item'))
        perc_dana20 = item20.aggregate(Max('persentase_kumulatif_dana'))

        # 5% SKU
        item5 = hasil_abc.filter(prioritas='A')
        perc_item5 = item5.aggregate(Max('persentase_kumulatif_item'))
        perc_dana5 = item5.aggregate(Max('persentase_kumulatif_dana'))
    
        
        # 5% SKU
        fig.add_hline(y=perc_dana5['persentase_kumulatif_dana__max'], line_width=1, line_dash="dash", line_color="red", annotation_text = "PIORITAS TINGGI")
        fig.add_vline(x=perc_item5['persentase_kumulatif_item__max'], line_width=1, line_dash="dash", line_color="red")
        
        # # 80% Volume
        fig.add_hline(y=perc_dana80['persentase_kumulatif_dana__max'], line_width=1, line_dash="dash", line_color="green",  annotation_text = "PRIORITAS RENDAH")
        fig.add_vline(x=perc_item80['persentase_kumulatif_item__max'], line_width=1, line_dash="dash", line_color="green")
        
        # # 20% SKU
        fig.add_hline(y=perc_dana20['persentase_kumulatif_dana__max'], line_width=1, line_dash="dash", line_color="blue", annotation_text = "PRIORITAS SEDANG")
        fig.add_vline(x=perc_item20['persentase_kumulatif_item__max'], line_width=1, line_dash="dash", line_color="blue")
        
        fig.update_layout(
        xaxis_title="Kumulatif Item", yaxis_title="Kumulatif Dana")
        
        fig.layout.xaxis.tickformat = ',.0%'
        fig.layout.yaxis.tickformat = ',.0%'
        
        
        print(fig)
        chart = fig.to_html
        context = {'hasil_abc':hasil_abc, 'chart': chart, 'unit': unit}
        return render(request, 'atk/wadir/analisis/abc_unit.html', context)
    else:
        return Http404

@login_required(login_url='login')
def cek_prediksi_unit(request, unit, atk):
    # id atk yang akan diprediksi
    id_atk = int(atk)
    id_unit = int(unit)
    atk = Barang_ATK.objects.filter(id=id_atk).first()
    unit = Unit.objects.filter(id=id_unit).first()
    stok = StokATK.objects.filter(atk=id_atk).first()
    
    # Cari atk beserta jumlah kegunaannya 
    stokKeluar = PenggunaanStok.objects.filter(atk=stok.id, unit=unit).values('tanggal__year').annotate(jumlah=Sum('jumlah')).order_by()
    print(stokKeluar)
    
    temp_times = [stokKeluar['tanggal__year'] for stokKeluar in stokKeluar]
    # temp_values = [stokKeluar['jumlah'] for stokKeluar in stokKeluar]
    
    times = []
    values = []
    
    for i in range(temp_times[0], temp_times[-1]+1):
        times.append(i)
     
    for i in times:
        permintaan = 0
        for s in stokKeluar:
            if s['tanggal__year'] == i:
                permintaan = s['jumlah']
        values.append(permintaan)
        
    print(values)
    print(times)
    
    times_size = len(times)
    
    
    # validasi jumlah ketersediaan data
    if times_size < 0:
        context = {
            'pred':None,
            'msg':"Data pada ATK belum siap untuk diprediksi"
        }
        return render(request, 'atk/forecast_unit.html', context)
    elif times_size <= 2:
        context = {
            'pred':None,
            'msg':"Data pada ATK belum siap untuk diprediksi"
        }
        return render(request, 'atk/forecast_unit.html', context)
    else:
        train_size = int(math.ceil(0.8 * times_size))
        test_size = int(math.ceil(0.2 * times_size))

        # ubah tipe data value yg akan diprediksi ke pandas series
        values_array = np.array(values)
        ser = pd.Series(values_array)

        train, test = temporal_train_test_split(ser, test_size=test_size)
        print(train, test)
        
        # ! BUAT DECISION PEMILIHAN METODE PREDIKSI
        # check if data is constant
        if max(values) == min(values):
            forecaster_stok = ExponentialSmoothing(optimized=True) 
        else:
            # check stationarity in data with some degree of variability.
            check_stat = adfuller(values)
            print('ADF Statistic: %f ' % check_stat[0])
            print('p-value: %f ' % check_stat[1])
            print('Critical Values:')
            for key, value in check_stat[4].items():
                print('\t%s: %.3f' % (key, value))
        
            has_trend = False
            has_season = False
            has_resid = False
            # jika data tidak stasioner
            print('Data tidak stasioner')
            
            # DECOMPOSE
            # additive decompose
            add_dec = seasonal_decompose(ser, model='additive', period=2)
            print(add_dec.seasonal, add_dec.trend, add_dec.resid, add_dec.observed)
            # Check if the data has a clear trend
            trend = add_dec.trend
            if trend.is_monotonic_increasing or trend.is_monotonic_decreasing:
                print("The data has a trend.")
                has_trend = True
            else:
                print("The data does not have a clear trend.")

            # Check if the data has significant seasonality
            seasonality = add_dec.seasonal
            if seasonality.var() != 0:
                print("The data has seasonality.")
                has_season = True
            else:
                print("The data does not have significant seasonality.")
                
            residual = add_dec.resid
            if residual.sum() != 0:
                has_resid = True
        
            if has_trend and has_season:
                # holt winter exponential smoothing
                forecaster_stok = ExponentialSmoothing(trend="add", seasonal="add", optimized=True, sp=2)
            elif has_trend: 
                # double exponential smoothing
                forecaster_stok = ExponentialSmoothing(trend="add", optimized=True)
            elif has_season:
                # season with no trend
                forecaster_stok = ExponentialSmoothing(seasonal="add", optimized=True, sp=2)
            else:
                forecaster_stok = ExponentialSmoothing(trend="add", damped_trend=True, optimized=True)

        forecaster_stok.fit(train)
        jml_tahun_pred = 2
        fh = np.arange(1,len(test) + 1 + jml_tahun_pred)
        fh2 = np.arange(1,len(test) + 1)
        
        # prediksi
        pred = forecaster_stok.predict(fh=fh)
        # prediksi akurasi
        pred2 = forecaster_stok.predict(fh=fh2)
        # cek akurasi
        mape=mean_absolute_percentage_error(test, pred2, symmetric=True)
        smape=mean_absolute_percentage_error(test, pred2, symmetric=True)

        print()
        print(f"MAPE: {mape}, SMAPE: {smape}")
        # ubah semua type hasil ke list
        train_list, test_list, pred_list = train.to_list(), test.to_list(), pred.to_list()
        print(train_list, test_list, pred_list, sep='\n')
        
        # cari nilai x pada diagram untuk 3 diagram garis (test, train, pred)
        x_train_list = times[:train_size+1]
        x_test_list = times[-test_size:]
        x_pred_list = times[-test_size:] + [*range(times[-1]+1, times[-1]+jml_tahun_pred)]
        
        # diagram
        fig = go.Figure()
        trace_train = go.Scatter(
            x=x_train_list,
            y=train_list + test_list[:1],
            mode='markers+lines',
            name='Data Latih',
            showlegend=True,
        )
        trace_test = go.Scatter(
            x=x_test_list,
            y=test_list,
            mode='markers+lines',
            name='Data Uji',
            showlegend=True,
        )
        trace_pred = go.Scatter(
            x=x_pred_list,
            y=pred_list,
            mode='markers+lines',
            name='Hasil Prediksi',
            showlegend=True,
        )
        fig.add_trace(trace_train)
        fig.add_trace(trace_test)
        fig.add_trace(trace_pred)
        
        fig.update_traces(hovertemplate=None)
        fig.update_layout(hovermode="x unified")
        fig.update_layout(
        xaxis_title="Tahun", yaxis_title="Jumlah Kegunaan")
        chart = fig.to_html
        
        context = {
            'chart': chart,
            'mape': mape,
            'mape_persen': (1-mape),
            'smape': smape,
            'smape_persen': (1-smape),
            'atk':atk,
            'pred':round(pred_list.pop()),
            'test':test_list.pop(),
        }
        return render(request, 'atk/forecast_unit.html', context)

@login_required(login_url='login')
def lihat_analisis_unit(request, scope):  
    if request.user.is_adminunit or request.user.is_pimpinanunit:
        scope = 'unit'
    abc = atk_abc_analysis(request, scope)

    tahun = datetime.datetime.now().year
    if scope == 'unit':
        hasil_abc = abc_analysis_model.objects.filter(unit=request.user.unit, tahun=tahun).order_by('-dana')
    elif scope == 'general':
        hasil_abc = abc_analysis_model_general.objects.filter(tahun=tahun).order_by('-dana')
    
    
    print(abc)
    print(hasil_abc)
    
    if hasil_abc.count() == 0:
        context = {'pesan': 'Data belum cukup untuk dianalisis'}
        return render(request, 'atk/metode/abc_analysis.html', context)
    
    fig = go.Figure()
    
    trace_0 = go.Scatter(
        x=[hasil_abc.persentase_kumulatif_item for hasil_abc in hasil_abc],
        y=[hasil_abc.persentase_kumulatif_dana for hasil_abc in hasil_abc],
        mode='markers+lines',
    )
    fig.add_trace(trace_0)
    
    # 80% Volume
    dana80 = hasil_abc.filter(prioritas='C')
    perc_item80 = dana80.aggregate(Max('persentase_kumulatif_item'))
    perc_dana80 = dana80.aggregate(Max('persentase_kumulatif_dana'))

    # # 20% SKU
    item20 = hasil_abc.filter(prioritas='B')
    perc_item20 = item20.aggregate(Max('persentase_kumulatif_item'))
    perc_dana20 = item20.aggregate(Max('persentase_kumulatif_dana'))

    # 5% SKU
    item5 = hasil_abc.filter(prioritas='A')
    perc_item5 = item5.aggregate(Max('persentase_kumulatif_item'))
    perc_dana5 = item5.aggregate(Max('persentase_kumulatif_dana'))
  
    
    # 5% SKU
    fig.add_hline(y=perc_dana5['persentase_kumulatif_dana__max'], line_width=1, line_dash="dash", line_color="red", annotation_text = "PIORITAS TINGGI")
    fig.add_vline(x=perc_item5['persentase_kumulatif_item__max'], line_width=1, line_dash="dash", line_color="red")
    
    # # 80% Volume
    fig.add_hline(y=perc_dana80['persentase_kumulatif_dana__max'], line_width=1, line_dash="dash", line_color="green",  annotation_text = "PRIORITAS RENDAH")
    fig.add_vline(x=perc_item80['persentase_kumulatif_item__max'], line_width=1, line_dash="dash", line_color="green")
    
    # # 20% SKU
    fig.add_hline(y=perc_dana20['persentase_kumulatif_dana__max'], line_width=1, line_dash="dash", line_color="blue", annotation_text = "PRIORITAS SEDANG")
    fig.add_vline(x=perc_item20['persentase_kumulatif_item__max'], line_width=1, line_dash="dash", line_color="blue")
    
    fig.update_layout(
    xaxis_title="Kumulatif Item", yaxis_title="Kumulatif Dana")
    
    fig.layout.xaxis.tickformat = ',.0%'
    fig.layout.yaxis.tickformat = ',.0%'
    
    if request.user.is_wadir:
        unit = Unit.objects.all()
    else:
        unit = None
     
    print(fig)
    chart = fig.to_html
    context = {'hasil_abc':hasil_abc, 'abc': abc, 'chart': chart, 'unit': unit}
    return render(request, 'atk/metode/abc_analysis.html', context)


# Peramalan
@login_required(login_url='login')
def forecastUnit(request, pk):
    # id atk yang akan diprediksi
    id_atk = int(pk)
    atk = Barang_ATK.objects.filter(id=id_atk).first()
    stok = StokATK.objects.filter(atk=id_atk).first()
    
    tahun_akhir = datetime.datetime.now().year
    print(tahun_akhir, type(tahun_akhir))
    tahun_awal = tahun_akhir if PenggunaanStok.objects.filter(atk=stok.id, unit=request.user.unit).values('tanggal__year').order_by('-tanggal').last()['tanggal__year'] is None else PenggunaanStok.objects.filter(atk=stok.id, unit=request.user.unit).values('tanggal__year').order_by('-tanggal').last()['tanggal__year']
    print(tahun_awal, type(tahun_awal))
    
    list_tahun = [i for i in range(tahun_awal, tahun_akhir+1)]
    
    if request.GET.get('start') != None and request.GET.get('end') != None:
        if request.GET.get('start') < request.GET.get('end'):
            start = request.GET.get('start')
            end = request.GET.get('end')
        # Cari atk beserta jumlah kegunaannya 
            stokKeluar = PenggunaanStok.objects.filter(Q(atk=stok.id) & Q(unit=request.user.unit) & 
                                                Q(tanggal__year__gte=start) &
                                                Q(tanggal__year__lte=end) 
                                                ).values('tanggal__year').annotate(jumlah=Sum('jumlah')).order_by()
        else:
            messages.error(request, 'Range tahun awal dan tahun akhir tidak valid')
            return redirect('forecast-unit', pk)
    else:
        # Cari atk beserta jumlah kegunaannya 
        stokKeluar = PenggunaanStok.objects.filter(atk=stok.id, unit=request.user.unit).values('tanggal__year').annotate(jumlah=Sum('jumlah')).order_by()
    
    print(stokKeluar)
    
    temp_times = [stokKeluar['tanggal__year'] for stokKeluar in stokKeluar]
    # temp_values = [stokKeluar['jumlah'] for stokKeluar in stokKeluar]
    
    times = []
    values = []
    
    for i in range(temp_times[0], temp_times[-1]+1):
        times.append(i)
     
    for i in times:
        permintaan = 0
        for s in stokKeluar:
            if s['tanggal__year'] == i:
                permintaan = s['jumlah']
        values.append(permintaan)
        
    print(values)
    print(times)
    
    times_size = len(times)
    
    
    # validasi jumlah ketersediaan data
    if times_size < 0:
        context = {
            'atk':atk,
            'tahun_awal': tahun_awal,
            'tahun_akhir': tahun_akhir,
            'list_tahun': list_tahun,
            'msg':"Data pada ATK belum siap untuk diprediksi"
        }
    elif times_size <= 3:
       context = {
           'atk':atk,
           'tahun_awal': tahun_awal,
            'tahun_akhir': tahun_akhir,
           'list_tahun': list_tahun,
            'msg':"Data pada ATK belum siap untuk diprediksi"
        }
    else:
        train_size = int(math.ceil(0.8 * times_size))
        test_size = int(math.ceil(0.2 * times_size))

        # ubah tipe data value yg akan diprediksi ke pandas series
        values_array = np.array(values)
        ser = pd.Series(values_array)

        train, test = temporal_train_test_split(ser, test_size=test_size)
        print(train, test)
        
        # ! BUAT DECISION PEMILIHAN METODE PREDIKSI
        # check if data is constant
        if max(values) == min(values):
            forecaster_stok = ExponentialSmoothing(optimized=True) 
        else:
            # check stationarity in data with some degree of variability.
            check_stat = adfuller(values)
            print('ADF Statistic: %f ' % check_stat[0])
            print('p-value: %f ' % check_stat[1])
            print('Critical Values:')
            for key, value in check_stat[4].items():
                print('\t%s: %.3f' % (key, value))
        
            has_trend = False
            has_season = False
            has_resid = False
            # jika data tidak stasioner
            print('Data tidak stasioner')
            
            # DECOMPOSE
            # additive decompose
            add_dec = seasonal_decompose(ser, model='additive', period=2)
            print(add_dec.seasonal, add_dec.trend, add_dec.resid, add_dec.observed)
            # Check if the data has a clear trend
            trend = add_dec.trend
            if trend.is_monotonic_increasing or trend.is_monotonic_decreasing:
                print("The data has a trend.")
                has_trend = True
            else:
                print("The data does not have a clear trend.")

            # Check if the data has significant seasonality
            seasonality = add_dec.seasonal
            if seasonality.var() != 0:
                print("The data has seasonality.")
                has_season = True
            else:
                print("The data does not have significant seasonality.")
                
            residual = add_dec.resid
            if residual.sum() != 0:
                has_resid = True
        
            if has_trend and has_season:
                # holt winter exponential smoothing
                forecaster_stok = ExponentialSmoothing(trend="add", seasonal="add", optimized=True, sp=2)
            elif has_trend: 
                # double exponential smoothing
                forecaster_stok = ExponentialSmoothing(trend="add", optimized=True)
            elif has_season:
                # season with no trend
                forecaster_stok = ExponentialSmoothing(seasonal="add", optimized=True, sp=2)
            else:
                forecaster_stok = ExponentialSmoothing(trend="add", damped_trend=True, optimized=True)
                
                
        forecaster_stok.fit(train)
        jml_tahun_pred = 2
        fh = np.arange(1,len(test) + 1 + jml_tahun_pred)
        fh2 = np.arange(1,len(test) + 1)
        
        # prediksi
        pred = forecaster_stok.predict(fh=fh)
        # prediksi akurasi
        pred2 = forecaster_stok.predict(fh=fh2)
        # cek akurasi
        mape=mean_absolute_percentage_error(test, pred2, symmetric=True)
        smape=mean_absolute_percentage_error(test, pred2, symmetric=True)
    
        print()
        print(f"MAPE: {mape}, SMAPE: {smape}")
        # ubah semua type hasil ke list
        train_list, test_list, pred_list = train.to_list(), test.to_list(), pred.to_list()
        print(train_list, test_list, pred_list, sep='\n')
        
        # cari nilai x pada diagram untuk 3 diagram garis (test, train, pred)
        x_train_list = times[:train_size+1]
        x_test_list = times[-test_size:]
        x_pred_list = times[-test_size:] + [*range(times[-1]+1, times[-1]+jml_tahun_pred)]
        
        # diagram
        fig = go.Figure()
        trace_train = go.Scatter(
            x=x_train_list,
            y=train_list + test_list[:1],
            mode='markers+lines',
            name='Data Latih',
            showlegend=True,
        )
        trace_test = go.Scatter(
            x=x_test_list,
            y=test_list,
            mode='markers+lines',
            name='Data Uji',
            showlegend=True,
        )
        trace_pred = go.Scatter(
            x=x_pred_list,
            y=pred_list,
            mode='markers+lines',
            name='Hasil Prediksi',
            showlegend=True,
        )
        fig.add_trace(trace_train)
        fig.add_trace(trace_test)
        fig.add_trace(trace_pred)
        
        fig.update_traces(hovertemplate=None)
        fig.update_layout(hovermode="x unified")
        fig.update_layout(
        xaxis_title="Tahun", yaxis_title="Jumlah Kegunaan")
        chart = fig.to_html
        
        context = {
            'tahun_awal': tahun_awal,
            'tahun_akhir': tahun_akhir,
            'list_tahun': list_tahun,
            'chart': chart,
            'mape': mape,
            'mape_persen': (1-mape),
            'smape': smape,
            'smape_persen': (1-smape),
            'atk':atk,
            'pred':round(pred_list.pop()),
            'test':test_list.pop(),
        }
    return render(request, 'atk/forecast_unit.html', context)

def forecast(request):  

    # times_size = len(times)
    # print(times_size)
    # values_array = np.array(values)
    # ser = pd.Series(values_array)
    # print(ser)

    # train, test = temporal_train_test_split(ser, test_size=1)
    # print(train, test)
    # forecaster_stok = NaiveForecaster(strategy='last')
    # forecaster_stok.fit(train)
    # fh = np.arange(1,len(test) + 1)
    # pred = forecaster_stok.predict(fh=fh)
    # print(pred)

    airline = datasets.load_airline()
    print(airline, type(airline) ,sep='\n')
    y_train, y_test = temporal_train_test_split(airline, test_size=36)

    forecaster = ExponentialSmoothing(trend='add', seasonal='multiplicative', sp=12)
    forecaster.fit(y_train)

    fh = np.arange(1,len(y_test) + 1)
    y_pred = forecaster.predict(fh=fh)

    print(y_pred)

    y_train_list, y_test_list, y_pred_list = y_train.to_list(), y_test.to_list(), y_pred.to_list()
    print(y_train_list, y_test_list, y_pred_list, sep='\n')
    x = [*range(1,137)]
    print(x)
    # check akurasi
    mape=mean_absolute_percentage_error(y_test, y_pred, symmetric=False)
    smape=mean_absolute_percentage_error(y_test, y_pred, symmetric=True)
    
    fig = go.Figure()
    trace_train = go.Scatter(
        x=[*range(1,101)],
        y=y_train_list,
        mode='lines',
        name='Data Latih',
        showlegend=True,
    )
    trace_test = go.Scatter(
        x=[*range(100,137)],
        y=y_test_list,
        mode='lines',
        name='Data Uji',
        showlegend=True,
    )
    trace_pred = go.Scatter(
        x=[*range(100,137)],
        y=y_pred_list,
        mode='lines',
        name='Hasil Prediksi',
        showlegend=True,
    )
    fig.add_trace(trace_train)
    fig.add_trace(trace_test)
    fig.add_trace(trace_pred)
    
    fig.update_traces(hovertemplate=None)
    fig.update_layout(hovermode="x unified")
    
    chart = fig.to_html

    context = {'chart': chart,
               'mape': mape,
               'smape': smape,
               }
    return render(request, 'atk/forecast.html', context)



    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="users.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Total Pengajuan') # this will make a sheet named Users Data

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['Alat Tulis', 'Jumlah Diajukan', 'Satuan', 'Harga Satuan', 'Total Biaya']

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style) # at 0 row 0 column 

    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()
    
    tahun = datetime.datetime.now().year
    jadwal = Jadwal.objects.filter(tahun=tahun)[:1].first()

    rows = total_pengajuan.objects.filter(jadwal=jadwal).values_list('atk', 'jumlah', 'satuan', 'atk__satuan', 'harga__harga', 'total_dana')
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num], font_style)

    wb.save(response)

    return response


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
