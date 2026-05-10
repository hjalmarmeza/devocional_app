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
        
    # Crear Outro Transparente Dinámico (Burbuja Premium)
    outro_overlay = os.path.join(IMGS_DIR, f"{fecha}_OUTRO_OVERLAY.png")
    img_outro = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img_outro)
    
    import urllib.request
    os.makedirs("assets/fonts", exist_ok=True)
    font_main = "assets/fonts/Montserrat-Bold.ttf"
    font_text = "assets/fonts/Montserrat-Medium.ttf"
    try:
        if not os.path.exists(font_main):
            urllib.request.urlretrieve("https://raw.githubusercontent.com/JulietaUla/Montserrat/master/fonts/ttf/Montserrat-Bold.ttf", font_main)
        if not os.path.exists(font_text):
            urllib.request.urlretrieve("https://raw.githubusercontent.com/JulietaUla/Montserrat/master/fonts/ttf/Montserrat-Medium.ttf", font_text)
            
        font_bubble = ImageFont.truetype(font_main, 55)
        font_sub = ImageFont.truetype(font_text, 45)
    except Exception as e: 
        print(f"⚠️ Error cargando fuente Premium: {e}. Usando fuente de emergencia.")
        font_bubble = font_sub = ImageFont.load_default(size=50)

    # 1. BURBUJA PREMIUM: "Caminemos Juntos En Fe"
    txt_bubble = "Caminemos Juntos En Fe"
    b_bbox = draw.textbbox((0,0), txt_bubble, font=font_bubble)
    b_w = b_bbox[2] - b_bbox[0]
    b_h = b_bbox[3] - b_bbox[1]
    
    # Dibujar la burbuja (Posición más baja para dejar espacio al logo)
    padding = 50
    bx1, by1 = (1080 - b_w)/2 - padding, 1100
    bx2, by2 = (1080 + b_w)/2 + padding, 1100 + b_h + padding
    
    # Fondo de cristal oscuro con borde dorado brillante
    draw.rounded_rectangle([bx1, by1, bx2, by2], radius=50, fill=(0, 0, 0, 210), outline=(218, 165, 32, 255), width=5)
    draw.text(((1080-b_w)/2, by1 + padding/2 - 5), txt_bubble, font=font_bubble, fill=(218, 165, 32, 255))
    
    # 2. LLAMADO A LA ACCIÓN (CTA)
    txt_cta = "SUSCRÍBETE PARA MÁS BENDICIÓN"
    c_bbox = draw.textbbox((0,0), txt_cta, font=font_sub)
    draw.text(((1080-(c_bbox[2]-c_bbox[0]))/2, by2 + 50), txt_cta, font=font_sub, fill="white")
    
    img_outro.save(outro_overlay)
        
    logo_animado = os.path.join(ASSETS_DIR, "logo animado/Logo Hjalmar Animado.mp4")
    music = get_music_file(month_num)
    
    if not os.path.exists(p1) or not os.path.exists(p2) or not music:
        print(f"❌ Faltan archivos para {fecha} (P1: {os.path.exists(p1)}, P2: {os.path.exists(p2)}, Música: {os.path.exists(music)})")
        return

    output_video = os.path.join(OUTPUT_DIR, f"{fecha}_short.mp4")
    
    # Configurar entrada de fondo
    input_bg_args = ["-stream_loop", "-1", "-i", selected_bg] if is_video else ["-loop", "1", "-i", selected_bg]
    
    # Filtro Cinematográfico Pro (Capas nativas 1080x1920)
    # 1. Procesamos el fondo (si es video no usamos zoompan complejo para evitar bugs)
    if is_video:
        bg_filter = f"[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1[bg];"
    else:
        bg_filter = f"[0:v]scale=1080*1.5:-1,zoompan=z='zoom+0.0005':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=900:s=1080x1920:fps=30,setsar=1[bg];"

    filter_complex = (
        f"{bg_filter}"
        f"[1:v]format=rgba,fade=t=in:st=0:d=1:alpha=1,fade=t=out:st=10:d=1:alpha=1[c1];"
        f"[2:v]format=rgba,fade=t=in:st=11:d=1:alpha=1,fade=t=out:st=21:d=1:alpha=1[c2];"
        f"[3:v]format=rgba,fade=t=in:st=22:d=1:alpha=1[c3];"
        f"[4:v]colorkey=black:0.1:0.1,scale=900:-1,fade=t=in:st=22:d=1:alpha=1[logo];"
        f"[bg][c1]overlay=0:0:enable='between(t,0,11)'[v1];"
        f"[v1][c2]overlay=0:0:enable='between(t,11,22)'[v2];"
        f"[v2][c3]overlay=0:0:enable='gt(t,22)'[v3];"
        f"[v3][logo]overlay=(W-w)/2:300:enable='gt(t,22)'[v]"
    )

    cmd = ["ffmpeg", "-y"] + input_bg_args + [
        "-loop", "1", "-i", p1, 
        "-loop", "1", "-i", p2, 
        "-loop", "1", "-i", outro_overlay, 
        "-stream_loop", "-1", "-i", logo_animado, 
        "-i", music, 
        "-filter_complex", filter_complex, 
        "-map", "[v]", "-map", "5:a", 
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-shortest", 
        "-t", "28", 
        output_video
    ]
    
    print(f"🎬 [DIAGNÓSTICO FFmpeg]: {' '.join(cmd)}")
    subprocess.run(cmd)
    print(f"🎬 Short finalizado con éxito: {output_video}")

if __name__ == "__main__":
    today = datetime.now().strftime("%Y-%m-%d")
    
    if os.path.exists(JSON_PATH):
        with open(JSON_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
            print(f"📦 [SISTEMA] Motor de Renderizado: {len(data)} fechas cargadas correctamente.")
            
            # Buscar hoy
            target = None
            for item in data:
                if item['fecha'] == today:
                    target = item
                    break
            
            # Si no hay hoy, buscar primer pendiente
            if not target:
                for item in data:
                    if not item.get('publicado', False):
                        target = item
                        print(f"ℹ️ Renderizando primer pendiente: {target['fecha']}")
                        break
            
            if target:
                render_short(target['fecha'])
            else:
                print("⚠️ No hay devocionales pendientes para renderizar.")
    else:
        print(f"❌ No se encontró el archivo JSON: {JSON_PATH}")
