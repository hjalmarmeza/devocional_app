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
        draw.text(((1080 - w) / 2, current_y), line, font=font, fill=fill)
        current_y += font.size + 12
    return current_y

def generar_imagenes_premium():
    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        devocionales = json.load(f)
        print(f"📦 [SISTEMA] Base de datos JSON cargada: {len(devocionales)} devocionales detectados.")

    import datetime
    today = datetime.date.today().strftime("%Y-%m-%d")
    
    # Prioridad: 1. Hoy, 2. El primer pendiente
    hoy_data = [d for d in devocionales if d['fecha'] == today]
    if not hoy_data:
        print(f"ℹ️ No se encontró fecha exacta para {today}. Buscando el primer pendiente...")
        pendientes = [d for d in devocionales if not d.get('publicado', False)]
        if pendientes:
            hoy_data = [pendientes[0]]
            print(f"✅ Procesando pendiente del: {hoy_data[0]['fecha']}")
    
    if not hoy_data:
        print(f"⚠️ No hay devocionales pendientes en el JSON.")
        return

    for item in hoy_data:
        # --- CONFIGURACIÓN DE LIENZO VERTICAL (1080x1920) ---
        W, H = 1080, 1920
        
        for i in range(1, 3): # Pantalla 1 (Versículo) y Pantalla 2 (Reflexión)
            img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            
            # 1. DIBUJAR TÍTULO EN 2 LÍNEAS (Parte Superior)
            try:
                font_title_main = ImageFont.truetype(FONT_PATH, 100)
                font_title_sub = ImageFont.truetype(FONT_PATH, 80)
            except Exception as e:
                print(f"⚠️ Fuente no encontrada en generador: {e}. Usando fuentes de emergencia.")
                try:
                    font_title_main = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 100)
                    font_title_sub = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 80)
                except:
                    font_title_main = ImageFont.load_default(size=80)
                    font_title_sub = ImageFont.load_default(size=60)
            
            # "DEVOCIONAL"
            t1 = "DEVOCIONAL"
            bbox1 = draw.textbbox((0, 0), t1, font=font_title_main)
            draw.text(((W - (bbox1[2]-bbox1[0]))/2, 150), t1, font=font_title_main, fill=(255, 255, 255, 255), stroke_width=2, stroke_fill="black")
            
            # "DIARIO"
            t2 = "DIARIO"
            bbox2 = draw.textbbox((0, 0), t2, font=font_title_sub)
            draw.text(((W - (bbox2[2]-bbox2[0]))/2, 260), t2, font=font_title_sub, fill=(218, 165, 32, 255), stroke_width=1, stroke_fill="black")

            # 2. MARCO DE CRISTAL CENTRAL
            m_x1, m_y1, m_x2, m_y2 = 100, 500, 980, 1400
            # Aumentamos la opacidad para asegurar visibilidad
            draw.rounded_rectangle([m_x1, m_y1, m_x2, m_y2], radius=50, fill=(0, 0, 0, 200), outline=(255, 255, 255, 80), width=4)
            
            # 3. CONTENIDO DINÁMICO
            if i == 1: # P1: Versículo
                try:
                    f_ref = ImageFont.truetype(FONT_PATH, 65)
                    f_text = ImageFont.truetype(FONT_PATH, 50)
                except:
                    f_ref = ImageFont.load_default(size=50)
                    f_text = ImageFont.load_default(size=40)
                
                # Referencia
                ref_txt = item['versiculo']
                print(f"📝 Generando P1 para {item['fecha']}: {ref_txt}")
                lines_ref = textwrap.wrap(ref_txt, width=25)
                y_cursor = m_y1 + 80
                for line in lines_ref:
                    bw = draw.textbbox((0,0), line, font=f_ref)
                    draw.text(((W - (bw[2]-bw[0]))/2, y_cursor), line, font=f_ref, fill=(218, 165, 32, 255))
                    y_cursor += 80
                
                y_cursor += 40
                # Texto del versículo
                body_txt = f"\"{item['texto']}\""
                lines_body = textwrap.wrap(body_txt, width=30)
                for line in lines_body:
                    bw = draw.textbbox((0,0), line, font=f_text)
                    draw.text(((W - (bw[2]-bw[0]))/2, y_cursor), line, font=f_text, fill="white")
                    y_cursor += 65
                    
            else: # P2: Reflexión
                try:
                    f_title = ImageFont.truetype(FONT_PATH, 70)
                    f_refl = ImageFont.truetype(FONT_PATH, 45)
                except:
                    f_title = ImageFont.load_default(size=55)
                    f_refl = ImageFont.load_default(size=35)
                
                # Título de la reflexión
                refl_title = item['titulo']
                print(f"📖 Generando P2 para {item['fecha']}: {refl_title}")
                bw = draw.textbbox((0,0), refl_title, font=f_title)
                draw.text(((W - (bw[2]-bw[0]))/2, m_y1 + 80), refl_title, font=f_title, fill=(218, 165, 32, 255))
                
                # Cuerpo de la reflexión
                y_cursor = m_y1 + 200
                refl_txt = item['reflexion']
                lines_refl = textwrap.wrap(refl_txt, width=38)
                for line in lines_refl:
                    bw = draw.textbbox((0,0), line, font=f_refl)
                    draw.text(((W - (bw[2]-bw[0]))/2, y_cursor), line, font=f_refl, fill="white")
                    y_cursor += 55

            img.save(f"{OUTPUT_DIR}/{item['fecha']}_P{i}.png")
        
        print(f"✨ Capas 9:16 generadas para el {item['fecha']}")

if __name__ == "__main__":
    generar_imagenes_premium()
