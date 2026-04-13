import requests
import os
import re
import concurrent.futures
import time
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# --- CONFIGURACIÓN DE ACCESO ---
TOKEN = "8718780006:AAHXJl8aS26q84i0mPopgVx5wZQG4JCvFwk"
CHAT_ID = "@iptvlinkspro"  # Tu canal

# Headers para saltar bloqueos de seguridad de las webs
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3',
}

def session_config():
    """Configura reintentos para que el bot no se rinda si una web va lenta"""
    s = requests.Session()
    retries = Retry(total=3, backoff_factor=0.2, status_forcelist=[500, 502, 503, 504])
    s.mount('https://', HTTPAdapter(max_retries=retries))
    return s

def validar_m3u_pro(url):
    """Verifica si el link es una lista m3u real y está online"""
    try:
        session = session_config()
        # Pedimos solo el inicio del archivo para ahorrar datos y tiempo
        with session.get(url, headers=HEADERS, timeout=12, stream=True) as r:
            if r.status_code == 200:
                first_line = next(r.iter_lines()).decode('utf-8', errors='ignore')
                if "#EXTM3U" in first_line:
                    return url
    except:
        return None
    return None

def rastrear_web_global():
    """Busca links en toda la web usando patrones de texto"""
    urls_encontradas = set()
    
    # 1. Repositorios de listas estables
    urls_encontradas.update([
        "https://iptv-org.github.io/iptv/index.m3u",
        "https://iptv-org.github.io/iptv/languages/spa.m3u",
        "https://raw.githubusercontent.com/teleriumtv/m3u/master/list.m3u",
        "https://raw.githubusercontent.com/vps01box/AM-IPTV/main/lista.m3u",
        "https://raw.githubusercontent.com/pizofm/Latino/master/Lista.m3u",
        "https://raw.githubusercontent.com/funcotv/funcotv/main/free.m3u",
        "https://raw.githubusercontent.com/LaQuay/TDTChannels/master/lists/tv.m3u8"
    ])

    # 2. Scrapeo de sitios temporales (Donde se sube el fútbol)
    fuentes_web = [
        "https://www.telegra.ph/LISTAS-IPTV-DIARIAS-04-13",
        "https://pastebin.com/archive" 
    ]

    for sitio in fuentes_web:
        try:
            r = requests.get(sitio, headers=HEADERS, timeout=10)
            # Buscamos links que terminen en m3u o m3u8
            links = re.findall(r'https?://[^\s<>"]+\.m3u[8]?', r.text)
            urls_encontradas.update(links)
        except:
            continue
            
    return list(urls_encontradas)

def enviar_reporte(listas):
    """Formatea el mensaje y lo envía al canal de Telegram"""
    if not listas:
        msg = "⚠️ *Aviso:* No se han encontrado nuevas listas estables en este rastreo."
    else:
        ahora = time.strftime("%H:%M")
        msg = f"🚀 **¡NUEVAS LISTAS DETECTADAS!** ({ahora})\n"
        msg += "━━━━━━━━━━━━━━━━━━━━\n"
        msg += "⚽️ *Canales de Fútbol, Cine y TV Premium:*\n\n"
        
        # Enviamos máximo 10 links para no saturar
        for i, link in enumerate(listas[:12], 1):
            msg += f"✅ **LISTA {i}:**\n`{link}`\n\n"
            
        msg += "━━━━━━━━━━━━━━━━━━━━\n"
        msg += "📺 **Instrucciones IBBO Player:**\n"
        msg += "1️⃣ Toca el link de arriba (se copiará).\n"
        msg += "2️⃣ Abre Ibbo Player > Add Playlist.\n"
        msg += "3️⃣ Pega el link en 'Remote Playlist'.\n\n"
        msg += "🔥 *¡Únete y comparte:* @iptvlinkspro"

    send_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": msg,
        "parse_mode": "Markdown",
        "disable_web_page_preview": "true"
    }
    requests.post(send_url, data=payload)

def main():
    print("🛰️ Iniciando sistema de rastreo IPTV Global...")
    print("🔍 Buscando en webs, foros y repositorios...")
    
    links_potenciales = rastrear_web_global()
    
    print(f"📡 Se han encontrado {len(links_potenciales)} candidatos. Validando...")
    
    validos = []
    # Usamos 30 hilos para validar todo en segundos
    with concurrent.futures.ThreadPoolExecutor(max_workers=30) as executor:
        resultados = executor.map(validar_m3u_pro, links_potenciales)
        for r in resultados:
            if r:
                validos.append(r)
    
    print(f"✅ Validación terminada. {len(validos)} listas listas para usar.")
    enviar_reporte(validos)

if __name__ == "__main__":
    main()
