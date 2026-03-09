from rest_framework import generics
from .models import InventarioBodega
from .serializers import InventarioBodegaSerializer

class InventarioAPIView(generics.ListAPIView):
    queryset = InventarioBodega.objects.select_related('item', 'bodega').all()
    serializer_class = InventarioBodegaSerializer
