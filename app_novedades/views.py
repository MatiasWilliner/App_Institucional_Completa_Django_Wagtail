from datetime import datetime

from django.http import JsonResponse
from django.shortcuts import render

from app_novedades.models import EventoPage

def eventos_json(request):
    eventos=EventoPage.objects.all()

    data = []

    for evento in eventos:
        fecha_hora = datetime.combine(evento.fecha,evento.hora)
        data.append({
            "title": evento.title,
            "start": fecha_hora.isoformat(),
            "backgroundColor": evento.categoria.color,
            "borderColor": evento.categoria.color,
        })

    return JsonResponse(data, safe=False)