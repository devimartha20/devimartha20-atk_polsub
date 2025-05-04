from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.db.models import *
from .models import *
from django.forms import Form, ModelForm, DateField, widgets
from django.core.exceptions import ValidationError

class loginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control form-control-lg",
                "placeholder": "Username",
                "aria-label": "Username"
            }
        )
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control form-control-lg",
                "placeholder": "Password",
                "aria-label": "Password"
            }
        )
    )

class addUserForm(UserCreationForm):
    email = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control form-control-lg",
                "placeholder": "Email",
                "aria-label": "Email"
            }
        )
    )
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control form-control-lg",
                "placeholder": "Username",
                "aria-label": "Username"
            }
        )
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control form-control-lg",
                "placeholder": "Password",
                "aria-label": "Password"
            }
        )
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control form-control-lg",
                "placeholder": "Password",
                "aria-label": "Password"
            }
        )
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'first_name', 'last_name' , 'is_admin', 'is_pimpinanunit', 'is_wadir', 'is_adminunit')
        
class DateInput(forms.DateInput):
    input_type = 'date'
    
#WADIR
class formJadwal(forms.ModelForm):
    
    YEAR_CHOICES = []
    for r in range(2023, (datetime.datetime.now().year+2)):
        YEAR_CHOICES.append((r,r)) 
    
    def clean(self):
        cleaned_data = super(formJadwal, self).clean()
        tahun = cleaned_data.get("tahun")
        pengajuan_mulai = cleaned_data.get("pengajuan_mulai")
        pengajuan_selesai = cleaned_data.get("pengajuan_selesai")

        if tahun and pengajuan_mulai and pengajuan_selesai:
            if int(pengajuan_mulai.strftime('%Y')) != tahun:
                raise ValidationError('Tanggal pembukaan tidak sesuai dengan periode tahun yang diinput')
            if pengajuan_selesai <= pengajuan_mulai:
                raise ValidationError('Range tanggal pembukaan dan Penutupan tidak valid!')
    class Meta:
        model = Jadwal
        fields = '__all__'
        exclude = ['status']
        labels = {'tahun': 'Tahun', 
                  'pengajuan_mulai': 'Tanggal Dibuka',
                  'pengajuan_selesai': 'Tanggal Ditutup'
                }
        widgets = {
            'tahun': forms.Select(attrs={"class": "form-control form-control-lg",
                                                 "type": "number"}),
            'pengajuan_mulai': forms.DateInput(attrs={"class": "form-control form-control-lg",
                                                 "type": "date"}),
            'pengajuan_selesai': forms.DateInput(attrs={"class": "form-control form-control-lg",
                                                 "type": "date"}),
            'keterangan': forms.TextInput(attrs={"class": "form-control form-control-lg",
                                                 "type": "text"})
        }
        input_formats = {
            'pengajuan_mulai': ['%d/%m/%Y']
        }
        
    
class formATK(forms.ModelForm):
    class Meta:
        model= Barang_ATK
        fields = '__all__'     
        exclude = ['status'] 
        labels = {'atk': 'Nama ATK', 
                  'spesifikasi': 'Spesifikasi',
                    'kategori': 'Kategori',
                  'satuan': 'Satuan',
                  'jumlah_per_satuan': 'Isi per Satuan',
                  'harga': 'Harga',
                  'link': 'Referensi',
                  'img': 'Gambar',
                  'keterangan': 'keterangan'
                  
                }
        widgets = {
            'atk': forms.TextInput(attrs={"class": "form-control form-control-lg",
                                                 "type": "text", "required":"required"}),
            'spesifikasi': forms.TextInput(attrs={"class": "form-control form-control-lg",
                                                 "type": "text", "required":"required"}),
            'link': forms.TextInput(attrs={"class": "form-control form-control-lg",
                                                 "type": "text", "required":"required"}),
            'jumlah_per_satuan': forms.NumberInput(attrs={"class": "form-control form-control-lg",
                                                 "type": "number", "min": 0 , "required":"required"}),
            'harga': forms.NumberInput(attrs={"class": "form-control form-control-lg",
                                                 "type": "number", "min": 0, "required":"required"}),
            'kategori': forms.Select(attrs={"class": "form-control form-control-lg", "required":"required"}),
            'satuan': forms.Select(attrs={"class": "form-control form-control-lg","required":"required"}),
            'keterangan': forms.TextInput(attrs={"class": "form-control form-control-lg",
                                                 "type": "text"})
        } 
        
class formPengumpulanPengajuan(forms.ModelForm):
    class Meta:
        model= pengumpulanPengajuan
        fields = '__all__'
        
class formIsiPengajuan(forms.ModelForm):
    atk = forms.ModelChoiceField(queryset=Barang_ATK.objects.all(), empty_label=None,
        widget=forms.Select(
            attrs={
                "class": "form-select",
                "placeholder": "Pilih ATK",

            }
        )
    )
    
    jumlah = forms.CharField(
        widget=forms.NumberInput(
            attrs={
                "class": "form-control form-control-lg",
                "placeholder": "Jumlah",
                "min": 1,
            }
        )
    )
    keterangan = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control form-control-lg",
                "placeholder": "Keterangan",

            }
        )
    )
    def clean(self):
        cleaned_data = super(formIsiPengajuan, self).clean()
        keterangan = cleaned_data.get("keterangan")
        atk = cleaned_data.get("atk")
        jumlah = cleaned_data.get("jumlah")
        atk_instance = Barang_ATK.objects.get(atk=atk)
        atk_exist = Isi_pengajuan.objects.filter(pengajuan=self.id_pengajuan, atk=atk_instance)
        if atk and jumlah and keterangan:
            if int(jumlah) < 0:
                raise ValidationError('Jumlah harus lebih dari 0!')
            # if atk_exist is not None:
            #     raise ValidationError('ATK yang sama telah diinput')
            
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        self.id_pengajuan = kwargs.pop("id_pengajuan", None)
        super(formIsiPengajuan, self).__init__(*args, **kwargs)
    
    
    class Meta:
        model = Isi_pengajuan
        fields = '__all__'
        exclude = ["rekomendasi", "pengajuan"]
        labels = {'atk': 'Pilih Barang', 
                  'jumlah': 'Jumlah Diajukan',
                  'keterangan': 'Keterangan'
                }

class formStokKeluar(forms.ModelForm):
    class Meta:
        model=PenggunaanStok
        fields = '__all__'
        exclude = ['unit']
        widgets = {
            'atk': forms.Select(attrs={"class": "form-control form-control-lg",
                                                 "type": "text"}),
            
            'jumlah': forms.NumberInput(attrs={"class": "form-control form-control-lg",
                                                 "type": "number",
                                                 "min": 1
                                                 }),
            'penerima': forms.Select(attrs={"class": "form-control form-control-lg",
                                                 "type": "text",
                                                 }),
            'guna': forms.Select(attrs={"class": "form-control form-control-lg",
                                                 "type": "text"
                                                 }),
            'keterangan': forms.TextInput(attrs={"class": "form-control form-control-lg",
                                                 "type": "text"
                                                 }),
            'tanggal': forms.DateInput(attrs={"class": "form-control form-control-lg",
                                                 "type": "date", "required":"required"}),
        }
        
    def clean(self):
        cleaned_data = super(formStokKeluar, self).clean()
        
        tahun = datetime.datetime.now().year
        
        atk = cleaned_data.get("atk")
        jumlah = cleaned_data.get("jumlah")
        tanggal = cleaned_data.get("tanggal")
        atk_instance = Barang_ATK.objects.get(atk=atk)
        max_jumlah = StokATK.objects.filter(unit=self.request.user.unit, atk=atk_instance).first()
        print(atk, max_jumlah)
        print(type(tanggal.strftime('%Y')), type(tahun))
        if tanggal and jumlah:
            if jumlah > max_jumlah.jumlah:
                print('error jumlah')
                raise ValidationError('Jumlah tidak boleh melebihi stok tersisa')
            if int(tanggal.strftime('%Y')) != tahun:
                print('error tahun')
                print(tanggal.strftime('%Y'), tahun)
                raise ValidationError(f'Anda hanya dapat mencatat stok untuk tahun {tahun}')
                
            
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        user_id = self.request.user.id
        super(formStokKeluar, self).__init__(*args, **kwargs)
        if user_id is not None:
            user = User.objects.filter(id=user_id).first()
            self.fields['atk'].queryset = StokATK.objects.filter(unit=user.unit)
            self.fields['guna'].queryset = guna.objects.filter(unit=user.unit)
        else:
            self.fields['atk'].queryset = StokATK.objects.none()
            self.fields['guna'].queryset = guna.objects.none()
    
class formStokMasuk(forms.ModelForm):
    class Meta:
        model=PenambahanStok
        fields = '__all__'
        exclude = ['unit']
        widgets = {
            'atk': forms.Select(attrs={"class": "form-control form-control-lg",
                                                 "type": "text"}),
            
            'jumlah': forms.NumberInput(attrs={"class": "form-control form-control-lg",
                                                 "type": "number",
                                                 
                                                 }),
            'keterangan': forms.TextInput(attrs={"class": "form-control form-control-lg",
                                                 "type": "text"
                                                 }),
            'tanggal': forms.DateInput(attrs={"class": "form-control form-control-lg",
                                                 "type": "date"}),
        }

class formGuna(forms.ModelForm):
    class Meta:
        model=guna
        fields = '__all__'
        exclude = ['unit']
        widgets = {
            'kegunaan': forms.TextInput(attrs={"class": "form-control form-control-lg",
                                                 "type": "text"
                                                 }),
            'keterangan': forms.TextInput(attrs={"class": "form-control form-control-lg",
                                                 "type": "text"
                                                 }),
        }

class formPerbaikan(forms.ModelForm):
    class Meta:
        model=PerbaikanPengajuan
        fields='__all__'
        exclude = ['pengajuan']
        widgets = {
            'keterangan': forms.TextInput(attrs={"class": "form-control form-control-lg",
                                                 "type": "text"
                                                 }),
            
        }
        
class atkForm(forms.ModelForm):
    class Meta:
        model=Barang_ATK
        fields='__all__'
        exclude= ['status', 'satuan']
        widgets = {
            'atk':forms.TextInput(attrs={"class": "form-control form-control-lg",
                                                 "type": "text"
                                                 }),
           ' keterangan':forms.TextInput(attrs={"class": "form-control form-control-lg",
                                                 "type": "text"
                                                 }),
            'kategori':forms.Select(attrs={"class": "form-control form-control-lg",
                                                 "type": "text"}),
            'jumlah_per_satuan': forms.NumberInput(attrs={"class": "form-control form-control-lg",
                                                 "type": "number"}),
            
            
        }