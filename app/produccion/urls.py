from django.urls import path
from . import views

urlpatterns = [
    path('lista/', views.produccion_lista_view, name='produccion_lista'),
]
