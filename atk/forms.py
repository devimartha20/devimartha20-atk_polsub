from django import forms
from django.contrib.auth.forms import UserCreationForm
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
        cleaned_data = super().clean()
        tahun = cleaned_data.get("tahun")
        pengajuan_mulai = cleaned_data.get("pengajuan_mulai")
        pengajuan_selesai = cleaned_data.get("pengajuan_selesai")

        if tahun and pengajuan_mulai and pengajuan_selesai:
            # if pengajuan_mulai.strftime('%Y') != tahun:
            #     raise ValidationError('Tanggal pembukaan tidak sesuai dengan periode tahun yang diinput')
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
                                                 "type": "date"}),
        }
    def __init__(self, *args, **kwargs):
        user_id = kwargs.pop('user_id', None)
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