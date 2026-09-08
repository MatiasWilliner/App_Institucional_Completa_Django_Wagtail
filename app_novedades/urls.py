from django.urls import path

from . import views


app_name = 'app_novedades'  # para usar {% url 'app_principal:ruta_ejemplo' %}

urlpatterns = [
    path('eventos_json', views.eventos_json, name='eventos_json'),
]