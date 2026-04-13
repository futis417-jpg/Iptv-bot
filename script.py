import requests
import os
import re
import concurrent.futures
import time

# --- DATOS DEL CANAL ---
TOKEN = "8718780006:AAHXJl8aS26q84i0mPopgVx5wZQG4JCvFwk"
CHAT_ID = "@iptvlinkspro"

# User-Agents reales de Smart TV para saltar protecciones
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (SmartTV; Linux; Tizen 5.0) AppleWebkit/537.36 (KHTML, like Gecko) SamsungBrowser/2.2 Chrome/63.0.3239.111 TV Safari/537.36'
}

def test_calidad_xtream(url):
    """Prueba si la cuenta tiene slots libres y contenido de calidad"""
    try:
        # Probamos una conexión real con timeout alto para servidores pesados
        with requests.get(url, headers=HEADERS, timeout=15, stream=True) as r:
            if r.status_code == 200:
                # Bajamos los primeros 150KB para analizar el ADN de la lista
                raw_data = r.raw.read(150000).decode('utf-8', errors='ignore').upper()
                
                if "#EXTM3U" not in raw_data:
                    return None

                # Analizador de contenido (Fútbol de España es prioridad 1)
                score = 0
                category = "GENERAL"
                
                # Buscamos rastro de canales Pro de España
                esp_keywords = ["MOVISTAR", "DAZN", "LALIGA", "CHAMPIONS", "M.+", "ESPAÑA", "SPAIN"]
                if any(x in raw_data for x in esp_keywords):
                    score += 50
                    category = "FUTBOL"
                
                # Buscamos rastro de Cine/Series Premium
                vod_keywords = ["NETFLIX", "HBO", "DISNEY", "APPLE TV", "PRIME VIDEO", "4K", "ULTRA HD"]
                if any(x in raw_data for x in vod_keywords):
                    score += 30
                    if category != "FUTBOL": category = "CINE"

                # Si la lista es muy pequeña, es basura
                if len(raw_data) < 5000: return None

                return {"url": url, "cat": category, "score": score}
    except:
        return None
    return None

def mega_buscador():
    """Rastreador de paneles Xtream en sitios de filtración masiva"""
    found_urls = set()
    # Fuentes de donde salen los links tipo Telelatino que me pasaste
    targets = [
        "https://www.referido.top",
        "https://pastebin.com/raw/uS9q6Se7",
        "https://pastebin.com/raw/8YpYqL6a",
        "https://www.google.com/search?q=%22get.php%3Fusername%3D%22+%22password%3D%22+iptv+2026",
        "https://raw.githubusercontent.com/vps01box/AM-IPTV/main/lista.m3u",
        "http://visuales.xyz"
    ]

    # Expresión regular para cazar links Xtream exactos
    pattern = r'https?://[^\s<>"]+:[0-9]*/get\.php\?username=[^\s&<>"]+&password=[^\s&<>"]+&type=m3u_plus'

    for t in targets:
        try:
            r = requests.get(t, headers=HEADERS, timeout=10)
            matches = re.findall(pattern, r.text)
            found_urls.update(matches)
        except: continue
    
    return list(found_urls)

def enviar_telegram_vip(resultados):
    if not resultados: return

    # Separamos lo mejor de lo mejor
    futbol = sorted([r for r in resultados if r['cat'] == "FUTBOL"], key=lambda x: x['score'], reverse=True)
    cine = sorted([r for r in resultados if r['cat'] == "CINE"], key=lambda x: x['score'], reverse=True)
    general = [r for r in resultados if r['cat'] == "GENERAL"]

    msg = f"Selection **IPTV ELITE SYSTEM** Selection\n"
    msg += f"👑 *Status: VIP ACTIVE | {time.strftime('%H:%M')}*\n"
    msg += "━━━━━━━━━━━━━━━━━━━━\n\n"

    if futbol:
        msg += "⚽️ **DIRECTO FÚTBOL ESPAÑA (TOP)**\n"
        for i, item in enumerate(futbol[:12], 1):
            msg += f"{i}️⃣ `{item['url']}`\n\n"
    
    msg += "━━━━━━━━━━━━━━━━━━━━\n\n"

    if cine:
        msg += "🍿 **CINE & SERIES (CALIDAD 4K)**\n"
        for i, item in enumerate(cine[:8], 1):
            msg += f"{i}️⃣ `{item['url']}`\n\n"

    msg += "━━━━━━━━━━━━━━━━━━━━\n"
    msg += "📢 *Servidor verificado. Actualización automática cada 3h.*\n"
    msg += "🚀 @iptvlinkspro"

    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                  data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown", "disable_web_page_preview": "true"})

if __name__ == "__main__":
    links = mega_buscador()
    finales = []
    # Usamos 12 hilos para máxima estabilidad de red en GitHub
    with concurrent.futures.ThreadPoolExecutor(max_workers=12) as executor:
        results = executor.map(test_calidad_xtream, links)
        for r in results:
            if r: finales.append(r)
    
    enviar_telegram_vip(finales)
