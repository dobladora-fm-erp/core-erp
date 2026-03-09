from django.urls import path
from . import views

urlpatterns = [
    path('lista/', views.inventario_lista_view, name='inventario_lista'),
]
