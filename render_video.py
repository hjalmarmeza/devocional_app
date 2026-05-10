import os
import subprocess
import json
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

# --- CONFIGURACIÓN ---
JSON_PATH = "devocionales_2026.json"
IMGS_DIR = "publicaciones"
MUSIC_DIR = "musica mp3"
ASSETS_DIR = "assets/fondos"
OUTPUT_DIR = "shorts"
FONT_PATH = "assets/fonts/base_font.ttf"

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

def get_music_file(month_num):
    meses = {
        "05": "Mayo", "06": "Junio", "07": "Julio", "08": "Agosto",
        "09": "Setiembre", "10": "Octubre", "11": "Noviembre", "12": "Diciembre"
    }
    prefix = meses.get(month_num)
    if not prefix: return None
    
    if os.path.exists(MUSIC_DIR):
        for file in os.listdir(MUSIC_DIR):
            if file.startswith(prefix):
                return os.path.join(MUSIC_DIR, file)
    return None

def render_short(fecha):
    p1 = os.path.join(IMGS_DIR, f"{fecha}_P1.png")
    p2 = os.path.join(IMGS_DIR, f"{fecha}_P2.png")
    month_num = fecha.split("-")[1]
    
    # --- MOTOR DE FONDOS DINÁMICOS ---
    bg_dir = "assets/backgrounds_devocional"
    fallback_bg = os.path.join(ASSETS_DIR, f"{month_num}.png")
    
    potential_bgs = []
    if os.path.exists(bg_dir):
        for root, dirs, files in os.walk(bg_dir):
            for file in files:
                if file.endswith(".mp4"):
                    potential_bgs.append(os.path.join(root, file))
    
    selected_bg = potential_bgs[0] if potential_bgs else fallback_bg
    is_video = selected_bg.endswith(".mp4")
    print(f"🌍 Fondo seleccionado: {selected_bg}")
        
    # Crear Outro Transparente Dinámico
    outro_overlay = os.path.join(IMGS_DIR, f"{fecha}_OUTRO_OVERLAY.png")
    img_outro = Image.new("RGBA", (1024, 1024), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img_outro)
    # Rectángulo de cristal para el cierre
    draw.rounded_rectangle([200, 400, 824, 624], radius=30, fill=(0, 0, 0, 180))
    try: font = ImageFont.truetype(FONT_PATH, 50)
    except: font = ImageFont.load_default()
    txt = "Suscríbete y camina en fe"
    bbox = draw.textbbox((0,0), txt, font=font)
    draw.text(((1024-(bbox[2]-bbox[0]))/2, 480), txt, font=font, fill="white")
    img_outro.save(outro_overlay)
        
    logo_animado = os.path.join(ASSETS_DIR, "logo animado/Logo Hjalmar Animado.mp4")
    music = get_music_file(month_num)
    
    if not os.path.exists(p1) or not os.path.exists(p2) or not music:
        print(f"❌ Faltan archivos para {fecha} (P1, P2 o Música)")
        return

    output_video = os.path.join(OUTPUT_DIR, f"{fecha}_short.mp4")
    
    # Configurar entrada de fondo
    input_bg_args = ["-stream_loop", "-1", "-i", selected_bg] if is_video else ["-loop", "1", "-i", selected_bg]
    
    # Filtro Cinematográfico Pro
    filter_complex = (
        f"[0:v]scale=1080*1.5:-1,zoompan=z='zoom+0.0002':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1080x1920:fps=30,setsar=1[bg];"
        f"[1:v]format=rgba,fade=t=in:st=0:d=1:alpha=1,fade=t=out:st=10:d=1:alpha=1[c1];"
        f"[2:v]format=rgba,fade=t=in:st=11:d=1:alpha=1,fade=t=out:st=21:d=1:alpha=1[c2];"
        f"[3:v]format=rgba,fade=t=in:st=22:d=1:alpha=1,fade=t=out:st=27:d=1:alpha=1[c3];"
        f"[4:v]colorkey=black:0.1:0.1,scale=800:-1,fade=t=in:st=22:d=1:alpha=1[logo];"
        f"[bg][c1]overlay=(W-w)/2:(H-h)/2[v1];"
        f"[v1][c2]overlay=(W-w)/2:(H-h)/2[v2];"
        f"[v2][c3]overlay=(W-w)/2:(H-h)/2[v3];"
        f"[v3][logo]overlay=(W-w)/2:(H-h)/2-150[v]"
    )

    cmd = ["ffmpeg", "-y"] + input_bg_args + [
        "-i", p1, 
        "-i", p2, 
        "-i", outro_overlay, 
        "-stream_loop", "-1", "-i", logo_animado, 
        "-i", music, 
        "-filter_complex", filter_complex, 
        "-map", "[v]", "-map", "5:a", 
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-shortest", 
        "-t", "28", 
        output_video
    ]
    
    subprocess.run(cmd)
    print(f"🎬 Short finalizado con éxito: {output_video}")

if __name__ == "__main__":
    today = datetime.now().strftime("%Y-%m-%d")
    
    if os.path.exists(JSON_PATH):
        with open(JSON_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for item in data:
                if item['fecha'] == today:
                    render_short(item['fecha'])
    else:
        print(f"❌ No se encontró el archivo JSON: {JSON_PATH}")
