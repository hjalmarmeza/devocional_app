import json
import os
from PIL import Image, ImageDraw, ImageFont
import textwrap

# --- CONFIGURACIÓN ESTRATÉGICA POR MES (CALIBRACIÓN AL MILÍMETRO) ---
# Formato: "mes": (x1, y1, x2, y2)
CALIBRACION = {
    "default": (180, 340, 844, 705),
    "05": (180, 340, 844, 705), # Mayo
    "06": (180, 340, 844, 705), # Junio
    "07": (240, 395, 750, 635), # Julio (Ajustado al cristal de la Lira)
    "08": (220, 255, 770, 500), # Agosto (Shofar - cristal más arriba)
    "09": (180, 320, 825, 680), # Septiembre (Biblia)
    "10": (175, 400, 825, 600), # Octubre (Altar - cristal horizontal central)
    "11": (280, 335, 860, 695), # Noviembre (Trigo)
    "12": (180, 280, 820, 675), # Diciembre (Pesebre)
}

# --- CONFIGURACIÓN DE RUTAS ---
ASSETS_DIR = "assets/fondos"
JSON_PATH = "devocionales_2026.json"
OUTPUT_DIR = "publicaciones"
FONT_PATH = "assets/fonts/base_font.ttf"
DEFAULT_BG = "05.png"

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

def get_text_height(draw, text_lines, font, spacing):
    return len(text_lines) * (font.size + spacing)

def draw_styled_text(draw, text, font, fill, y_start, width_chars):
    lines = textwrap.wrap(text, width=width_chars)
    current_y = y_start
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        w = bbox[2] - bbox[0]
        draw.text(((1024 - w) / 2, current_y), line, font=font, fill=fill)
        current_y += font.size + 12
    return current_y

def generar_imagenes_premium():
    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        devocionales = json.load(f)

    import datetime
    today = datetime.date.today().strftime("%Y-%m-%d")
    
    # Filtrar solo para hoy
    hoy_data = [d for d in devocionales if d['fecha'] == today]
    
    if not hoy_data:
        print(f"⚠️ No hay devocional programado para hoy ({today})")
        return

    for item in hoy_data:
        # ... (resto del código igual)
        # Determinar el mes para el fondo (formato MM.png)
        mes = item['fecha'].split("-")[1]
        bg_path = os.path.join(ASSETS_DIR, f"{mes}.png")
        
        if not os.path.exists(bg_path):
            bg_path = os.path.join(ASSETS_DIR, DEFAULT_BG)
            
        print(f"🎨 Usando fondo: {bg_path} para {item['fecha']}")

        # Obtener calibración para el mes
        x1, y1, x2, y2 = CALIBRACION.get(mes, CALIBRACION["default"])
        rect_width = x2 - x1
        rect_height = y2 - y1
        center_y = y1 + (rect_height / 2)

        # --- PANTALLA 1: VERSÍCULO ---
        img1 = Image.open(bg_path).convert("RGBA")
        draw1 = ImageDraw.Draw(img1)
        
        font_ref = ImageFont.truetype(FONT_PATH, 55)
        font_body = ImageFont.truetype(FONT_PATH, 44)
        
        ref_lines = textwrap.wrap(item['versiculo'], width=22)
        body_lines = textwrap.wrap(f"\"{item['texto']}\"", width=32)
        
        total_h = get_text_height(draw1, ref_lines, font_ref, 15) + get_text_height(draw1, body_lines, font_body, 12) + 20
        y_cursor = center_y - (total_h / 2)

        # Dibujar Referencia en Dorado Suave
        y_cursor = draw_styled_text(draw1, item['versiculo'], font_ref, (218, 165, 32), y_cursor, 25)
        y_cursor += 10
        # Dibujar Texto en Blanco
        draw_styled_text(draw1, f"\"{item['texto']}\"", font_body, (255, 255, 255), y_cursor, 40)

        img1.save(f"{OUTPUT_DIR}/{item['fecha']}_P1.png")

        # --- PANTALLA 2: REFLEXIÓN ---
        img2 = Image.open(bg_path).convert("RGBA")
        draw2 = ImageDraw.Draw(img2)
        
        font_title = ImageFont.truetype(FONT_PATH, 52)
        font_reflect = ImageFont.truetype(FONT_PATH, 38)

        ref_body_lines = textwrap.wrap(item['reflexion'], width=35)
        total_h2 = get_text_height(draw2, [item['titulo']], font_title, 20) + get_text_height(draw2, ref_body_lines, font_reflect, 10) + 20
        y_cursor2 = center_y - (total_h2 / 2)

        # Dibujar Título
        y_cursor2 = draw_styled_text(draw2, item['titulo'], font_title, (218, 165, 32), y_cursor2, 28)
        y_cursor2 += 20
        # Dibujar Reflexión
        draw_styled_text(draw2, item['reflexion'], font_reflect, (255, 255, 255), y_cursor2, 35)

        img2.save(f"{OUTPUT_DIR}/{item['fecha']}_P2.png")
        
        print(f"✨ Generada versión PREMIUM para el {item['fecha']}")

if __name__ == "__main__":
    generar_imagenes_premium()
