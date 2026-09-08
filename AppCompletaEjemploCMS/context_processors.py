from app_novedades.models import EventosIndexPage, NoticiasIndexPage
from app_trabajo.models import AreasIndexPage, TalleresIndexPage

def navegacion(request):
    return {
        'pagina_eventos': EventosIndexPage.objects.live().first(),
        'pagina_noticias': NoticiasIndexPage.objects.live().first(),
        'pagina_areas': AreasIndexPage.objects.live().first(),
        'pagina_talleres': TalleresIndexPage.objects.live().first(),
    }