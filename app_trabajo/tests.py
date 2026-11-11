from datetime import datetime, date
import pytest

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from wagtail.models import Site

from AppCompletaEjemploCMS.factories import AreaFactory, AreasIndexFactory, EventoFactory, EventosIndexFactory, ImagenExtraFactory, NoticiasIndexFactory, TallerFactory, TalleresIndexFactory
from app_trabajo.models import AreaPage, ImagenExtra, TallerPage




######################################################### Fixtures #########################################################




# Fixture para creación de páginas índice de visitantes
@pytest.fixture()
def paginas_indice_visitantes():
    # Obtenemos la página raíz del sitio por defecto 
    # y creamos las páginas índice de visitantes como hijas de la misma
    root = Site.objects.get(is_default_site=True).root_page
    NoticiasIndexFactory.create(parent=root)
    EventosIndexFactory.create(parent=root)
    areas=AreasIndexFactory.create(parent=root)
    talleres=TalleresIndexFactory.create(parent=root)
    return {
        "areas": areas,
        "talleres": talleres
    }




######################################################### Tests para lo relacionado con las áreas #########################################################




# Test para probar la página de areas sin areas cargadas
@pytest.mark.django_db
def test_pagina_areas_sin_areas(client, paginas_indice_visitantes):
    fixture_data=paginas_indice_visitantes
    # Realiza get a la ruta 
    pagina_areas=fixture_data["areas"]
    response = client.get(pagina_areas.url)
    # Comprueba que se obtenga el código esperado
    assert response.status_code == 200
    # Comprueba que se obtenga la plantilla esperada
    assert "app_trabajo/areas_index_page.html" in [t.name for t in response.templates]
    # Comprueba que no había datos cargados en la base de datos
    assert AreaPage.objects.count()==0
    # Comprueba que se obtengan listas vacías
    assert list(response.context["areas"]) == []


# Test para probar la página de áreas con áreas cargadas
@pytest.mark.django_db
def test_pagina_areas_con_areas(client, paginas_indice_visitantes):
    fixture_data=paginas_indice_visitantes
    # Carga de datos en la base de datos
    areas=AreaFactory.create_batch(6, parent=fixture_data["areas"])
    # Realiza get a la ruta
    pagina_areas=fixture_data["areas"]
    response = client.get(pagina_areas.url)
    # Comprueba que se obtenga el código esperado
    assert response.status_code == 200
    # Comprueba que se obtenga la plantilla esperada
    assert "app_trabajo/areas_index_page.html" in [t.name for t in response.templates]
    # Comprueba que había datos cargados en la base de datos
    assert AreaPage.objects.count()==6
    # Ordena las áreas por fecha de publicación y luego por ID en orden descendente para obtener las últimas áreas
    # porque asi esta en el modelo, y se hace para que el test sea más robusto y no dependa del orden de creación de las áreas
    areas_ordenadas = sorted(areas, key=lambda area: (area.first_published_at, area.id), reverse=True)
    # Comprueba que se obtengan los datos correctos en la lista que corresponde a las últimas áreas cargadas
    assert list(response.context["areas"])==areas_ordenadas[:3]




######################################################### Tests para lo relacionado con los talleres #########################################################




# Test para probar la página de talleres sin talleres cargados
@pytest.mark.django_db
def test_pagina_talleres_sin_talleres(client, paginas_indice_visitantes):
    fixture_data=paginas_indice_visitantes
    # Realiza get a la ruta
    pagina_talleres=fixture_data["talleres"]
    response = client.get(pagina_talleres.url)
    # Comprueba que se obtenga el código esperado
    assert response.status_code == 200
    # Comprueba que se obtenga la plantilla esperada
    assert "app_trabajo/talleres_index_page.html" in [t.name for t in response.templates]
    # Comprueba que no había datos cargados en la base de datos
    assert TallerPage.objects.count()==0
    # Comprueba que se obtengan listas vacías
    assert list(response.context["talleres"]) == []


# Test para probar la página de talleres con talleres cargados
@pytest.mark.django_db
def test_pagina_talleres_con_talleres(client, paginas_indice_visitantes):
    fixture_data=paginas_indice_visitantes
    # Carga de datos en la base de datos
    talleres=TallerFactory.create_batch(6, parent=fixture_data["talleres"])
    # Realiza get a la ruta
    pagina_talleres=fixture_data["talleres"]
    response = client.get(pagina_talleres.url)
    # Comprueba que se obtenga el código esperado
    assert response.status_code == 200
    # Comprueba que se obtenga la plantilla esperada
    assert "app_trabajo/talleres_index_page.html" in [t.name for t in response.templates]
    # Comprueba que había datos cargados en la base de datos
    assert TallerPage.objects.count()==6
    # Ordena los talleres por fecha de publicación y luego por ID en orden descendente para obtener los últimos talleres
    # porque asi esta en el modelo, y se hace para que el test sea más robusto y no dependa del orden de creación de los talleres
    talleres_ordenados = sorted(talleres, key=lambda taller: (taller.first_published_at, taller.id), reverse=True)
    # Comprueba que se obtengan los datos correctos
    assert list(response.context["talleres"])==talleres_ordenados[:3]


# Test para probar la página de detalle de taller con datos validos
@pytest.mark.django_db
def test_pagina_detalle_taller_con_imagenes(client, paginas_indice_visitantes):
    fixture_data=paginas_indice_visitantes
    # Carga un objeto a la base de datos y lo guarda en la variable para usarlo después
    taller=TallerFactory.create(parent=fixture_data["talleres"], title="Taller de prueba")
    ImagenExtraFactory.create_batch(3, taller=taller)
    # Realiza un get con el argumento esperado correcto
    response = client.get(f"{taller.url}")
    # Comprueba que se obtenga el código esperado
    assert response.status_code == 200
    # Convierte a un string Unicode usando la codificación utf-8
    content = response.content.decode()
    # Compruenba que el título del objeto cargado anteriormente se encuentre en el contenido recibido 
    # y convertido a texto anteriormente
    assert taller.title in content
    # Comprueba que hay imágenes extras cargadas en la base de datos
    assert taller.imagenes_extra.count()==3
    # Comprueba que se obtenga la plantilla esperada
    assert "app_trabajo/taller_page.html" in [template.name for template in response.templates]


# Test para probar la página de detalle de taller con datos validos
@pytest.mark.django_db
def test_pagina_detalle_taller_sin_imagenes(client, paginas_indice_visitantes):
    fixture_data=paginas_indice_visitantes
    # Carga un objeto a la base de datos y lo guarda en la variable para usarlo después
    taller=TallerFactory.create(parent=fixture_data["talleres"], title="Taller de prueba")
    # Realiza un get con el argumento esperado correcto
    response = client.get(f"{taller.url}")
    # Comprueba que se obtenga el código esperado
    assert response.status_code == 200
    # Convierte a un string Unicode usando la codificación utf-8
    content = response.content.decode()
    # Compruenba que el título del objeto cargado anteriormente se encuentre en el contenido recibido 
    # y convertido a texto anteriormente
    assert taller.title in content
    # Comprueba que no hay imágenes extras cargadas en la base de datos
    assert taller.imagenes_extra.count()==0
    # Comprueba que se obtenga la plantilla esperada
    assert "app_trabajo/taller_page.html" in [template.name for template in response.templates]

