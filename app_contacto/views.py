import os
import re
import requests
from email.mime.image import MIMEImage

from django.template.loader import render_to_string
from django.contrib import messages
from django.core.mail import EmailMultiAlternatives
from django.shortcuts import redirect, render
from django.utils.html import escape

from AppCompletaEjemploCMS import settings




# Vista para la página Contacto
def contacto(request):
    return render(request, 'contacto.html', {"RECAPTCHA_PUBLIC_KEY":settings.RECAPTCHA_PUBLIC_KEY})


# Vista para el envío de mails de consulta con carga de imagen usando recaptcha
def enviar_mail_personalizado(request):
    # Datos dinámicos
    if request.method == 'POST':

        # Verificar que exista el token
        recaptcha_response = request.POST.get('g-recaptcha-response')
        if not recaptcha_response:
            messages.error(
                request,
                "Completá la verificación de seguridad."
            )
            return redirect('app_contacto:contacto')

        # Verificar el reCaptcha
        try:
            r = requests.post(
                'https://www.google.com/recaptcha/api/siteverify',
                data={
                'secret': settings.RECAPTCHA_PRIVATE_KEY,
                'response': recaptcha_response
                },
                timeout=5
            )
            result = r.json()
        except:
            messages.error(
                request,
                "No se pudo verificar la seguridad por un inconveniente técnico. Por favor, intentá nuevamente en unos minutos."
            )
            return redirect('app_contacto:contacto')
        if not result.get('success'):
            messages.error(request, "Ocurrió un inconveniente al verificar la seguridad. Intentá nuevamente más tarde.")
            return redirect('app_contacto:contacto')

        # Si el captcha es válido, se sigue con la lógica del mail
        nombre_completo=escape(request.POST.get('nombre_completo',''))
        email_usuario = escape(request.POST.get('email',''))
        telefono = escape(request.POST.get('telefono',''))
        consulta=escape(request.POST.get('consulta',''))
        consulta_segura = re.sub(r'https?://\S+', '[enlace removido]', consulta)

        # Renderiza la plantilla con contexto
        html_content = render_to_string('email.html', {
            'nombre': nombre_completo,
            'telefono': telefono,
            'email': email_usuario,
            'consulta': consulta_segura,
            'cid_logo': 'logo_id'
        })

        # Email configurado con HTML
        email = EmailMultiAlternatives(
            subject=f'Consulta del sitio - {nombre_completo}',
            body='Tu cliente de correo no admite HTML.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[settings.DEFAULT_TO_EMAIL],
        )
        ruta_logo = os.path.join(settings.BASE_DIR, 'app_contacto','static', 'app_contacto', 'images', 'logo.png')
        with open(ruta_logo, 'rb') as img_file:
            imagen = MIMEImage(img_file.read())
            imagen.add_header('Content-ID', '<logo_id>')
            imagen.add_header('Content-Disposition', 'inline', filename='logo.png')
            email.attach(imagen)
        email.attach_alternative(html_content, "text/html")
        if email.send()>0:
            messages.success(request, "Correo enviado correctamente.")
        else:
            messages.error(request, "No se ha podido enviar el correo a causa de un error")
        return redirect('app_contacto:contacto')