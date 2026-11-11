from datetime import date

from django.db import models
from django.core.paginator import Paginator

from urllib3 import request
from wagtail.snippets.models import register_snippet
from wagtail.admin.panels import FieldPanel, InlinePanel
from wagtail.models import Page, ParentalKey
from wagtail.fields import RichTextField
from wagtail.images import get_image_model


# Modelo de la página de índice de talleres
# Permite crear una página que actúa como contenedor para los talleres individuales
class TalleresIndexPage(Page):
    subpage_types = ["app_trabajo.TallerPage"]

    class Meta:
        verbose_name = "Índice de talleres"

    def get_context(self, request):

        context = super().get_context(request)

        talleres = (
            TallerPage.objects
            .child_of(self)
            .live()
            .specific()
            .order_by("-first_published_at","-id")
        )

        # Paginación para todos los talleres
        paginator = Paginator(talleres, 3)
        page_number = request.GET.get("page")

        # Se pasan los talleres con la paginación en el contexto
        context["talleres"] = paginator.get_page(page_number)

        return context

# Modelo de los talleres que hereda de la clase Page de Wagtail
# Una page es un tipo de contenido que puede ser creado y gestionado en el CMS de Wagtail
class TallerPage(Page):
    # Campos de la página de talleres
    descripcion = RichTextField()
    imagen = models.ForeignKey(
        get_image_model(),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )
    formulario = models.URLField(blank=True, null=True)
    # Paneles de contenido para la página de talleres
    content_panels = Page.content_panels + [
        FieldPanel("descripcion"),
        FieldPanel("imagen"),
        FieldPanel("formulario"),
        InlinePanel(
            "imagenes_extra",
            label="Imágenes extra"
        ),
    ]
    # Tipos de página padre permitidos para las páginas de los talleres
    parent_page_types = ["app_trabajo.TalleresIndexPage"]
    # Contexto para etiquetas de redes sociales
    def get_context(self, request):
        context = super().get_context(request)
        context["url_compartir"] = request.build_absolute_uri(self.url)
        context["type"]="Taller"
        return context

# Modelo Imagen extra del taller
class ImagenExtra(models.Model):
    archivo = models.ForeignKey(
        get_image_model(),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )
    taller = ParentalKey(
        "app_trabajo.TallerPage",
        on_delete=models.CASCADE,
        related_name="imagenes_extra"
    )
    # Paneles de contenido para la página de imágenes extras del taller
    content_panels = Page.content_panels + [
        FieldPanel("archivo"),
        FieldPanel("taller"),
    ]

# Modelo de la página de índice de talleres
# Permite crear una página que actúa como contenedor para los talleres individuales
class AreasIndexPage(Page):
    subpage_types = ["app_trabajo.AreaPage"]

    class Meta:
        verbose_name = "Índice de áreas"

    def get_context(self, request):

        context = super().get_context(request)

        areas = (
            AreaPage.objects
            .child_of(self)
            .live()
            .specific()
            .order_by("-first_published_at","-id")
        )

        # Paginación para todas las áreas
        paginator = Paginator(areas, 3)
        page_number = request.GET.get("page")

        # Se pasan las áreas con la paginación en el contexto
        context["areas"] = paginator.get_page(page_number)

        return context

# Modelo de las áreas que hereda de la clase Page de Wagtail
# Una page es un tipo de contenido que puede ser creado y gestionado en el CMS de Wagtail
class AreaPage(Page):
    # Campos de la página de areas
    descripcion = RichTextField()
    imagen = models.ForeignKey(
        get_image_model(),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )
    # Paneles de contenido para la página de áreas
    content_panels = Page.content_panels + [
        FieldPanel("descripcion"),
        FieldPanel("imagen"),
    ]
    # Tipos de página padre permitidos para las páginas de las áreas
    parent_page_types = ["app_trabajo.AreasIndexPage"]