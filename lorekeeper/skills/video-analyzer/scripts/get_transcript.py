#!/usr/bin/env python3
"""
get_transcript.py
Extrae la transcripción nativa de un video de YouTube usando Playwright.
También extrae metadatos básicos del video.

Uso:
    python get_transcript.py "https://www.youtube.com/watch?v=XXXXX"
    python get_transcript.py "https://www.youtube.com/watch?v=XXXXX" --lang es
    python get_transcript.py "https://www.youtube.com/watch?v=XXXXX" --output transcript.txt

Requiere:
    pip install playwright
    playwright install chromium
"""

import argparse
import json
import re
import sys
import time
from pathlib import Path


def extract_video_id(url: str) -> str | None:
    """Extrae el ID del video de una URL de YouTube."""
    patterns = [
        r"(?:v=|\/)([0-9A-Za-z_-]{11}).*",
        r"(?:youtu\.be\/)([0-9A-Za-z_-]{11})",
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


def get_youtube_transcript(url: str, lang: str = "es") -> dict:
    """
    Extrae transcripción y metadatos de un video de YouTube.
    
    Returns:
        dict con keys: title, channel, duration, upload_date, 
                       description, transcript, transcript_available, lang_used
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("ERROR: Playwright no está instalado.")
        print("Instala con: pip install playwright && playwright install chromium")
        sys.exit(1)

    result = {
        "title": None,
        "channel": None,
        "duration": None,
        "upload_date": None,
        "description": None,
        "url": url,
        "video_id": extract_video_id(url),
        "transcript": None,
        "transcript_available": False,
        "lang_used": None,
        "error": None,
    }

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            locale="es-MX",
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        )
        page = context.new_page()

        try:
            # Cargar el video
            print(f"Cargando video: {url}")
            page.goto(url, wait_until="domcontentloaded", timeout=30000)
            time.sleep(3)

            # Aceptar cookies si aparece el diálogo
            try:
                accept_btn = page.locator("button:has-text('Accept'), button:has-text('Aceptar')").first
                if accept_btn.is_visible(timeout=3000):
                    accept_btn.click()
                    time.sleep(1)
            except Exception:
                pass

            # Extraer título
            try:
                title = page.locator("h1.ytd-video-primary-info-renderer").inner_text(timeout=5000)
                result["title"] = title.strip()
                print(f"Título: {result['title']}")
            except Exception:
                try:
                    title = page.title()
                    result["title"] = title.replace(" - YouTube", "").strip()
                except Exception:
                    pass

            # Extraer canal
            try:
                channel = page.locator("ytd-channel-name a").first.inner_text(timeout=5000)
                result["channel"] = channel.strip()
            except Exception:
                pass

            # Extraer descripción (primeras líneas)
            try:
                # Expandir descripción
                expand_btn = page.locator("tp-yt-paper-button#expand").first
                if expand_btn.is_visible(timeout=2000):
                    expand_btn.click()
                    time.sleep(1)
                desc = page.locator("ytd-text-inline-expander").inner_text(timeout=5000)
                result["description"] = desc[:500].strip() if desc else None
            except Exception:
                pass

            # ── Obtener transcripción ──────────────────────────────────────
            # Método 1: YouTube Transcript API interna
            # YouTube carga los datos de transcripción en el JS de la página
            try:
                content = page.content()
                
                # Buscar timedtext en el contenido de la página
                caption_pattern = r'"captionTracks":\[([^\]]+)\]'
                caption_match = re.search(caption_pattern, content)
                
                if caption_match:
                    tracks_raw = "[" + caption_match.group(1) + "]"
                    # Limpiar para parsear
                    tracks_raw = tracks_raw.replace('\\"', '"')
                    
                    # Extraer URLs de las pistas disponibles
                    url_pattern = r'"baseUrl":"(https://www\.youtube\.com/api/timedtext[^"]+)"'
                    lang_pattern = r'"languageCode":"([^"]+)"'
                    
                    urls = re.findall(url_pattern, tracks_raw)
                    langs = re.findall(lang_pattern, tracks_raw)
                    
                    if urls:
                        # Preferir el idioma solicitado, luego español, luego el primero
                        selected_url = None
                        selected_lang = None
                        
                        for i, (u, l) in enumerate(zip(urls, langs)):
                            if l == lang:
                                selected_url = u
                                selected_lang = l
                                break
                        
                        if not selected_url and langs:
                            for i, (u, l) in enumerate(zip(urls, langs)):
                                if l.startswith("es"):
                                    selected_url = u
                                    selected_lang = l
                                    break
                        
                        if not selected_url:
                            selected_url = urls[0]
                            selected_lang = langs[0] if langs else "unknown"
                        
                        # Obtener la transcripción
                        transcript_page = context.new_page()
                        transcript_page.goto(selected_url + "&fmt=json3", timeout=15000)
                        transcript_content = transcript_page.content()
                        transcript_page.close()
                        
                        # Parsear el JSON de transcripción
                        json_match = re.search(r'\{.*\}', transcript_content, re.DOTALL)
                        if json_match:
                            transcript_data = json.loads(json_match.group())
                            
                            segments = []
                            for event in transcript_data.get("events", []):
                                if "segs" in event:
                                    text = "".join(
                                        seg.get("utf8", "") for seg in event["segs"]
                                    ).strip()
                                    if text and text != "\n":
                                        start_ms = event.get("tStartMs", 0)
                                        start_s = int(start_ms / 1000)
                                        minutes = start_s // 60
                                        seconds = start_s % 60
                                        segments.append(f"[{minutes:02d}:{seconds:02d}] {text}")
                            
                            if segments:
                                result["transcript"] = "\n".join(segments)
                                result["transcript_available"] = True
                                result["lang_used"] = selected_lang
                                print(f"✓ Transcripción extraída ({len(segments)} segmentos, idioma: {selected_lang})")

            except Exception as e:
                print(f"Método 1 falló: {e}")

            # Método 2: Usar el botón de transcripción en la UI
            if not result["transcript_available"]:
                try:
                    print("Intentando método 2: botón de transcripción...")
                    
                    # Buscar el menú de opciones del video
                    more_btn = page.locator("ytd-menu-renderer button").first
                    more_btn.click(timeout=5000)
                    time.sleep(1)
                    
                    # Buscar opción de transcripción
                    transcript_option = page.locator("text=Transcripción, text=Transcript").first
                    transcript_option.click(timeout=5000)
                    time.sleep(2)
                    
                    # Extraer segmentos de transcripción
                    segments = page.locator("ytd-transcript-segment-renderer").all()
                    
                    if segments:
                        lines = []
                        for seg in segments:
                            timestamp = seg.locator(".segment-timestamp").inner_text()
                            text = seg.locator(".segment-text").inner_text()
                            lines.append(f"[{timestamp.strip()}] {text.strip()}")
                        
                        result["transcript"] = "\n".join(lines)
                        result["transcript_available"] = True
                        result["lang_used"] = "detected"
                        print(f"✓ Transcripción extraída vía UI ({len(lines)} segmentos)")
                
                except Exception as e:
                    print(f"Método 2 falló: {e}")

        except Exception as e:
            result["error"] = str(e)
            print(f"ERROR general: {e}")
        
        finally:
            browser.close()

    return result


def format_output(data: dict) -> str:
    """Formatea el resultado para salida en texto."""
    lines = []
    lines.append("=" * 60)
    lines.append("METADATOS DEL VIDEO")
    lines.append("=" * 60)
    lines.append(f"Título:  {data.get('title', 'No disponible')}")
    lines.append(f"Canal:   {data.get('channel', 'No disponible')}")
    lines.append(f"URL:     {data.get('url', '')}")
    lines.append(f"ID:      {data.get('video_id', '')}")
    
    if data.get("description"):
        lines.append(f"\nDescripción:\n{data['description']}")
    
    lines.append("\n" + "=" * 60)
    lines.append("TRANSCRIPCIÓN")
    lines.append("=" * 60)
    
    if data.get("transcript_available"):
        lines.append(f"Idioma: {data.get('lang_used', 'desconocido')}\n")
        lines.append(data["transcript"])
    else:
        lines.append("TRANSCRIPCIÓN NO DISPONIBLE")
        lines.append("\nPosibles causas:")
        lines.append("- El video no tiene subtítulos generados")
        lines.append("- El video es privado o tiene restricciones")
        lines.append("- El creador desactivó las transcripciones")
        lines.append("\nAlternativa: Copia y pega el texto manualmente en Claude.")
        
        if data.get("error"):
            lines.append(f"\nError técnico: {data['error']}")
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Extrae transcripción de YouTube para el skill video-analyzer"
    )
    parser.add_argument("url", help="URL del video de YouTube")
    parser.add_argument(
        "--lang", default="es", 
        help="Código de idioma preferido (default: es)"
    )
    parser.add_argument(
        "--output", default=None,
        help="Archivo de salida (default: imprime en pantalla)"
    )
    parser.add_argument(
        "--json", action="store_true",
        help="Salida en formato JSON crudo"
    )
    
    args = parser.parse_args()
    
    # Validar URL
    if "youtube.com" not in args.url and "youtu.be" not in args.url:
        print("ERROR: La URL debe ser de YouTube")
        sys.exit(1)
    
    # Extraer transcripción
    data = get_youtube_transcript(args.url, lang=args.lang)
    
    # Formatear salida
    if args.json:
        output = json.dumps(data, ensure_ascii=False, indent=2)
    else:
        output = format_output(data)
    
    # Escribir o imprimir
    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
        print(f"✓ Guardado en: {args.output}")
    else:
        print(output)
    
    # Exit code: 0 si hay transcripción, 1 si no
    sys.exit(0 if data["transcript_available"] else 1)


if __name__ == "__main__":
    main()
