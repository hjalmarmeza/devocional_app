import json
import os
from PIL import Image, ImageDraw, ImageFont
import textwrap

# --- CONFIGURACIÓN DE ÁREA (REPOSITORIO DE CRISTAL) ---
# Basado en la imagen de 1024x1024
RECT_X1, RECT_Y1 = 180, 340
RECT_X2, RECT_Y2 = 844, 705
RECT_WIDTH = RECT_X2 - RECT_X1
RECT_HEIGHT = RECT_Y2 - RECT_Y1
CENTER_X = 512
CENTER_Y = RECT_Y1 + (RECT_HEIGHT / 2)

# --- CONFIGURACIÓN DE RUTAS ---
ASSETS_DIR = "Devocional/assets/fondos"
JSON_PATH = "Devocional/devocionales_2026.json"
OUTPUT_DIR = "Devocional/publicaciones"
FONT_PATH = "Devocional/assets/fonts/base_font.ttf"
DEFAULT_BG = "05.png" # Mayo como backup

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

    for item in devocionales:
        # Determinar el mes para el fondo (formato MM.png)
        mes = item['fecha'].split("-")[1]
        bg_path = os.path.join(ASSETS_DIR, f"{mes}.png")
        
        if not os.path.exists(bg_path):
            bg_path = os.path.join(ASSETS_DIR, DEFAULT_BG)
            
        print(f"🎨 Usando fondo: {bg_path} para {item['fecha']}")

        # --- PANTALLA 1: VERSÍCULO ---
        img1 = Image.open(bg_path).convert("RGBA")
        draw1 = ImageDraw.Draw(img1)
        
        font_ref = ImageFont.truetype(FONT_PATH, 45)  # Referencia (Salmo...)
        font_body = ImageFont.truetype(FONT_PATH, 32) # Texto bíblico
        
        # Calcular altura total para centrar verticalmente en el cristal
        ref_lines = textwrap.wrap(item['versiculo'], width=25)
        body_lines = textwrap.wrap(f"\"{item['texto']}\"", width=40)
        
        total_h = get_text_height(draw1, ref_lines, font_ref, 15) + get_text_height(draw1, body_lines, font_body, 12) + 20
        y_cursor = CENTER_Y - (total_h / 2)

        # Dibujar Referencia en Dorado Suave
        y_cursor = draw_styled_text(draw1, item['versiculo'], font_ref, (218, 165, 32), y_cursor, 25)
        y_cursor += 10
        # Dibujar Texto en Blanco
        draw_styled_text(draw1, f"\"{item['texto']}\"", font_body, (255, 255, 255), y_cursor, 40)

        img1.save(f"{OUTPUT_DIR}/{item['fecha']}_P1.png")

        # --- PANTALLA 2: REFLEXIÓN ---
        img2 = Image.open(bg_path).convert("RGBA")
        draw2 = ImageDraw.Draw(img2)
        
        font_title = ImageFont.truetype(FONT_PATH, 40)
        font_reflect = ImageFont.truetype(FONT_PATH, 28)

        ref_body_lines = textwrap.wrap(item['reflexion'], width=45)
        total_h2 = get_text_height(draw2, [item['titulo']], font_title, 20) + get_text_height(draw2, ref_body_lines, font_reflect, 10) + 20
        y_cursor2 = CENTER_Y - (total_h2 / 2)

        # Dibujar Título
        y_cursor2 = draw_styled_text(draw2, item['titulo'], font_title, (218, 165, 32), y_cursor2, 30)
        y_cursor2 += 15
        # Dibujar Reflexión
        draw_styled_text(draw2, item['reflexion'], font_reflect, (255, 255, 255), y_cursor2, 45)

        img2.save(f"{OUTPUT_DIR}/{item['fecha']}_P2.png")
        
        print(f"✨ Generada versión PREMIUM para el {item['fecha']}")

if __name__ == "__main__":
    generar_imagenes_premium()
