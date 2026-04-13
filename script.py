import requests
import os
import re
import concurrent.futures
import time

# --- DATOS DE CONEXIÓN ---
TOKEN = "8718780006:AAHXJl8aS26q84i0mPopgVx5wZQG4JCvFwk"
CHAT_ID = "@iptvlinkspro"

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
}

def analizar_calidad_premium(url):
    """Analiza si la lista es pesada y completa (estilo TeleLatino)"""
    try:
        # Aumentamos el timeout porque las listas grandes tardan en responder
        r = requests.get(url, headers=HEADERS, timeout=20, stream=True)
        if r.status_code == 200:
            # Leemos un bloque grande para detectar calidad de metadatos (logos, grupos)
            text = r.raw.read(200000).decode('utf-8', errors='ignore').upper()
            
            if "#EXTM3U" not in text:
                return None

            # Puntuación de "Belleza" de la lista
            puntos = 0
            if "GROUP-TITLE" in text: puntos += 10  # Está organizada por categorías
            if "TVG-LOGO" in text: puntos += 10     # Tiene logos de canales
            if "MOVISTAR" in text or "DAZN" in text: puntos += 15 # Tiene fútbol pro
            if "NETFLIX" in text or "HBO" in text: puntos += 5   # Tiene pelis/series
            
            # Clasificación
            es_futbol = any(x in text for x in ["MOVISTAR", "DAZN", "LALIGA", "BEIN", "SKY SPORTS"])
            categoria = "⚽️ FÚTBOL & PREMIUM" if es_futbol else "🎬 CINE & SERIES PRO"
            
            # Solo enviamos listas con buena puntuación (mínimo 10 puntos)
            if puntos >= 10:
                return {"url": url, "cat": categoria, "puntos": puntos}
    except:
        return None
    return None

def recolectar_fuentes_elite():
    """Busca en servidores que alojan listas masivas"""
    links = set()
    fuentes = [
        "https://iptv-org.github.io/iptv/index.m3u",
        "https://raw.githubusercontent.com/vps01box/AM-IPTV/main/lista.m3u",
        "https://raw.githubusercontent.com/pizofm/Latino/master/Lista.m3u",
        "https://raw.githubusercontent.com/clancat/m3u/main/spanish.m3u",
        "https://raw.githubusercontent.com/teleriumtv/m3u/master/list.m3u",
        "https://raw.githubusercontent.com/funcotv/funcotv/main/free.m3u",
        "https://pastebin.com/raw/uS9q6Se7",
        "https://pastebin.com/raw/8YpYqL6a",
        "https://raw.githubusercontent.com/Kodi-Vigo/TV/master/peli.m3u", # Cine
        "https://raw.githubusercontent.com/Guydun/IPTV/main/All_Channels.m3u"
    ]
    
    for f in fuentes:
        try:
            r = requests.get(f, headers=HEADERS, timeout=10)
            found = re.findall(r'https?://[^\s<>"]+\.m3u[8]?', r.text)
            links.update(found)
        except: continue
    return list(links)

def enviar_telegram_estilo_premium(resultados):
    if not resultados: return

    # Separar y ordenar por puntos (las mejores arriba)
    futbol = sorted([r for r in resultados if "FÚTBOL" in r['cat']], key=lambda x: x['puntos'], reverse=True)
    cine = sorted([r for r in resultados if "CINE" in r['cat']], key=lambda x: x['puntos'], reverse=True)

    msg = f"💎 **IPTV PREMIUM STYLE** 💎\n"
    msg += f"✨ *Calidad Tele Latino | {time.strftime('%H:%M')}*\n"
    msg += "━━━━━━━━━━━━━━━━━━━━\n\n"

    # SECCIÓN FÚTBOL
    msg += "🏆 **TOP 10 FÚTBOL ESPAÑA**\n"
    for i, item in enumerate(futbol[:10], 1):
        msg += f"{i}️⃣ `{item['url']}`\n\n"

    msg += "━━━━━━━━━━━━━━━━━━━━\n\n"

    # SECCIÓN CINE Y SERIES
    msg += "🍿 **TOP 10 PELIS Y SERIES**\n"
    for i, item in enumerate(cine[:10], 1):
        msg += f"{i}️⃣ `{item['url']}`\n\n"

    msg += "━━━━━━━━━━━━━━━━━━━━\n"
    msg += "⭐ **TIP:** Estas listas tienen logos y categorías.\n"
    msg += "📲 @iptvlinkspro"

    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                  data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown", "disable_web_page_preview": "true"})

if __name__ == "__main__":
    candidatos = recolectar_fuentes_elite()
    finales = []
    # Usamos 15 hilos para no saturar y que el análisis sea profundo
    with concurrent.futures.ThreadPoolExecutor(max_workers=15) as executor:
        res = executor.map(analizar_calidad_premium, candidatos)
        for r in res:
            if r: finales.append(r)
    
    enviar_telegram_estilo_premium(finales)
