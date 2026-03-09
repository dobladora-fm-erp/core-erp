from django.urls import path
from . import views

urlpatterns = [
    path('lista/', views.ventas_lista_view, name='ventas_lista'),
]
