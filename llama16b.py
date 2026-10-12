import base64
import json
import requests
from pathlib import Path
from PIL import Image

from functools import wraps
import time

def medir_tiempo(func):
    """Decorador que calcula el tiempo de ejecución de una función."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        inicio = time.perf_counter()
        resultado = func(*args, **kwargs)
        duracion = time.perf_counter() - inicio
        print(f"{func.__name__}() -> {duracion:.4f} s")
        return resultado
    return wrapper

# ── Configuración (hardcoded) ─────────────────────────────────────
URL = "http://127.0.0.1:8080/v1/chat/completions"  # endpoint del servidor
                     # ruta de la imagen
TIMEOUT = 300                                      # timeout en segundos


# def format_img(imagen_path):
#     imagen_path = Path(imagen_path)

#     imagen_fija_path = imagen_path.parent / f"f_{imagen_path.stem}.jpg"

#     with Image.open(imagen_path) as img:
#         img_rgb = img.convert("RGB")
#         img_rgb.save(imagen_fija_path, "JPEG")

#     return str(imagen_fija_path)

from pathlib import Path
from PIL import Image, ImageOps

def format_img(
    imagen_path,
    max_dimension=2200,
    jpeg_quality=92
):
    imagen_path = Path(imagen_path)
    imagen_fija_path = imagen_path.parent / f"f_{imagen_path.stem}.jpg"

    with Image.open(imagen_path) as img:
        # Corregir la orientación según los metadatos EXIF
        img = ImageOps.exif_transpose(img)

        # Evitar dimensiones excesivas, conservando la proporción
        img.thumbnail(
            (max_dimension, max_dimension),
            Image.Resampling.LANCZOS
        )

        # Convertir a RGB para garantizar compatibilidad con JPEG
        img_rgb = img.convert("RGB")

        # Guardar optimizado, sin metadatos innecesarios
        img_rgb.save(
            imagen_fija_path,
            format="JPEG",
            quality=jpeg_quality,
            optimize=True,
            progressive=False
        )

    return str(imagen_fija_path)


def image_to_data_url(path):
    """Lee una imagen y la convierte a data URL base64 (JPEG)."""
    data = Path(path).read_bytes()                          # leer bytes del archivo
    encoded = base64.b64encode(data).decode("utf-8")        # codificar en base64
    return f"data:image/jpeg;base64,{encoded}"              # formatear data URL


def build_payload(image_url):
    """Construye el payload JSON para el endpoint chat/completions."""
    prompt = """ocr, resultado como json, modelo json: {
                    "cui": "",
                    "primer_apellido": "",
                    "segundo_apellido": "",
                    "prenombres": "",
                    "sexo": "",
                    "estado_civil": "",
                    "fecha_nacimiento": "",
                    "ubigeo_nacimiento": "",
                    "fecha_emision": "",
                    "fecha_caducidad": "",
                    "grupo_votacion": "",
                    "donacion_organos": ""
                    }"""
    return {                                                # payload con imagen + texto
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": image_url}},  # imagen primero
                    {"type": "text", "text": prompt},                        # texto después
                ],
            }
        ],
        "stream": False,                                    # respuesta completa
        "response_format": {"type": "json_object"},         # forzar JSON
    }


def send_request(payload):
    """Envía el payload al endpoint y devuelve el JSON de respuesta."""
    print("Enviando petición...")                           # aviso por consola
    response = requests.post(URL, json=payload, timeout=TIMEOUT)  # POST al servidor
    print("HTTP:", response.status_code)                    # mostrar código HTTP
    response.raise_for_status()                             # lanzar error si 4xx/5xx
    return response.json()                                  # parsear respuesta


def print_full_response(result):
    """Imprime la respuesta completa formateada como JSON."""
    print("\nRESPUESTA COMPLETA:\n")
    print(json.dumps(result, indent=2, ensure_ascii=False))  # dump legible


def print_model_content(result):
    """Extrae e imprime el contenido devuelto por el modelo."""
    print("\nCONTENIDO DEL MODELO:\n")
    try:
        content = result["choices"][0]["message"]["content"]  # ruta esperada
        print(content)
    except Exception:
        print("No se pudo obtener choices[0].message.content")  # fallback


def main(image_path):
    """Orquesta el flujo completo: imagen → payload → request → salida."""
    f_image_path=format_img(image_path)
    image_url = image_to_data_url(f_image_path)               # 1. imagen a data URL
    payload = build_payload(image_url)                      # 2. construir payload
    result = send_request(payload)                          # 3. enviar y recibir
    # print_full_response(result)                             # 4. imprimir todo
    print_model_content(result)                             # 5. imprimir contenido



@medir_tiempo
def ejecutar():
    # Lista con las rutas de las imágenes
    # image_paths = ["dni3.jpg"]
    image_paths = ["dni1.jpg", "dni2.jpg", "dni3.jpg", "dni4.jpg", "dni6.jpg"]



    # Recorrer la lista elemento por elemento
    for image_path in image_paths:
        print(f"=== Procesando: {image_path} ===")
        response = main(image_path=image_path)
        print(response)
        print("-" * 40)  # Separador visual entre resultados
                                                        # punto de entrada


ejecutar()