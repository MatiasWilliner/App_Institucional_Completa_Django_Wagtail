from datetime import datetime, date
import pytest

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from wagtail.models import Site

from AppCompletaEjemploCMS.factories import AreasIndexFactory, CategoriaEventoFactory, CategoriaNoticiaFactory, EventoFactory, EventosIndexFactory, NoticiaFactory, NoticiasIndexFactory, TalleresIndexFactory
from app_novedades.models import EventoPage, NoticiaPage





######################################################### Fixtures #########################################################




# Fixture para creación de páginas índice de visitantes
@pytest.fixture()
def paginas_indice_visitantes():
    # Obtenemos la página raíz del sitio por defecto 
    # y creamos las páginas índice de visitantes como hijas de la misma
    root = Site.objects.get(is_default_site=True).root_page
    AreasIndexFactory.create(parent=root)
    TalleresIndexFactory.create(parent=root)
    noticias=NoticiasIndexFactory.create(parent=root)
    eventos=EventosIndexFactory.create(parent=root)
    return {
        "noticias": noticias,
        "eventos":eventos
    }




######################################################### Tests para lo relacionado con las noticias #########################################################




# Test para probar la página de noticias sin noticias cargadas
@pytest.mark.django_db
def test_pagina_noticias_sin_noticias(client, paginas_indice_visitantes):
    fixture_data=paginas_indice_visitantes
    # Realiza get a la ruta 
    pagina_noticias=fixture_data["noticias"]
    response = client.get(pagina_noticias.url)
    # Comprueba que se obtenga el código esperado
    assert response.status_code == 200
    # Comprueba que se obtenga la plantilla esperada
    assert "app_novedades/noticias_index_page.html" in [t.name for t in response.templates]
    # Comprueba que no había datos cargados en la base de datos
    assert NoticiaPage.objects.count()==0
    # Comprueba que se obtengan listas vacías
    assert list(response.context["noticias_destacadas"]) == []
    assert list(response.context["noticias"]) == []


# Test para probar la página de noticias con noticias cargadas
@pytest.mark.django_db
def test_pagina_noticias_con_muchas_noticias(client, paginas_indice_visitantes):
    fixture_data=paginas_indice_visitantes
    # Carga de datos en la base de datos
    noticias=NoticiaFactory.create_batch(6, parent=fixture_data["noticias"])
    # Realiza get a la ruta
    pagina_noticias=fixture_data["noticias"]
    response = client.get(pagina_noticias.url)
    # Comprueba que se obtenga el código esperado
    assert response.status_code == 200
    # Comprueba que se obtenga la plantilla esperada
    assert "app_novedades/noticias_index_page.html" in [t.name for t in response.templates]
    # Comprueba que había datos cargados en la base de datos
    assert NoticiaPage.objects.count()==6
    # Ordena las noticias por fecha de publicación y luego por ID en orden descendente para obtener las últimas noticias
    # porque asi esta en el modelo, y se hace para que el test sea más robusto y no dependa del orden de creación de las noticias
    noticias_ordenadas = sorted(noticias, key=lambda noticia: (noticia.first_published_at, noticia.id), reverse=True)
    # Comprueba que se obtengan los datos correctos en la lista que corresponde a las últimas noticias cargadas
    assert list(response.context["noticias_destacadas"])==noticias_ordenadas[:3]
    # Comprueba que se obtengan los datos correctos en la lista que corresponde al resto de noticias 
    # teniendo en cuenta la paginación (2 por página)
    assert list(response.context["noticias"])==noticias_ordenadas[3:5]


# Test para probar la página de noticias con noticias cargadas
@pytest.mark.django_db
def test_pagina_noticias_con_ultimas_noticias(client, paginas_indice_visitantes):
    fixture_data=paginas_indice_visitantes
    # Carga de datos en la base de datos
    noticia=NoticiaFactory.create(parent=fixture_data["noticias"])
    # Realiza get a la ruta
    pagina_noticias=fixture_data["noticias"]
    response = client.get(pagina_noticias.url)
    # Comprueba que se obtenga el código esperado
    assert response.status_code == 200
    # Comprueba que se obtenga la plantilla esperada
    assert "app_novedades/noticias_index_page.html" in [t.name for t in response.templates]
    # Comprueba que había datos cargados en la base de datos
    assert NoticiaPage.objects.count()==1
    # Comprueba que se obtengan los datos correctos en las listas del contexto
    assert list(response.context["noticias_destacadas"])==[noticia]
    assert list(response.context["noticias"])==[]


# Test para probar la página de noticias con noticias cargadas y filtrado por categoría
@pytest.mark.django_db
def test_pagina_noticias_filtro_categorias(client, paginas_indice_visitantes):
    fixture_data=paginas_indice_visitantes
    # Crear dos categorías
    categorias = CategoriaNoticiaFactory.create_batch(2)
    # Crear seis noticias distribuidas entre ambas categorías
    noticias = NoticiaFactory.create_batch(
        4,
        parent=fixture_data["noticias"],
        categoria=categorias[0],
        first_published_at = timezone.make_aware(datetime(2026, 5, 12))
    ) + NoticiaFactory.create_batch(
        2,
        parent=fixture_data["noticias"],
        categoria=categorias[1],
        first_published_at = timezone.make_aware(datetime(2023, 5, 12))
    )
    pagina_noticias=fixture_data["noticias"]
    # Realiza get a la ruta
    response = client.get(f"{pagina_noticias.url}?categoria={categorias[0].id}")
    # Comprueba que se obtenga el código esperado
    assert response.status_code == 200
    # Comprueba que se obtenga la plantilla esperada
    assert "app_novedades/noticias_index_page.html" in [t.name for t in response.templates]
    # Comprueba que había datos cargados en la base de datos
    assert NoticiaPage.objects.count()==6
    # Ordena las noticias por fecha de publicación y luego por ID en orden descendente para obtener las últimas noticias
    # porque asi esta en el modelo, y se hace para que el test sea más robusto y no dependa del orden de creación de las noticias
    noticias_ordenadas = sorted(noticias, key=lambda noticia: (noticia.first_published_at, noticia.id), reverse=True)
    # Comprueba que se obtengan los datos correctos en la lista que corresponde a las últimas noticias cargadas
    # Estas noticias no se ven afectadas por el filtro de categoría
    assert list(response.context["noticias_destacadas"])==noticias_ordenadas[:3]
    # Comprueba que se obtengan las noticias filtradas.
    # En este caso se tiene paginación de 2 y solo 1 noticia cumple con el filtro, por lo que se obtiene 1 noticia filtrada
    assert list(response.context["noticias"])==noticias_ordenadas[3:4]


# Test para probar la página de noticias con noticias cargadas y filtrado de fechas
@pytest.mark.django_db
def test_pagina_noticias_filtro_fechas(client, paginas_indice_visitantes):
    fixture_data=paginas_indice_visitantes
    # Crear dos categorías
    categorias = CategoriaNoticiaFactory.create_batch(2)
    # Carga de datos en la base de datos
    noticias = NoticiaFactory.create_batch(
        4,
        parent=fixture_data["noticias"],
        categoria=categorias[0],
        first_published_at = timezone.make_aware(datetime(2026, 5, 12))
    ) + NoticiaFactory.create_batch(
        2,
        parent=fixture_data["noticias"],
        categoria=categorias[1],
        first_published_at = timezone.make_aware(datetime(2023, 5, 12))
    )
    pagina_noticias=fixture_data["noticias"]
    # Realiza get a la ruta
    response = client.get(f"{pagina_noticias.url}?fecha_desde=2026-04-01&fecha_hasta=2026-10-03")
    # Comprueba que se obtenga el código esperado
    assert response.status_code == 200
    # Comprueba que se obtenga la plantilla esperada
    assert "app_novedades/noticias_index_page.html" in [t.name for t in response.templates]
    # Comprueba que había datos cargados en la base de datos
    assert NoticiaPage.objects.count()==6
    # Ordena las noticias por fecha de publicación y luego por ID en orden descendente para obtener las últimas noticias
    # porque asi esta en el modelo, y se hace para que el test sea más robusto y no dependa del orden de creación de las noticias
    noticias_ordenadas = sorted(noticias, key=lambda noticia: (noticia.first_published_at, noticia.id), reverse=True)
    # Comprueba que se obtengan las noticias filtradas.
    # En este caso se tiene paginación de 3 pero solo 1 noticias cumplen con el filtro, por lo que se obtienen las 1 noticias filtradas
    assert list(response.context["noticias"])==[noticias_ordenadas[3]]


# Test para probar la página de noticias con noticias cargadas y filtrado combinado de categoría y fechas
@pytest.mark.django_db
def test_pagina_noticias_filtro_combinado(client, paginas_indice_visitantes):
    fixture_data=paginas_indice_visitantes
    # Cargar dos categorías
    categorias = CategoriaNoticiaFactory.create_batch(2)
    # Crear seis noticias distribuidas entre ambas categorías y diferentes fechas
    noticias = NoticiaFactory.create_batch(
        3,
        parent=fixture_data["noticias"],
        categoria=categorias[0],
        first_published_at = timezone.make_aware(datetime(2026, 5, 12))
    ) + NoticiaFactory.create_batch(
        1,
        parent=fixture_data["noticias"],
        categoria=categorias[1],
        first_published_at = timezone.make_aware(datetime(2026, 5, 11))
    ) + NoticiaFactory.create_batch(
        2,
        parent=fixture_data["noticias"],
        categoria=categorias[0],
        first_published_at = timezone.make_aware(datetime(2023, 5, 12))
    )
    pagina_noticias=fixture_data["noticias"]
    # Realiza get a la ruta
    response = client.get(f"{pagina_noticias.url}?categoria={categorias[1].id}&fecha_desde=2026-04-01&fecha_hasta=2026-10-03")
    # Comprueba que se obtenga el código esperado
    assert response.status_code == 200
    # Comprueba que se obtenga la plantilla esperada
    assert "app_novedades/noticias_index_page.html" in [t.name for t in response.templates]
    # Comprueba que había datos cargados en la base de datos
    assert NoticiaPage.objects.count()==6
    # Ordena las noticias por fecha de publicación y luego por ID en orden descendente para obtener las últimas noticias
    # porque asi esta en el modelo, y se hace para que el test sea más robusto y no dependa del orden de creación de las noticias
    noticias_ordenadas = sorted(noticias, key=lambda noticia: (noticia.first_published_at, noticia.id), reverse=True)
    # Comprueba que se obtengan las noticias filtradas.
    # En este caso se tiene paginación de 2 pero solo 1 noticias cumple con el filtro, por lo que se obtienen las 1 noticias filtradas
    assert list(response.context["noticias"])==[noticias_ordenadas[3]]


# Test para probar la página de detalle de noticia con datos validos
@pytest.mark.django_db
def test_pagina_detalle_noticia_valida(client, paginas_indice_visitantes):
    fixture_data=paginas_indice_visitantes
    # Carga un objeto a la base de datos y lo guarda en la variable para usarlo después
    noticia=NoticiaFactory.create(parent=fixture_data["noticias"], title="Noticia de prueba")
    # Realiza un get con el argumento esperado correcto
    response = client.get(f"{noticia.url}")
    # Comprueba que se obtenga el código esperado
    assert response.status_code == 200
    # Convierte a un string Unicode usando la codificación utf-8
    content = response.content.decode()
    # Compruenba que el título del objeto cargado anteriormente se encuentre en el contenido recibido 
    # y convertido a texto anteriormente
    assert noticia.title in content
    # Comprueba que se obtenga la plantilla esperada
    assert "app_novedades/noticia_page.html" in [template.name for template in response.templates]




######################################################### Tests para lo relacionado con los eventos #########################################################




# Test para probar la página de eventos sin eventos cargados
@pytest.mark.django_db
def test_pagina_eventos_sin_eventos(client, paginas_indice_visitantes):
    fixture_data=paginas_indice_visitantes
    # Realiza get a la ruta 
    pagina_eventos=fixture_data["eventos"]
    response = client.get(pagina_eventos.url)
    # Comprueba que se obtenga el código esperado
    assert response.status_code == 200
    # Comprueba que se obtenga la plantilla esperada
    assert "app_novedades/eventos_index_page.html" in [t.name for t in response.templates]
    # Comprueba que no había datos cargados en la base de datos
    assert EventoPage.objects.count()==0
    # Comprueba que se obtengan listas vacías
    assert list(response.context["eventos"]) == []


# Test para probar la página de eventos con eventos cargados
@pytest.mark.django_db
def test_pagina_eventos_con_eventos(client, paginas_indice_visitantes):
    fixture_data=paginas_indice_visitantes
    # Carga de datos en la base de datos
    eventos=EventoFactory.create_batch(6, parent=fixture_data["eventos"])
    # Realiza get a la ruta
    pagina_eventos=fixture_data["eventos"]
    response = client.get(pagina_eventos.url)
    # Comprueba que se obtenga el código esperado
    assert response.status_code == 200
    # Comprueba que se obtenga la plantilla esperada
    assert "app_novedades/eventos_index_page.html" in [t.name for t in response.templates]
    # Comprueba que había datos cargados en la base de datos
    assert EventoPage.objects.count()==6
    # Ordena los eventos por fecha del evento y luego por ID en orden descendente para obtener los últimos eventos
    # porque asi esta en el modelo, y se hace para que el test sea más robusto y no dependa del orden de creación de los eventos
    eventos_ordenados = sorted(eventos, key=lambda evento: (evento.fecha, evento.id), reverse=True)
    # Comprueba que se obtengan los datos correctos
    assert list(response.context["eventos"])==eventos_ordenados[:3]


# Test para probar la carga de eventos en fullcalendar
@pytest.mark.django_db
def test_pagina_eventos_fullcalendar(client, paginas_indice_visitantes):
    fixture_data=paginas_indice_visitantes
    # Carga de datos en la base de datos
    evento=EventoFactory.create(parent=fixture_data["eventos"])
    # Realiza get a la ruta
    response = client.get(reverse('app_novedades:eventos_json'))
    # Comprueba que se obtenga el código esperado
    assert response.status_code == 200
    data = response.json()
    # Comprueba que el objeto sea una lista como se espera
    assert isinstance(data, list)
    # Comprueba que la lista tenga un elemento
    assert len(data) == 1
    # Obtiene el primer evento
    evento_json = data[0]
    # Comprueba el título del evento obtenido con el esperado, en este caso, title es de FullCalendar
    assert evento_json["title"] == evento.title
    # Combina la fecha-hora y las convierte al formato esperado
    esperado = datetime.combine(evento.fecha, evento.hora).isoformat()
    # Comprueba la fecha-hora del evento obtenido con el esperado, en este caso, start es de FullCalendar
    assert evento_json["start"] == esperado


# Test para probar la página de eventos con eventos cargados y filtrado por categoría
@pytest.mark.django_db
def test_pagina_eventos_filtro_categorias(client, paginas_indice_visitantes):
    fixture_data=paginas_indice_visitantes
    # Cargar dos categorías
    categorias = CategoriaEventoFactory.create_batch(2)
    # Crear seis eventos distribuidos entre ambas categorías
    eventos = EventoFactory.create_batch(
        2,
        parent=fixture_data["eventos"],
        categoria=categorias[0],
        fecha = date.fromisoformat("2026-05-12")
    ) + EventoFactory.create_batch(
        4,
        parent=fixture_data["eventos"],
        categoria=categorias[1],
        fecha = date.fromisoformat("2023-05-12")
    )
    # Realiza get a la ruta
    pagina_eventos=fixture_data["eventos"]
    response = client.get(f"{pagina_eventos.url}?categoria={categorias[0].id}")
    # Comprueba que se obtenga el código esperado
    assert response.status_code == 200
    # Comprueba que se obtenga la plantilla esperada
    assert "app_novedades/eventos_index_page.html" in [t.name for t in response.templates]
    # Comprueba que había datos cargados en la base de datos
    assert EventoPage.objects.count()==6
    # Ordena los eventos por fecha del evento y luego por ID en orden descendente para obtener los últimos eventos
    # porque asi esta en el modelo, y se hace para que el test sea más robusto y no dependa del orden de creación de los eventos
    eventos_ordenados = sorted(eventos, key=lambda evento: (evento.fecha, evento.id), reverse=True)
    # Comprueba que se obtengan los eventos filtrados.
    # En este caso se tiene paginación de 3 pero solo 2 eventos cumplen con el filtro, por lo que se obtienen los 2 eventos filtrados
    assert list(response.context["eventos"])==eventos_ordenados[:2]


# Test para probar la página de eventos con eventos cargados y filtrado de fechas
@pytest.mark.django_db
def test_pagina_eventos_filtro_fechas(client, paginas_indice_visitantes):
    fixture_data=paginas_indice_visitantes
    # Cargar dos categorías
    categorias = CategoriaEventoFactory.create_batch(2)
    # Carga de datos en la base de datos
    eventos = EventoFactory.create_batch(
        2,
        parent=fixture_data["eventos"],
        categoria=categorias[0],
        fecha = date.fromisoformat("2026-05-12")
    ) + EventoFactory.create_batch(
        4,
        parent=fixture_data["eventos"],
        categoria=categorias[1],
        fecha = date.fromisoformat("2023-05-12")
    )
    pagina_eventos=fixture_data["eventos"]
    # Realiza get a la ruta
    response = client.get(f"{pagina_eventos.url}?fecha_desde=2026-04-01&fecha_hasta=2026-10-03")
    # Comprueba que se obtenga el código esperado
    assert response.status_code == 200
    # Comprueba que se obtenga la plantilla esperada
    assert "app_novedades/eventos_index_page.html" in [t.name for t in response.templates]
    # Comprueba que había datos cargados en la base de datos
    assert EventoPage.objects.count()==6
    # Ordena los eventos por fecha del evento y luego por ID en orden descendente para obtener los últimos eventos
    # porque asi esta en el modelo, y se hace para que el test sea más robusto y no dependa del orden de creación de los eventos
    eventos_ordenados = sorted(eventos, key=lambda evento: (evento.fecha, evento.id), reverse=True)
    # Comprueba que se obtengan los eventos filtrados.
    # En este caso se tiene paginación de 3 pero solo 2 eventos cumplen con el filtro, por lo que se obtienen los 2 eventos filtrados
    assert list(response.context["eventos"])==eventos_ordenados[:2]


# Test para probar la página de eventos con eventos cargados y filtrado combinado de categoría y fechas
@pytest.mark.django_db
def test_pagina_eventos_filtro_combinado(client, paginas_indice_visitantes):
    fixture_data=paginas_indice_visitantes
    # Cargar dos categorías
    categorias = CategoriaEventoFactory.create_batch(2)
    # Crear seis eventos distribuidos entre ambas categorías y diferentes fechas
    eventos = EventoFactory.create_batch(
            1,
            parent=fixture_data["eventos"],
            categoria=categorias[0],
            fecha = date.fromisoformat("2026-05-12")
        ) + EventoFactory.create_batch(
            1,
            parent=fixture_data["eventos"],
            categoria=categorias[1],
            fecha = date.fromisoformat("2026-06-12")
        ) + EventoFactory.create_batch(
            4,
            parent=fixture_data["eventos"],
            categoria=categorias[0],
            fecha = date.fromisoformat("2023-05-12")
        )
    pagina_eventos=fixture_data["eventos"]
    # Realiza get a la ruta
    response = client.get(f"{pagina_eventos.url}?categoria={categorias[0].id}&fecha_desde=2026-04-01&fecha_hasta=2026-10-03")
    # Comprueba que se obtenga el código esperado
    assert response.status_code == 200
    # Comprueba que se obtenga la plantilla esperada
    assert "app_novedades/eventos_index_page.html" in [t.name for t in response.templates]
    # Comprueba que había datos cargados en la base de datos
    assert EventoPage.objects.count()==6
    # Ordena los eventos por fecha del evento y luego por ID en orden descendente para obtener los últimos eventos
    # porque asi esta en el modelo, y se hace para que el test sea más robusto y no dependa del orden de creación de los eventos
    eventos_ordenados = sorted(eventos, key=lambda evento: (evento.fecha, evento.id), reverse=True)
    # Comprueba que se obtengan los eventos filtrados.
    # En este caso se tiene paginación de 3 pero solo 1 eventos cumple con el filtro, por lo que se obtiene los 1 evento filtrado
    assert list(response.context["eventos"])==[eventos_ordenados[1]]

