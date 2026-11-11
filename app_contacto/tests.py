import pytest
from unittest.mock import patch

from django.contrib.messages.api import get_messages
from django.urls import reverse

from AppCompletaEjemploCMS.factories import AreasIndexFactory, EventosIndexFactory, NoticiasIndexFactory, TalleresIndexFactory


# Fixture para creación de páginas índice de visitantes
@pytest.fixture()
def paginas_indice_visitantes():
    AreasIndexFactory.create()
    TalleresIndexFactory.create()
    NoticiasIndexFactory.create()
    EventosIndexFactory.create()


# Test para probar la página contacto
@pytest.mark.django_db
def test_pagina_contacto(client,paginas_indice_visitantes):
    response = client.get(reverse("app_contacto:contacto"))
    assert response.status_code == 200
    content = response.content.decode()
    assert '<form' in content
    assert "contacto.html" in [template.name for template in response.templates] 


# Test para probar el correcto envío de mail
@pytest.mark.django_db
def test_exito_envio_mail(client,paginas_indice_visitantes):
    with patch("app_contacto.views.requests.post") as mock_recaptcha, \
         patch("app_contacto.views.EmailMultiAlternatives.send") as mock_send:
        # Simula captcha válido
        mock_recaptcha.return_value.json.return_value = {"success": True}
        # Simula envío exitoso de mail
        mock_send.return_value = 1
        response = client.post(reverse("app_contacto:enviar_mail_personalizado"),
            {"g-recaptcha-response": "fake-token","nombre_completo": "Nombre Apellido", "email":"email@hotmail.com", "telefono":"345678", "consulta":"Esta es una consulta de prueba"},
            follow=True
        )
    assert response.status_code == 200
    assert response.request["PATH_INFO"] == reverse("app_contacto:contacto")
    messages = list(get_messages(response.wsgi_request))
    assert any("Correo enviado correctamente." in str(message) for message in messages)


# Test para probar el error en envio de mail por respuesta negativa en la validación de recaptcha
@pytest.mark.django_db
def test_error_usuario_validacion_envio_mail(client,paginas_indice_visitantes):
    with patch("app_contacto.views.requests.post") as mock_recaptcha:
        mock_recaptcha.return_value.json.return_value = {"success": False}
        response = client.post(reverse("app_contacto:enviar_mail_personalizado"),
            {"g-recaptcha-response": "fake-token","nombre_completo": "Nombre Apellido", "email":"email@hotmail.com", "telefono":"345678", "consulta":"Esta es una consulta de prueba"},
            follow=True
        )
    messages = list(get_messages(response.wsgi_request))
    assert any("Ocurrió un inconveniente al verificar la seguridad. Intentá nuevamente más tarde." in str(message) for message in messages)


# Test para probar el error en envio de mail por ocurrencia de error en proceso de validación de recaptcha
@pytest.mark.django_db
def test_error_tecnico_validacion_envio_mail(client,paginas_indice_visitantes):
    with patch("app_contacto.views.requests.post", side_effect=Exception("Error al tratar de validar")):
        response = client.post(reverse("app_contacto:enviar_mail_personalizado"),
            {"g-recaptcha-response": "fake-token","nombre_completo": "Nombre Apellido", "email":"email@hotmail.com", "telefono":"345678", "consulta":"Esta es una consulta de prueba"},
            follow=True
        )
    messages = list(get_messages(response.wsgi_request))
    assert any("No se pudo verificar la seguridad por un inconveniente técnico. Por favor, intentá nuevamente en unos minutos." in str(message) for message in messages)


# Test para probar el error de la falta del token en envío de mail
@pytest.mark.django_db
def test_error_token_recaptcha_envio_mail(client,paginas_indice_visitantes):
    with patch("app_contacto.views.requests.post") as mock_recaptcha, \
         patch("app_contacto.views.EmailMultiAlternatives.send") as mock_send:
        # Simula captcha válido
        mock_recaptcha.return_value.json.return_value = {"success": True}
        # Simula envío exitoso de mail
        mock_send.return_value = 0
        response = client.post(reverse("app_contacto:enviar_mail_personalizado"),
            {"nombre_completo": "Nombre Apellido", "email":"email@hotmail.com", "telefono":"345678", "consulta":"Esta es una consulta de prueba"},
            follow=True
        )
    assert response.status_code == 200
    messages = list(get_messages(response.wsgi_request))
    assert any("Completá la verificación de seguridad." in str(message) for message in messages)


# Test para probar el error en envío de mail en alguna parte del proceso
@pytest.mark.django_db
def test_error_envio_mail(client,paginas_indice_visitantes):
    with patch("app_contacto.views.requests.post") as mock_recaptcha, \
         patch("app_contacto.views.EmailMultiAlternatives.send") as mock_send:
        # Simula captcha válido
        mock_recaptcha.return_value.json.return_value = {"success": True}
        # Simula envío exitoso de mail
        mock_send.return_value = 0
        response = client.post(reverse("app_contacto:enviar_mail_personalizado"),
            {"g-recaptcha-response": "fake-token","nombre_completo": "Nombre Apellido", "email":"email@hotmail.com", "telefono":"345678", "consulta":"Esta es una consulta de prueba"},
            follow=True
        )
    messages = list(get_messages(response.wsgi_request))
    assert any("No se ha podido enviar el correo a causa de un error" in str(message) for message in messages)
