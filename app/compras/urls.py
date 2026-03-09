from django.urls import path
from . import views

urlpatterns = [
    path('lista/', views.compras_lista_view, name='compras_lista'),
]
