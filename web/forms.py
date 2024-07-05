from django import forms
from .models import Comuna, Usuario, SolicitudArriendo,Inmueble
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.models import User


class RegistroUsuarioForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['username', 'password', 'nombres', 'apellidos', 'rut', 'direccion', 'telefono', 'correo_electronico', 'tipo_usuario']
        widgets = {
            'password': forms.PasswordInput(),
        }


class InmuebleForm(forms.ModelForm):
    class Meta:
        model = Inmueble
        exclude = ('propietario',)  # Excluimos el campo 'propietario' del formulario


class SolicitudArriendoForm(forms.ModelForm):
    class Meta:
        model = SolicitudArriendo
        fields = ['id','inmueble', 'mensaje', 'estado']


class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = Usuario
        fields = ['nombres', 'apellidos', 'correo_electronico']
