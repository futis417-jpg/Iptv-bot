import requests
import os
import re
import concurrent.futures
import time

# --- CONFIGURACIÓN TOTAL ---
TOKEN = "8718780006:AAHXJl8aS26q84i0mPopgVx5wZQG4JCvFwk"
CHAT_ID = "@iptvlinkspro"

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def validar_y_clasificar(url):
    """Verifica si el link funciona y si tiene contenido de España/Fútbol"""
    try:
        r = requests.get(url, headers=HEADERS, timeout=8, stream=True)
        if r.status_code == 200:
            content = r.raw.read(2000).decode('utf-8', errors='ignore').upper()
            if "#EXTM3U" in content:
                # Puntuación de calidad: Si tiene España o Deporte, va primero
                prioridad = 0
                if any(x in content for x in ["SPAIN", "ESPAÑA", "MOVISTAR", "LALIGA", "DAZN", "FUTBOL"]):
                    prioridad = 1
                return (url, prioridad)
    except:
        return None
    return None

def rastrear_sitios_oscuros():
    """Busca en sitios donde se suben listas temporales de fútbol"""
    enlaces = set()
    
    # Webs que recopilan listas m3u a diario
    motores = [
        "https://www.telegra.ph/IPTV-SPAIN-FREE-04-13",
        "https://pastebin.com/raw/8YpYqL6a",
        "https://iptv-org.github.io/iptv/countries/es.m3u", # España oficial
        "https://raw.githubusercontent.com/vps01box/AM-IPTV/main/lista.m3u",
        "https://raw.githubusercontent.com/pizofm/Latino/master/Lista.m3u",
        "https://raw.githubusercontent.com/Guydun/IPTV/main/All_Channels.m3u",
        "https://www.google.com/search?q=filetype:m3u+spain+2026" # Dorking
    ]

    for url in motores:
        try:
            r = requests.get(url, headers=HEADERS, timeout=10)
            # Buscador de patrones m3u/m3u8 en el texto
            encontrados = re.findall(r'https?://[^\s<>"]+\.m3u[8]?', r.text)
            enlaces.update(encontrados)
        except:
            continue
    return list(enlaces)

def enviar_telegram_pro(listas):
    if not listas:
        return
    
    # Ordenar por prioridad (las de fútbol/España primero)
    listas.sort(key=lambda x: x[1], reverse=True)
    
    ahora = time.strftime("%H:%M")
    msg = f"🛰 **RASTREO AVANZADO COMPLETADO** ({ahora})\n"
    msg += "━━━━━━━━━━━━━━━━━━━━\n"
    msg += "🇪🇸 **FOCO: ESPAÑA & FÚTBOL TOTAL** ⚽️\n\n"
    
    # Enviar las mejores 20
    for i, (link, prio) in enumerate(listas[:25], 1):
        emoji = "⭐️" if prio == 1 else "✅"
        msg += f"{emoji} **LISTA {i}:**\n`{link}`\n\n"
        
        # Telegram tiene límite de caracteres, si el mensaje es muy largo lo cortamos
        if len(msg) > 3800:
            break

    msg += "━━━━━━━━━━━━━━━━━━━━\n"
    msg += "📺 **TIP:** Si una no carga el fútbol, prueba la siguiente. ¡Hay 25 opciones!"

    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                  data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown", "disable_web_page_preview": "true"})

def main():
    print("🕵️‍♂️ Buscando en la internet profunda...")
    candidatos = rastrear_sitios_oscuros()
    
    print(f"🔬 Validando {len(candidatos)} fuentes encontradas...")
    validos = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=40) as executor:
        resultados = executor.map(validar_y_clasificar, candidatos)
        for res in resultados:
            if res:
                validos.append(res)
    
    enviar_telegram_pro(validos)

if __name__ == "__main__":
    main()
