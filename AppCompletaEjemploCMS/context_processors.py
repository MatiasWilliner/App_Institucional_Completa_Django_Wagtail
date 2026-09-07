from app_novedades.models import EventosIndexPage, NoticiasIndexPage

def navegacion(request):
    return {
        'pagina_eventos': EventosIndexPage.objects.live().first(),
        'pagina_noticias': NoticiasIndexPage.objects.live().first()
    }