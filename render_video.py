import os
import subprocess
import json
from datetime import datetime

# --- CONFIGURACIÓN ---
JSON_PATH = "devocionales_2026.json"
IMGS_DIR = "publicaciones"
MUSIC_DIR = "musica mp3"
ASSETS_DIR = "assets/fondos"
OUTPUT_DIR = "shorts"

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

def get_music_file(month_num):
    # Diccionario de meses para mapear el número al inicio del nombre del archivo
    meses = {
        "05": "Mayo", "06": "Junio", "07": "Julio", "08": "Agosto",
        "09": "Setiembre", "10": "Octubre", "11": "Noviembre", "12": "Diciembre"
    }
    prefix = meses.get(month_num)
    if not prefix: return None
    
    for file in os.listdir(MUSIC_DIR):
        if file.startswith(prefix):
            return os.path.join(MUSIC_DIR, file)
    return None

from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

def add_outro_text(bg_path, output_path):
    img = Image.open(bg_path).convert("RGBA")
    draw = ImageDraw.Draw(img)
    w, h = img.size
    
    # Tapar áreas de texto original
    draw.rectangle([0, 0, w, 250], fill=(0,0,0,255))
    draw.rectangle([0, h-250, w, h], fill=(0,0,0,255))
    
    # Desenfoque más suave (20) como te gustaba
    img = img.filter(ImageFilter.GaussianBlur(radius=20))
    
    # Brillo más natural (0.9)
    enhancer = ImageEnhance.Brightness(img)
    img = enhancer.enhance(0.9)
    
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype(FONT_PATH, 55)
    except:
        font = ImageFont.load_default()
        
    text = "Suscríbete y caminemos juntos en fe"
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    
    # Dibujar sombra
    draw.text(((w-tw)/2 + 3, h/2 + 303), text, font=font, fill=(0,0,0,255))
    # Dibujar texto principal en Blanco Puro
    draw.text(((w-tw)/2, h/2 + 300), text, font=font, fill=(255, 255, 255))
    
    img.save(output_path)

def render_short(fecha):
    p1 = os.path.join(IMGS_DIR, f"{fecha}_P1.png")
    p2 = os.path.join(IMGS_DIR, f"{fecha}_P2.png")
    month_num = fecha.split("-")[1]
    
    # Fondo de cierre (usamos el mismo del mes como base para el blur cinemático)
    base_bg = os.path.join(ASSETS_DIR, f"{month_num}.png")
    if not os.path.exists(base_bg):
        base_bg = os.path.join(ASSETS_DIR, "05.png") # Backup
        
    outro_final = os.path.join(IMGS_DIR, f"{fecha}_OUTRO_FINAL.png")
    add_outro_text(base_bg, outro_final)
        
    logo_animado = os.path.join(ASSETS_DIR, "logo animado/Logo Hjalmar Animado.mp4")
    music = get_music_file(month_num)
    
    if not os.path.exists(p1) or not os.path.exists(p2) or not music:
        print(f"❌ Faltan archivos para {fecha}")
        return

    output_video = os.path.join(OUTPUT_DIR, f"{fecha}_short.mp4")
    
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-t", "11", "-i", p1,
        "-loop", "1", "-t", "11", "-i", p2,
        "-loop", "1", "-t", "8", "-i", outro_final,
        "-i", logo_animado,
        "-i", music,
        "-filter_complex", 
        "[0:v]scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,setsar=1,fade=t=out:st=10:d=1[v0];"
        "[1:v]scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,setsar=1,fade=t=in:st=0:d=1,fade=t=out:st=10:d=1[v1];"
        "[2:v]scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,setsar=1,fade=t=in:st=0:d=1[v2_base];"
        # Procesar Logo y eliminar la marca de agua "Veo" (estimada a la derecha del centro)
        "[3:v]colorkey=black:0.1:0.1,scale=850:-1,drawbox=x=iw-150:y=ih/2-50:w=150:h=100:color=black@0:t=fill[logo];"
        "[v2_base][logo]overlay=(W-w)/2:(H-h)/2-150[v2_final];"
        "[v0][v1][v2_final]concat=n=3:v=1:a=0[v]",
        "-map", "[v]", "-map", "4:a",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-shortest",
        "-t", "28",
        output_video
    ]
    
    subprocess.run(cmd)
    print(f"🎬 Short con cierre renderizado: {output_video}")

if __name__ == "__main__":
    # Asegurar que FONT_PATH esté disponible para drawtext
    global FONT_PATH
    FONT_PATH = "assets/fonts/base_font.ttf"
    
    today = datetime.now().strftime("%Y-%m-%d")
    
    with open(JSON_PATH, 'r') as f:
        data = json.load(f)
        for item in data:
            if item['fecha'] == today:
                render_short(item['fecha'])
