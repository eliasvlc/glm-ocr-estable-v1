import base64
import json
import requests
from pathlib import Path
from PIL import Image

# ── Configuración (hardcoded) ─────────────────────────────────────
URL = "http://127.0.0.1:8080/v1/chat/completions"  # endpoint del servidor
IMAGE_PATH = "dni1.jpg"                            # ruta de la imagen
TIMEOUT = 300                                      # timeout en segundos


def format_img(imagen_path):
    imagen_path = Path(imagen_path)

    imagen_fija_path = imagen_path.parent / f"f_{imagen_path.stem}.jpg"

    with Image.open(imagen_path) as img:
        img_rgb = img.convert("RGB")
        img_rgb.save(imagen_fija_path, "JPEG")

    return str(imagen_fija_path)


def image_to_data_url(path):
    """Lee una imagen y la convierte a data URL base64 (JPEG)."""
    data = Path(path).read_bytes()                          # leer bytes del archivo
    encoded = base64.b64encode(data).decode("utf-8")        # codificar en base64
    return f"data:image/jpeg;base64,{encoded}"              # formatear data URL


def build_payload(image_url):
    """Construye el payload JSON para el endpoint chat/completions."""
    prompt = """ocr, resultado como json, modelo json: {
                    "dni": "",
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


def main():
    """Orquesta el flujo completo: imagen → payload → request → salida."""
    image_path=format_img(IMAGE_PATH)
    image_url = image_to_data_url(image_path)               # 1. imagen a data URL
    payload = build_payload(image_url)                      # 2. construir payload
    result = send_request(payload)                          # 3. enviar y recibir
    print_full_response(result)                             # 4. imprimir todo
    print_model_content(result)                             # 5. imprimir contenido


if __name__ == "__main__":
    main()                                                  # punto de entrada