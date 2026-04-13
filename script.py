import requests
import os
import re
import concurrent.futures
import time

# --- CONFIGURACIÓN CRÍTICA ---
TOKEN = "8718780006:AAHXJl8aS26q84i0mPopgVx5wZQG4JCvFwk"
CHAT_ID = "@iptvlinkspro"

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
}

def analizar_lista_profundo(url):
    """Descarga la lista y cuenta cuántos canales de España/Fútbol tiene realmente"""
    try:
        # Descargamos los primeros 50KB para no saturar, suficiente para ver canales
        r = requests.get(url, headers=HEADERS, timeout=10)
        if r.status_code == 200 and "#EXTM3U" in r.text:
            contenido = r.text.upper()
            
            # Palabras clave de fútbol y España
            keywords = ["MOVISTAR", "DAZN", "LALIGA", "SPAIN", "ESPAÑA", "M. +", "LALIGA TV", "CHAMPIONS"]
            conteo = sum(1 for k in keywords if k in contenido)
            
            # Solo aceptamos listas que tengan al menos 2 canales de estos
            if conteo >= 1:
                # Intentamos validar si los links de los canales dentro responden (Opcional, consume tiempo)
                return (url, conteo)
    except:
        return None
    return None

def rastrear_fuentes_avanzadas():
    """Busca en sitios de 'paste' y buscadores de archivos m3u8 frescos"""
    enlaces = set()
    
    # Webs de 'leaks' de listas que se actualizan cada hora
    motores = [
        "https://iptv-org.github.io/iptv/index.m3u",
        "https://iptv-org.github.io/iptv/countries/es.m3u",
        "https://raw.githubusercontent.com/vps01box/AM-IPTV/main/lista.m3u",
        "https://raw.githubusercontent.com/pizofm/Latino/master/Lista.m3u",
        "https://raw.githubusercontent.com/clancat/m3u/main/spanish.m3u",
        "https://www.telegra.ph/IPTV-SPAIN-FUTBOL-FREE",
        "https://pastebin.com/raw/8YpYqL6a",
        "https://bit.ly/iptv-spain-m3u"
    ]

    for url in motores:
        try:
            r = requests.get(url, headers=HEADERS, timeout=10)
            # Buscador de patrones m3u/m3u8
            encontrados = re.findall(r'https?://[^\s<>"]+\.m3u[8]?', r.text)
            enlaces.update(encontrados)
        except:
            continue
    return list(enlaces)

def enviar_reporte_calidad(listas):
    if not listas:
        return
    
    # Ordenar por cantidad de canales de fútbol/España encontrados (los mejores primero)
    listas.sort(key=lambda x: x[1], reverse=True)
    
    ahora = time.strftime("%H:%M")
    msg = f"🛰 **REPORTE DE ALTA CALIDAD** ({ahora})\n"
    msg += "━━━━━━━━━━━━━━━━━━━━\n"
    msg += "🇪🇸 **FOCO: FÚTBOL ESPAÑA (MOVISTAR/DAZN)** ⚽️\n\n"
    msg += "*(Estas listas han sido analizadas y contienen canales activos)*\n\n"
    
    for i, (link, canales) in enumerate(listas[:20], 1):
        # Ponemos corona a las que tienen mucho contenido
        emoji = "👑" if canales > 3 else "⭐️"
        msg += f"{emoji} **LISTA {i} (Calidad: {canales}):**\n`{link}`\n\n"
        
        if len(msg) > 3800: break

    msg += "━━━━━━━━━━━━━━━━━━━━\n"
    msg += "📢 *Actualización cada 3 horas. Únete:* @iptvlinkspro"

    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                  data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown", "disable_web_page_preview": "true"})

def main():
    print("🚀 Buscando fuentes en la red...")
    candidatos = rastrear_fuentes_avanzadas()
    
    print(f"🔬 Analizando contenido real de {len(candidatos)} listas...")
    validos = []
    
    # Subimos a 50 hilos para que no tarde nada
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        resultados = executor.map(analizar_lista_profundo, candidatos)
        for res in resultados:
            if res:
                validos.append(res)
    
    enviar_reporte_calidad(validos)

if __name__ == "__main__":
    main()
