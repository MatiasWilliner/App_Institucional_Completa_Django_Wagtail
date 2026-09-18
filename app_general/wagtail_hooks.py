from django.templatetags.static import static
from wagtail import hooks
from wagtail.admin.ui.components import Component
from django.utils.html import format_html
from django.template.loader import render_to_string

from app_novedades.models import EventoPage, NoticiaPage
from app_trabajo.models import AreaPage, TallerPage

# Los hooks en este caso son funciones que detecta wagtail mediante la etiqueta hooks. 
# Estos permiten personalizar tanto los estilos como las deistribución del template.
# Dependiendo la página y lo que se quiere modificar, se tienen palabras claves como en este caso
# insert_global_admin_css
# Hook para cambiar los estilos del panel de administración
@hooks.register("insert_global_admin_css")
def css_admin_global():
    return f'<link rel="stylesheet" href="{static("app_general/css/estilos-wagtail-personalizados.css")}">'

# Hook para cambiar la página principal
@hooks.register("construct_main_menu")
def modificar_menu(request, menu_items):
    # Opciones a eliminar de la barra izqueirda
    elementos_a_eliminar = {
        "documents",
    }
    # Armar una lista con todos los items menos los que se eliminan
    menu_items[:] = [
        item for item in menu_items
        if item.name not in elementos_a_eliminar
    ]

# Panel para mostrar atajos a las páginas de carga
class ShortcutPanel(Component):
    order = 50

    def render_html(self, parent_context):
        return render_to_string(
            "wagtailadmin/atajos.html",
            request=parent_context["request"],
        )

# Panel para mostrar la cantidad de elementos cargados
class QuantityPanel(Component):
    order = 60

    def __init__(self, request):
        self.request = request

    def render_html(self, parent_context):

        context = {
            "noticias": NoticiaPage.objects.live().count(),
            "eventos": EventoPage.objects.live().count(),
            "talleres": TallerPage.objects.live().count(),
            "areas": AreaPage.objects.live().count(),
        }

        return render_to_string(
            "wagtailadmin/cantidades.html",
            context,
            request=self.request,
        )

# Hook para agregar paneles personalizados
@hooks.register("construct_homepage_panels")
def agregar_paneles_personalizados(request, panels):
    panels.append(ShortcutPanel())
    panels.append(QuantityPanel(request))