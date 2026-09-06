import os
import sys
import requests
from bs4 import BeautifulSoup

# URL del portal de afiliados de Amazon México
URL = "https://afiliados.amazon.com.mx/"
CLOSED_TEXT = "No estamos aceptando nuevos solicitantes"

# Leemos las credenciales desde los Secrets de GitHub Actions
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/118.0.0.0 Safari/537.36"
    )
}

def enviar_telegram(mensaje):
    """Envía un mensaje de texto a tu chat de Telegram."""
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("[ERROR] Faltan credenciales de Telegram. Revisa los Secrets de GitHub.")
        return
        
    url_api = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": mensaje,
        "parse_mode": "HTML"
    }
    try:
        requests.post(url_api, json=payload, timeout=10)
    except Exception as e:
        print(f"[ERROR] Falló el envío a Telegram: {e}")

def check_status():
    try:
        response = requests.get(URL, headers=HEADERS, timeout=15)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        page_text = soup.get_text()

        if CLOSED_TEXT in page_text:
            print("[INFO] Los registros siguen cerrados.")
            # Descomenta la siguiente línea si quieres que te notifique a Telegram cada media hora que sigue cerrado
            # enviar_telegram("ℹ️ <b>Amazon Afiliados</b>: Los registros siguen cerrados.")
        else:
            mensaje = f"🚨 <b>¡ATENCIÓN!</b> La página de registro de Amazon parece estar ACTIVA o ha cambiado.\n\n🔗 Revisa aquí: {URL}"
            print(mensaje)
            enviar_telegram(mensaje)
            sys.exit(1) # Genera una alerta visible de fallo en GitHub Actions

    except requests.RequestException as e:
        error_msg = f"⚠️ <b>[ERROR]</b> No se pudo acceder a la página de Amazon: {e}"
        print(error_msg)
        enviar_telegram(error_msg)
        sys.exit(1)

if __name__ == "__main__":
    check_status()
