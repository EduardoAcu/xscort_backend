# utils.py
from io import BytesIO
from django.core.files import File
from PIL import Image
import os

def comprimir_imagen(image, max_width=1200):
    """
    Recibe un ImageFieldFile, lo redimensiona y lo convierte a WebP.
    Retorna un objeto File de Django listo para guardar.
    """
    if not image:
        return None

    # Abrir la imagen con Pillow
    img = Image.open(image)
    
    # Manejar transparencia (PNG) para evitar fondos negros si conviertes a RGB
    # WebP soporta transparencia, así que mantenemos RGBA si existe
    if img.mode in ('RGBA', 'LA'):
        # Si prefieres quitar transparencia y poner fondo blanco:
        # background = Image.new('RGB', img.size, (255, 255, 255))
        # background.paste(img, mask=img.split()[3])
        # img = background
        pass
    else:
        img = img.convert('RGB')

    # Redimensionar si es muy grande (manteniendo ratio)
    if img.width > max_width:
        ratio = max_width / float(img.width)
        height = int((float(img.height) * float(ratio)))
        img = img.resize((max_width, height), Image.Resampling.LANCZOS)

    # Guardar en memoria como WebP
    im_io = BytesIO()
    img.save(im_io, 'WEBP', quality=85, optimize=True)
    
    # Crear el nuevo nombre de archivo
    nombre_original = os.path.basename(image.name)
    nombre_sin_ext = os.path.splitext(nombre_original)[0]
    nuevo_nombre = f"{nombre_sin_ext}.webp"

    # Retornar el archivo compatible con Django
    new_image = File(im_io, name=nuevo_nombre)
    return new_image
