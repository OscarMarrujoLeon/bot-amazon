import os
import sys
import requests
from bs4 import BeautifulSoup

# URL del portal de afiliados de Amazon México
URL = "https://afiliados.amazon.com.mx/"

# Texto clave que indica que los registros están cerrados
CLOSED_TEXT = "No estamos aceptando nuevos solicitantes"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/118.0.0.0 Safari/537.36"
    )
}


def check_status():
    try:
        response = requests.get(URL, headers=HEADERS, timeout=15)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        page_text = soup.get_text()

        if CLOSED_TEXT in page_text:
            print("[INFO] Los registros siguen cerrados.")
        else:
            print("🚨 ¡ATENCIÓN! La página de registro parece estar ACTIVA o ha cambiado.")
            # Si se ejecuta en GitHub Actions, genera una alerta visible en el build
            sys.exit(1)

    except requests.RequestException as e:
        print(f"[ERROR] No se pudo acceder a la página: {e}")


if __name__ == "__main__":
    check_status()
