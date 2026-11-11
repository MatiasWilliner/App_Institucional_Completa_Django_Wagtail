import datetime

import factory
import wagtail_factories
from wagtail.images import get_image_model
from app_novedades.models import CategoriaEvento, CategoriaNoticia, EventoPage, EventosIndexPage, NoticiaPage, NoticiasIndexPage
from app_trabajo.models import AreaPage, AreasIndexPage, ImagenExtra, TallerPage, TalleresIndexPage




######################################################### Factories para los tests #########################################################




class ImagenFactory(wagtail_factories.ImageFactory):
    class Meta:
        model = get_image_model()

class CategoriaNoticiaFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CategoriaNoticia

    descripcion = "Categoria noticia original"
    color = "#f39c12"

class CategoriaEventoFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CategoriaEvento

    descripcion = "Categoria evento original"
    color = "#f39c12"

class NoticiasIndexFactory(wagtail_factories.PageFactory):
    class Meta:
        model = NoticiasIndexPage

    title = "Noticias"

class NoticiaFactory(wagtail_factories.PageFactory):
    class Meta:
        model = NoticiaPage

    title = factory.Sequence(lambda n: f"Noticia original {n + 1}")
    descripcion = "Esto es una noticia"
    categoria = factory.SubFactory(CategoriaNoticiaFactory)
    imagen = factory.SubFactory(ImagenFactory)

class EventosIndexFactory(wagtail_factories.PageFactory):
    class Meta:
        model = EventosIndexPage

    title = "Eventos"

class EventoFactory(wagtail_factories.PageFactory):
    class Meta:
        model = EventoPage

    title = factory.Sequence(lambda n: f"Evento original {n + 1}")
    descripcion = "Esto es un evento"
    formulario = "http://www.google.com/"
    categoria = factory.SubFactory(CategoriaEventoFactory)
    imagen = factory.SubFactory(ImagenFactory)
    fecha = datetime.date.fromisoformat("2025-05-12")
    hora = "12:15"
    modalidad = "Presencial"
    lugar = "Lugar de ejemplo"

class AreasIndexFactory(wagtail_factories.PageFactory):
    class Meta:
        model = AreasIndexPage

    title = "Áreas"

class AreaFactory(wagtail_factories.PageFactory):
    class Meta:
        model = AreaPage

    title = factory.Sequence(lambda n: f"Área original {n + 1}")
    descripcion = "Esto es un área"
    imagen = factory.SubFactory(ImagenFactory)

class TalleresIndexFactory(wagtail_factories.PageFactory):
    class Meta:
        model = TalleresIndexPage

    title = "Talleres"

class TallerFactory(wagtail_factories.PageFactory):
    class Meta:
        model = TallerPage

    title = factory.Sequence(lambda n: f"Taller original {n + 1}")
    descripcion = "Esto es un taller"
    imagen = factory.SubFactory(ImagenFactory)
    formulario = "http://www.google.com/"

class ImagenExtraFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ImagenExtra

    archivo=factory.SubFactory(ImagenFactory)
    taller=factory.SubFactory(TallerFactory)