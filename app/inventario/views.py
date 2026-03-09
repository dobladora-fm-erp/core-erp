from rest_framework import generics
from .models import InventarioBodega
from .serializers import InventarioBodegaSerializer

class InventarioAPIView(generics.ListAPIView):
    queryset = InventarioBodega.objects.select_related('item', 'bodega').all()
    serializer_class = InventarioBodegaSerializer

from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def inventario_lista_view(request):
    saldos = InventarioBodega.objects.select_related('item', 'bodega', 'item__unidad_medida_base').all()
    return render(request, 'inventario/lista_inventario.html', {'saldos': saldos})
