from django.shortcuts import render

from app_novedades.models import NoticiaPage, EventoPage

def home(request):
    noticias=NoticiaPage.objects.all()[:3]
    eventos=EventoPage.objects.all()[:3] 
    return render(request, 'home.html', {'noticias': noticias, 'eventos': eventos})

def sobre_nosotros(request):
    return render(request, 'sobre_nosotros.html')