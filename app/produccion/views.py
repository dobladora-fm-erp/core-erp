from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import OrdenProduccion

@login_required
def produccion_lista_view(request):
    ordenes = OrdenProduccion.objects.prefetch_related('insumos__item', 'productos__item').all().order_by('-fecha_creacion')
    return render(request, 'produccion/lista_produccion.html', {'ordenes': ordenes})
