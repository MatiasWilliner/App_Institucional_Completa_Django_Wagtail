from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('app_novedades.urls')),  
    path('', include('app_general.urls')),
    path('', include('app_trabajo.urls')),  
    path('', include('app_contacto.urls')), 
]

