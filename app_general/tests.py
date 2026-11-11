import pytest

from django.urls import reverse
from django.contrib.auth.models import User
from django.templatetags.static import static as static_url
from django.test import RequestFactory

from wagtail import hooks

from AppCompletaEjemploCMS.factories import AreasIndexFactory, EventoFactory, EventosIndexFactory, NoticiaFactory, NoticiasIndexFactory, TalleresIndexFactory
from app_general.wagtail_hooks import QuantityPanel, ShortcutPanel
from app_novedades.models import NoticiaPage, EventoPage


# Fixture para creación de páginas índice de visitantes
@pytest.fixture()
def paginas_indice_visitantes():
    AreasIndexFactory.create()
    TalleresIndexFactory.create()
    noticias=NoticiasIndexFactory.create()
    eventos=EventosIndexFactory.create()
    return {
        "noticias": noticias,
        "eventos":eventos
    } 


# Test para probar la página home sin información para la misma. Si bien los valores que 
# devuelve el fixture no se usan en este test, es necesario que se ejecute para que se creen 
# las páginas índice de visitantes y no falle el test.
@pytest.mark.django_db
def test_pagina_home_sin_info(client, paginas_indice_visitantes):
    # Realiza get a la ruta y guarda la respuesta en una variable para usar después
    response = client.get(reverse("app_general:home"))
    # Comprueba que se obtenga el código esperado
    assert response.status_code == 200
    # Comprueba que se obtenga la plantilla esperada
    assert "home.html" in [template.name for template in response.templates]
    # Comprueba que no había datos cargados en la base de datos
    assert NoticiaPage.objects.count()==0
    assert EventoPage.objects.count()==0
    # Comprueba que se obtengan listas vacías
    assert list(response.context["noticias"]) == []
    assert list(response.context["eventos"]) == []


# Test para probar la página home con información para la misma
@pytest.mark.django_db
def test_pagina_home_con_info(client, paginas_indice_visitantes):
    fixture_data=paginas_indice_visitantes
    # Carga de datos en la base de datos
    noticia=NoticiaFactory.create(parent=fixture_data["noticias"])
    evento=EventoFactory.create(parent=fixture_data["eventos"])
    # Realiza get a la ruta 
    response = client.get(reverse("app_general:home"))
    # Comprueba que se obtenga el código esperado
    assert response.status_code == 200
    # Comprueba que se obtenga la plantilla esperada
    assert "home.html" in [t.name for t in response.templates]
    # Comprueba que no había datos cargados en la base de datos
    assert NoticiaPage.objects.count()==1
    assert EventoPage.objects.count()==1
    # Comprueba que se obtengan listas correctas
    assert list(response.context["noticias"])==[noticia]
    assert list(response.context["eventos"])==[evento]


# Test para probar la página sobre nosotros. Lo mismo que el primer test
@pytest.mark.django_db
def test_pagina_sobre_nosotros(client, paginas_indice_visitantes):
    response = client.get(reverse("app_general:sobre_nosotros"))
    assert response.status_code == 200
    assert "sobre_nosotros.html" in [template.name for template in response.templates] 


# Test para probar la página de administración base personalizada.
@pytest.mark.django_db
def test_pagina_admin_base_personalizada(client):
    # Crea un usuario de prueba y lo autentica en el cliente de pruebas
    usuario_prueba=User.objects.create_user(username="tester", password="12345", is_superuser=True)
    # Autentica al usuario en el cliente de pruebas
    client.force_login(usuario_prueba)
    # Realiza get a la ruta de administración y guarda la respuesta en una variable para usar después
    response = client.get(reverse("wagtailadmin_home"))
    assert response.status_code == 200
    # Comprueba que se obtenga la plantilla esperada
    assert "CMS Institucional".encode("utf-8") in response.content


# Test para probar la página de login personalizada.
@pytest.mark.django_db
def test_pagina_login_personalizada(client):
    response = client.get(reverse("wagtailadmin_login"))
    assert response.status_code == 200
    assert "Iniciar sesión en el CMS".encode("utf-8") in response.content


# Test para probar la carga de los paneles personalizados en la página de administración.
@pytest.mark.django_db
def test_carga_paneles_personalizados(client):
    usuario_prueba=User.objects.create_user(username="tester", password="12345", is_superuser=True)
    client.force_login(usuario_prueba)
    response = client.get(reverse("wagtailadmin_home"))
    assert "Atajos".encode("utf-8") in response.content
    assert "Cantidades cargadas".encode("utf-8") in response.content


# Test para probar el panel de atajos
@pytest.mark.django_db
def test_shortcut_panel():
    # Crea un objeto RequestFactory para simular una solicitud HTTP. RequestFactory permite 
    # construir una petición sin realizar una solicitud completa mediante el cliente de pruebas de Django
    request = RequestFactory().get("/admin/")
    # Crea un contexto de solicitud para pasar al componente ShortcutPanel
    parent_context = {"request": request}
    # Crea una instancia del componente ShortcutPanel y renderiza su HTML
    componente = ShortcutPanel()
    html = componente.render_html(parent_context)
    # Comprueba que la cadena "Atajos" esté presente en el HTML generado por el componente
    assert "Atajos" in html


# Test para probar el panel de cantidades
@pytest.mark.django_db
def test_quantity_panel():
    # Crea un objeto RequestFactory para simular una solicitud HTTP. RequestFactory permite 
    # construir una petición sin realizar una solicitud completa mediante el cliente de pruebas de Django
    request = RequestFactory().get("/admin/")
    # Crea un contexto de solicitud para pasar al componente QuantityPanel
    parent_context = {"request": request}
    # Crea una instancia del componente QuantityPanel y renderiza su HTML
    componente = QuantityPanel()
    html = componente.render_html(parent_context)
    # Comprueba que la cadena "Cantidades cargadas" esté presente en el HTML generado por el componente
    assert "Cantidades cargadas" in html


# Test para probar el hook insert_global_admin_css
@pytest.mark.django_db
def test_css_admin_global():
    # Obtiene la lista de funciones registradas para el hook "insert_global_admin_css"
    hook = hooks.get_hooks("insert_global_admin_css")
    # Busca la función con el nombre "css_admin_global" en la lista de funciones registradas y la ejecuta
    resultado = next(
        funcion() for funcion in hook
        if funcion.__name__ == "css_admin_global"
    )
    # Comprueba que el resultado de la función sea igual a la cadena esperada
    assert (
        f'<link rel="stylesheet" href="{static_url("app_general/css/estilos-wagtail-personalizados.css")}">'
        == resultado
    )