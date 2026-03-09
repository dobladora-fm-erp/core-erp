from django.urls import path
from . import views

urlpatterns = [
    path('lista/', views.tesoreria_lista_view, name='tesoreria_lista'),
]
