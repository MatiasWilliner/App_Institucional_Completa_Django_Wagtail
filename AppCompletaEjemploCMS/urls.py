from django.contrib import admin
from django.urls import include, path
from django.conf.urls.static import static
from django.conf import settings

from wagtail import urls as wagtail_urls
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.documents import urls as wagtaildocs_urls

urlpatterns = [
    # Urls de Django
    path('django-admin/', admin.site.urls),
    path('', include('app_novedades.urls')),  
    path('', include('app_general.urls')),
    path('', include('app_trabajo.urls')),  
    path('', include('app_contacto.urls')), 
    # Urls de Wagtail
    path("admin/", include(wagtailadmin_urls)),
    path("documents/", include(wagtaildocs_urls)),
    # Wagtail al final
    path("", include(wagtail_urls)),
]
if settings.DEBUG:
    urlpatterns += static(
        settings.STATIC_URL,
        document_root=settings.STATIC_ROOT
    )

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )
