from django.urls import path

from . import views


app_name = 'app_contacto'  # para usar {% url 'app_principal:ruta_ejemplo' %}

urlpatterns = [
    path('contacto', views.contacto, name='contacto'),
]