from rest_framework import generics
from .models import InventarioBodega, Item
from .serializers import InventarioBodegaSerializer

class InventarioAPIView(generics.ListAPIView):
    queryset = InventarioBodega.objects.select_related('item', 'bodega').all()
    serializer_class = InventarioBodegaSerializer

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import ItemForm

@login_required
def inventario_lista_view(request):
    saldos = InventarioBodega.objects.select_related('item', 'bodega', 'item__unidad_medida_base').all()
    return render(request, 'inventario/lista_inventario.html', {'saldos': saldos})

@login_required
def items_lista_view(request):
    items = Item.objects.select_related('categoria', 'unidad_medida_base').all()
    return render(request, 'inventario/lista_items.html', {'items': items})

@login_required
def item_crear_view(request):
    if request.method == 'POST':
        form = ItemForm(request.POST)
        if form.is_valid():
            item = form.save()
            messages.success(request, f'Ítem {item} creado exitosamente.')
            return redirect('items_lista')
    else:
        form = ItemForm()
    
    return render(request, 'inventario/form_item.html', {'form': form, 'titulo': 'Nuevo Ítem'})

@login_required
def item_editar_view(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    if request.method == 'POST':
        form = ItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, f'Ítem actualizado exitosamente.')
            return redirect('items_lista')
    else:
        form = ItemForm(instance=item)
    
    return render(request, 'inventario/form_item.html', {'form': form, 'titulo': f'Editar Ítem: {item}'})
