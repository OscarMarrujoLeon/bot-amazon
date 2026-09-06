import os
import sys
import requests
from bs4 import BeautifulSoup

# URL del portal de afiliados de Amazon México
URL = "https://afiliados.amazon.com.mx/"
CLOSED_TEXT = "No estamos aceptando nuevos solicitantes"

# Leemos las credenciales (agregamos .strip() para evitar espacios en blanco invisibles)
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "").strip()
CHAT_ID = os.getenv("CHAT_ID", "").strip()

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/118.0.0.0 Safari/537.36"
    )
}

def enviar_telegram(mensaje):
    print("\n[LOG] Preparando envío de mensaje a Telegram...")
    
    # 1. Validar que GitHub sí esté inyectando las credenciales
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("[ERROR CRÍTICO] Las credenciales están vacías.")
        print(f"[DEBUG] TOKEN Detectado: {'SÍ' if TELEGRAM_TOKEN else 'NO'} | CHAT_ID Detectado: {'SÍ' if CHAT_ID else 'NO'}")
        return
        
    print(f"[DEBUG] Credenciales detectadas correctamente. CHAT_ID objetivo: {CHAT_ID}")
        
    url_api = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": mensaje,
        "parse_mode": "HTML"
    }
    
    # 2. Intentar el envío y capturar la respuesta cruda de Telegram
    try:
        print("[LOG] Conectando con la API de Telegram...")
        response = requests.post(url_api, json=payload, timeout=10)
        
        # Esto imprimirá el error exacto de Telegram (Ej: 400 Bad Request, 401 Unauthorized, etc.)
        print(f"[API TELEGRAM] Código HTTP: {response.status_code}")
        print(f"[API TELEGRAM] Respuesta: {response.text}")
        
        response.raise_for_status()
        print("[V] ¡Mensaje enviado y aceptado por Telegram con éxito!\n")
        
    except Exception as e:
        print(f"[ERROR] Excepción al procesar el envío: {e}\n")

def check_status():
    print("[LOG] Iniciando conexión con Amazon...")
    try:
        response = requests.get(URL, headers=HEADERS, timeout=15)
        response.raise_for_status()
        print("[LOG] Conexión exitosa. Analizando HTML de la página...")

        soup = BeautifulSoup(response.text, "html.parser")
        page_text = soup.get_text()

        if CLOSED_TEXT in page_text:
            print("[INFO] Resultado: Los registros siguen cerrados.")
            enviar_telegram("ℹ️ <b>Amazon Afiliados</b>: Los registros siguen cerrados.")
        else:
            mensaje = f"🚨 <b>¡ATENCIÓN!</b> La página de registro de Amazon parece estar ACTIVA o ha cambiado.\n\n🔗 Revisa aquí: {URL}"
            print("[INFO] Resultado: ¡CAMBIO DETECTADO!")
            enviar_telegram(mensaje)
            sys.exit(1)

    except requests.RequestException as e:
        error_msg = f"⚠️ <b>[ERROR]</b> No se pudo acceder a la página de Amazon: {e}"
        print(error_msg)
        enviar_telegram(error_msg)
        sys.exit(1)

if __name__ == "__main__":
    check_status()
