import requests
import os
import re
import concurrent.futures
from bs4 import BeautifulSoup

# CONFIGURACIÓN
TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
}

def validar_m3u(url):
    """Verifica si el link es un archivo m3u real y está vivo"""
    try:
        # Algunos servidores bloquean peticiones HEAD, usamos GET limitado
        with requests.get(url, headers=HEADERS, timeout=10, stream=True) as r:
            if r.status_code == 200:
                # Leemos los primeros 100 bytes para buscar la firma EXTM3U
                chunk = r.raw.read(100).decode('utf-8', errors='ignore')
                if "#EXTM3U" in chunk or "EXTINF" in chunk:
                    return url
    except:
        return None
    return None

def buscar_en_la_web():
    """Busca links .m3u en sitios de intercambio de texto y buscadores"""
    urls_encontradas = set()
    
    # 1. Fuentes fijas de alta calidad (GitHub)
    urls_encontradas.update([
        "https://iptv-org.github.io/iptv/index.m3u",
        "https://iptv-org.github.io/iptv/languages/spa.m3u",
        "https://raw.githubusercontent.com/vps01box/AM-IPTV/main/lista.m3u",
        "https://raw.githubusercontent.com/pizofm/Latino/master/Lista.m3u"
    ])

    # 2. Rastreo en sitios de 'Paste' (donde se suben listas de fútbol diario)
    # Buscamos en sitios como Telegra.ph que se usa mucho para IPTV
    queries = ["https://telegra.ph/IPTV-Spain-M3U", "https://pastebin.com/raw/8YpYqL6a"] # Ejemplos
    
    # 3. Simulación de búsqueda en sitios de listas actualizadas
    # Aquí el bot "escanea" webs que publican links m3u8
    webs_iptv = [
        "https://www.telegra.ph/LISTAS-IPTV-ACTUALIZADAS-04-13", # Ejemplo de fecha de hoy
    ]

    for web in webs_iptv:
        try:
            r = requests.get(web, headers=HEADERS, timeout=10)
            # Buscamos cualquier cosa que parezca un link m3u/m3u8 en el código fuente
            links = re.findall(r'https?://[^\s<>"]+\.m3u[8]?', r.text)
            urls_encontradas.update(links)
        except:
            continue

    return list(urls_encontradas)

def main():
    print("🌐 Iniciando rastreo web global...")
    potenciales = buscar_en_la_web()
    
    validos = []
    # Validamos en paralelo para no tardar horas
    with concurrent.futures.ThreadPoolExecutor(max_workers=25) as executor:
        resultados = executor.map(validar_m3u, potenciales)
        for r in resultados:
            if r:
                validos.append(r)

    if validos:
        # Dividimos en categorías para el canal
        msg = "🌍 **RASTREO WEB IPTV COMPLETO** 🌍\n"
        msg += "*(Enlaces directos encontrados en webs y foros)*\n"
        msg += "━━━━━━━━━━━━━━━━━━━━\n"
        
        # Limitar a los 10 mejores para no saturar Telegram
        for link in validos[:12]:
            msg += f"📦 `{link}`\n\n"
            
        msg += "━━━━━━━━━━━━━━━━━━━━\n"
        msg += "🏆 *Fútbol, Canales Premium y TDT*\n"
        msg += "⚠️ *Usa estos links en tu IBBO Player ahora.*"
    else:
        msg = "⚠️ No se han encontrado nuevas listas en la web en este momento."

    # Enviar a Telegram
    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                  data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown", "disable_web_page_preview": "true"})

if __name__ == "__main__":
    main()
