from django.contrib import messages
from django.forms import modelformset_factory
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from .models import SolicitudArriendo, Inmueble, Region, Comuna
from .forms import CustomUserChangeForm, RegistroUsuarioForm, SolicitudArriendoForm, InmuebleForm




def home(request):
    inmuebles = Inmueble.objects.all()
    return render(request, 'index.html',{'inmuebles': inmuebles})



@login_required
def detalle_inmueble(request, id):
    inmueble = Inmueble.objects.get (pk=id)
    return render(request,'detalle_inmueble.html',{'inmueble':inmueble})



def registro_usuario(request):
    if request.method == 'POST':
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            usuario = form.save(commit=False)
            password = form.cleaned_data['password']
            usuario.set_password(password)
            usuario.save()
            # Autenticar al usuario después del registro
            usuario_autenticado = authenticate(username=usuario.username, password=password)
            if usuario_autenticado is not None:
                login(request, usuario_autenticado)
                return redirect('home')
    else:
        form = RegistroUsuarioForm()
    return render(request, 'registro_usuario.html', {'form': form})


@login_required
def generar_solicitud_arriendo(request, id):
    # Obtener el inmueble por su ID
    inmueble = get_object_or_404(Inmueble, pk=id)

    # Verificar si el usuario está autenticado y es un arrendatario
    if request.user.is_authenticated and request.user.tipo_usuario == 'arrendatario':
        if request.method == 'POST':
            #print(request.POST)
            form = SolicitudArriendoForm(request.POST)
            if form.is_valid():
                solicitud = form.save(commit=False)
                solicitud.arrendatario = request.user  # Asignar el usuario arrendatario
                solicitud.inmueble = inmueble
                solicitud.save()
                return redirect('detalle', id=inmueble.id)
        else:
            # Inicializar el formulario con el inmueble correspondiente
            form = SolicitudArriendoForm(initial={'inmueble': inmueble})
        return render(request, 'generar_solicitud_arriendo.html', {'form': form, 'inmueble': inmueble})
    else:
        return redirect('index')


@login_required
def solicitudes_arrendador(request):
    # Verificar si el usuario es un arrendador
    if request.user.usuario.tipo_usuario == 'arrendador':
        # Obtener todas las solicitudes recibidas por el arrendador
        solicitudes = SolicitudArriendo.objects.filter(inmueble__propietario=request.user)
        return render(request, 'solicitudes_arrendador.html', {'solicitudes': solicitudes})
    else:
        # Redirigir a otra página si el usuario no es un arrendador
        return redirect('index')


@login_required
def crear_inmueble(request):
    regiones = Region.objects.all()
    comunas = Comuna.objects.all()

    if request.method == 'POST':
        form = InmuebleForm(request.POST, request.FILES)
        if form.is_valid():
            inmueble = form.save(commit=False)
            inmueble.propietario = request.user
            inmueble.save()
            return redirect('dashboard')
    else:
        form = InmuebleForm()

    return render(request, 'alta_inmueble.html', {'form': form, 'regiones': regiones, 'comunas': comunas})


@login_required
def actualizar_inmueble(request, id):
    inmueble = get_object_or_404(Inmueble, pk=id)

    if request.method == 'POST':
        form = InmuebleForm(request.POST, request.FILES, instance=inmueble)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = InmuebleForm(instance=inmueble)

    comunas = Comuna.objects.all()
    regiones = Region.objects.all()

    return render(request, 'editar_inmueble.html',{'form':form, 'comunas':comunas, 'regiones':regiones})


@login_required
def eliminar_inmueble(request, id):
    inmueble = get_object_or_404(Inmueble, pk=id)
    if request.method == 'POST':
        inmueble.delete()
        return redirect('dashboard')
    else:
        return render(request,'eliminar_inmueble.html', {'inmueble':inmueble} )


@login_required
def dashboard(request):
    if request.user.tipo_usuario == 'arrendatario':
        solicitudes = SolicitudArriendo.objects.filter(arrendatario=request.user)
        regiones = Region.objects.all()
        comunas = Comuna.objects.all()
        region_id = request.GET.get('region')
        comuna_id = request.GET.get('comuna')
        inmuebles = Inmueble.objects.filter(disponible=True)
        if region_id and region_id != '0':
            inmuebles = inmuebles.filter(comuna__region_id=region_id)
        if comuna_id:
            inmuebles = inmuebles.filter(comuna=comuna_id)

        return render(request, 'dashboard_arrendatario.html', {'solicitudes': solicitudes, 'regiones': regiones, 'comunas': comunas, 'inmuebles': inmuebles})

    elif request.user.tipo_usuario == 'arrendador':
        # Obtener las solicitudes recibidas por el arrendador
        solicitudes_recibidas = SolicitudArriendo.objects.filter(inmueble__propietario=request.user, estado='pendiente')
        # Obtener los inmuebles del arrendador
        inmuebles = Inmueble.objects.filter(propietario=request.user)
        return render(request, 'dashboard_arrendador.html', {'solicitudes_recibidas': solicitudes_recibidas, 'inmuebles': inmuebles})


@login_required
def actualizar_usuario(request):
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, '¡Los datos del usuario han sido actualizados!')
            return redirect('dashboard')
    else:
        form = CustomUserChangeForm(instance=request.user)
    return render(request, 'perfil.html', {'form': form})


@login_required
def cambiar_estado_solicitud(request, solicitud_id):
    solicitud = get_object_or_404(SolicitudArriendo, pk=solicitud_id)
    if solicitud.inmueble.propietario == request.user:
        if request.method == 'POST':
            nuevo_estado = request.POST.get('nuevo_estado')
            solicitud.estado = nuevo_estado
            solicitud.save()
            inmueble = Inmueble.objects.get(pk=solicitud.inmueble.id)
            inmueble.disponible = False
            inmueble.save()
    return redirect('dashboard')

@login_required
def cancelar_solicitud(request, solicitud_id):
    solicitud = get_object_or_404(SolicitudArriendo, pk=solicitud_id)
    if request.method == 'POST':
        inmueble = Inmueble.objects.get(pk=solicitud.inmueble.id)
        inmueble.disponible = True
        inmueble.save()
        solicitud.delete()
    return redirect('dashboard')

def comunas(request):
    region_id = request.GET.get('region')
    comunas = Comuna.objects.filter(region_id=region_id)
    for comuna in comunas:
        data = f"<option value='{comuna.id}'>{comuna.nombre}</option>"
    return data