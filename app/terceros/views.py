from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Tercero
from .forms import TerceroForm

@login_required
def terceros_lista_view(request):
    terceros = Tercero.objects.all().order_by('razon_social', 'nombres')
    return render(request, 'terceros/lista_terceros.html', {'terceros': terceros})

@login_required
def tercero_crear_view(request):
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest' or 'ajax' in request.GET
    if request.method == 'POST':
        form = TerceroForm(request.POST)
        if form.is_valid():
            tercero = form.save()
            if is_ajax:
                return JsonResponse({'success': True, 'id': tercero.id, 'text': str(tercero)})
            messages.success(request, f'Tercero {tercero} creado exitosamente.')
            return redirect('terceros_lista')
    else:
        form = TerceroForm()
    
    return render(request, 'terceros/form_tercero.html', {'form': form, 'titulo': 'Nuevo Tercero', 'is_ajax': is_ajax})

@login_required
def tercero_editar_view(request, tercero_id):
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest' or 'ajax' in request.GET
    tercero = get_object_or_404(Tercero, id=tercero_id)
    if request.method == 'POST':
        form = TerceroForm(request.POST, instance=tercero)
        if form.is_valid():
            form.save()
            if is_ajax:
                return JsonResponse({'success': True, 'id': tercero.id, 'text': str(tercero)})
            messages.success(request, f'Tercero actualizado exitosamente.')
            return redirect('terceros_lista')
    else:
        form = TerceroForm(instance=tercero)
    
    return render(request, 'terceros/form_tercero.html', {'form': form, 'titulo': f'Editar Tercero: {tercero}', 'is_ajax': is_ajax})

@login_required
def tercero_ver_view(request, tercero_id):
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest' or 'ajax' in request.GET
    tercero = get_object_or_404(Tercero, id=tercero_id)
    form = TerceroForm(instance=tercero)
    return render(request, 'terceros/form_tercero.html', {'form': form, 'titulo': f'Ver Tercero: {tercero}', 'is_ajax': is_ajax})
