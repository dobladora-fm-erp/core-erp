from django.urls import path
from . import views

urlpatterns = [
    path('lista/', views.terceros_lista_view, name='terceros_lista'),
    path('crear/', views.tercero_crear_view, name='tercero_crear'),
    path('<int:tercero_id>/editar/', views.tercero_editar_view, name='tercero_editar'),
    path('<int:tercero_id>/ver/', views.tercero_ver_view, name='tercero_ver'),
]
