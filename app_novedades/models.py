from datetime import date, datetime, time, timezone

from django.db import models
from django.core.paginator import Paginator
from django.utils import timezone

from urllib3 import request
from wagtail.snippets.models import register_snippet
from wagtail.admin.panels import FieldPanel
from wagtail.models import Page
from wagtail.fields import RichTextField
from wagtail.images import get_image_model


# Modelo de categoría de noticias que es un snippet registrado en Wagtail
# Un snippet es un tipo de contenido reutilizable. Complementa a las pages 
# y permite crear contenido que puede ser referenciado en múltiples lugares del sitio web.
@register_snippet
class CategoriaNoticia(models.Model):
    COLORES_CHOICES = [
        ("#c64d4d", "Rojo ladrillo"),
        ("#d19e46", "Mostaza"),
        ("#1f5d7e", "Azul petróleo"),
        ("#4CAF50", "Verde"),
        ("#bdc3c7", "Gris claro"),
        ("#d2b4de", "Lila claro"),
        ("#2c3e50", "Gris oscuro"),
        ("#e67e22", "Naranja fuerte"),
        ("#8e44ad", "Violeta oscuro"),
        ("#16a085", "Verde azulado"),
        ("#34495e", "Azul grisáceo"),
        ("#e74c3c", "Rojo fuerte"),
        ("#2980b9", "Azul intenso"),
        ("#f39c12", "Amarillo dorado"),
    ]

    # Campos del modelo de categoría de noticias
    descripcion = models.CharField(max_length=80)
    color = models.CharField(
        max_length=7,
        choices=COLORES_CHOICES,
        default="#c64d4d"
    )
    # Paneles de contenido para la categoría de noticias
    panels = [
        FieldPanel("descripcion"),
        FieldPanel("color"),
    ]

    def __str__(self):
        return self.descripcion

# Modelo de la página de índice de noticias
# Permite crear una página que actúa como contenedor para las noticias individuales
class NoticiasIndexPage(Page):
    subpage_types = ["app_novedades.NoticiaPage"]

    class Meta:
        verbose_name = "Índice de noticias"

    def get_context(self, request):

        context = super().get_context(request)

        noticias = (
            NoticiaPage.objects
            .child_of(self)
            .live()
            .specific()
            .order_by("-first_published_at","-id")
        )

        # Las 3 noticias destacadas
        noticias_destacadas = noticias[:3]
        # Obtenemos los IDs de las noticias destacadas para excluirlas de las restantes
        ids_noticias_destacadas = [noticia.id for noticia in noticias_destacadas]

        # El resto de las noticias.
        # Se obtienen de esta forma para despues poderles aplicar el filtro
        # porque no se puede filtrar un slice 
        noticias_restantes = noticias.exclude(
            id__in=ids_noticias_destacadas
        )

        # Filtro por categoría
        categoria = request.GET.get("categoria")
        if categoria:
            noticias_restantes = noticias_restantes.filter(
                categoria_id=categoria
            )
        
        # Filtro rango de fechas
        fecha_desde = request.GET.get("fecha_desde")
        fecha_hasta = request.GET.get("fecha_hasta")
        # Si se especifica fecha_desde, se hace aware y se le asigna la hora mínima del día para que incluya todas las noticias de ese día
        if fecha_desde:
            fecha_desde = timezone.make_aware(
                datetime.combine(
                    date.fromisoformat(fecha_desde),
                    time.min
                )
            )
            noticias_restantes = noticias_restantes.filter(
                first_published_at__gte=fecha_desde
            )
        # Si se especifica fecha_hasta, se hace aware y se le asigna la hora máxima del día para que incluya todas las noticias de ese día
        if fecha_hasta:
            fecha_hasta = timezone.make_aware(
                datetime.combine(
                    date.fromisoformat(fecha_hasta),
                    time.max
                )
            )
            noticias_restantes = noticias_restantes.filter(
                first_published_at__lte=fecha_hasta
            )

        # Paginación solamente para las restantes
        paginator = Paginator(noticias_restantes, 2)
        page_number = request.GET.get("page")

        # Las noticias destacadas y las noticias paginadas al contexto
        context["noticias_destacadas"] = noticias_destacadas
        context["noticias"] = paginator.get_page(page_number)

        # Las categorías de noticias para que estén disponibles en las plantillas
        context["categorias"] = CategoriaNoticia.objects.all()

        return context

# Modelo de las noticias que hereda de la clase Page de Wagtail
# Una page es un tipo de contenido que puede ser creado y gestionado en el CMS de Wagtail
class NoticiaPage(Page):
    # Campos de la página de noticias
    descripcion = RichTextField()
    categoria = models.ForeignKey(
        CategoriaNoticia,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    direccion = models.URLField(blank=True, null=True)
    imagen = models.ForeignKey(
        get_image_model(),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )
    # Paneles de contenido para la página de noticias
    content_panels = Page.content_panels + [
        FieldPanel("descripcion"),
        FieldPanel("categoria"),
        FieldPanel("direccion"),
        FieldPanel("imagen"),
    ]
    # Tipos de página padre permitidos para las página de las noticias
    parent_page_types = ["app_novedades.NoticiasIndexPage"]

    # Contexto para etiquetas de redes sociales
    def get_context(self, request):
        context = super().get_context(request)
        context["url_compartir"] = request.build_absolute_uri(self.url)
        context["type"]="Noticia"
        return context

# Modelo de categoría de eventos que es un snippet registrado en Wagtail
@register_snippet
class CategoriaEvento(models.Model):
    COLORES_CHOICES = [
        ("#c64d4d", "Rojo ladrillo"),
        ("#d19e46", "Mostaza"),
        ("#1f5d7e", "Azul petróleo"),
        ("#4CAF50", "Verde"),
        ("#bdc3c7", "Gris claro"),
        ("#d2b4de", "Lila claro"),
        ("#2c3e50", "Gris oscuro"),
        ("#e67e22", "Naranja fuerte"),
        ("#8e44ad", "Violeta oscuro"),
        ("#16a085", "Verde azulado"),
        ("#34495e", "Azul grisáceo"),
        ("#e74c3c", "Rojo fuerte"),
        ("#2980b9", "Azul intenso"),
        ("#f39c12", "Amarillo dorado"),
    ]
    descripcion=models.CharField(max_length=80)
    color=models.CharField(
        max_length=7, 
        choices=COLORES_CHOICES, 
        default="#c64d4d"
    )
    panels = [
        FieldPanel("descripcion"),
        FieldPanel("color"),
    ]
    def __str__(self):
        return self.descripcion
    
# Modelo de la página de índice de eventos
class EventosIndexPage(Page):
    subpage_types = ["app_novedades.EventoPage"]

    class Meta:
        verbose_name = "Índice de eventos"

    def get_context(self, request):
        context = super().get_context(request)

        eventos = (
            EventoPage.objects
            .child_of(self)
            .live()
            .specific()
            .order_by("-fecha","-id")
        )

        # Filtro por categoría
        categoria = request.GET.get("categoria")
        if categoria:
            eventos = eventos.filter(
                categoria_id=categoria
            )
                
        # Filtro rango de fechas
        fecha_desde = request.GET.get("fecha_desde")
        fecha_hasta = request.GET.get("fecha_hasta")
        print(fecha_desde)
        if fecha_desde:
            eventos = eventos.filter(
                fecha__gte=fecha_desde
            )
        if fecha_hasta:
            eventos = eventos.filter(
                fecha__lte=fecha_hasta
            )

        # Paginación solamente para las restantes
        paginator = Paginator(eventos, 3)
        page_number = request.GET.get("page")

        context["eventos"] = paginator.get_page(page_number)
        context["categorias"] = CategoriaEvento.objects.all()

        return context
    
# Modelo de los eventos que hereda de la clase Page de Wagtail   
class EventoPage(Page):
    MODALIDAD = [
        ('Presencial', 'Presencial'),
        ('Virtual', 'Virtual'),
    ]
    descripcion=RichTextField()
    formulario=models.URLField(null=True, blank=True)
    categoria = models.ForeignKey(
        CategoriaEvento,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    fecha=models.DateField(default=date.today)
    hora=models.TimeField()
    modalidad=models.CharField(max_length=100, choices=MODALIDAD, default="")
    lugar=models.CharField(max_length=300)
    imagen = models.ForeignKey(
        get_image_model(),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )
    content_panels = Page.content_panels + [
        FieldPanel("descripcion"),
        FieldPanel("formulario"),
        FieldPanel("categoria"),
        FieldPanel("fecha"),
        FieldPanel("hora"),
        FieldPanel("modalidad"),
        FieldPanel("lugar"),
        FieldPanel("imagen")
    ]
    parent_page_types = ["app_novedades.EventosIndexPage"]