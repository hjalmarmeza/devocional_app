import os
import subprocess
import json
from datetime import datetime

# --- CONFIGURACIÓN ---
JSON_PATH = "Devocional/devocionales_2026.json"
IMGS_DIR = "Devocional/publicaciones"
MUSIC_DIR = "Devocional/musica mp3"
OUTPUT_DIR = "Devocional/shorts"

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

def render_short(fecha):
    p1 = os.path.join(IMGS_DIR, f"{fecha}_P1.png")
    p2 = os.path.join(IMGS_DIR, f"{fecha}_P2.png")
    month_num = fecha.split("-")[1]
    music = get_music_file(month_num)
    
    if not os.path.exists(p1) or not os.path.exists(p2) or not music:
        print(f"❌ Faltan archivos para {fecha}")
        return

    output_video = os.path.join(OUTPUT_DIR, f"{fecha}_short.mp4")
    
    # Comando FFmpeg para:
    # 1. P1 durante 5 seg, P2 durante 10 seg.
    # 2. Aplicar un crossfade de 1 segundo.
    # 3. Incluir el audio del mes.
    # 4. Formato vertical 1080x1920 (aunque las imágenes son cuadradas, las centraremos).
    
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-t", "6", "-i", p1,
        "-loop", "1", "-t", "11", "-i", p2,
        "-i", music,
        "-filter_complex", 
        "[0:v]scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,setsar=1,fade=t=out:st=5:d=1[v0];"
        "[1:v]scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,setsar=1,fade=t=in:st=0:d=1[v1];"
        "[v0][v1]concat=n=2:v=1:a=0[v]",
        "-map", "[v]", "-map", "2:a",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-shortest",
        "-t", "15",
        output_video
    ]
    
    subprocess.run(cmd)
    print(f"🎬 Short renderizado: {output_video}")

if __name__ == "__main__":
    with open(JSON_PATH, 'r') as f:
        data = json.load(f)
        for item in data:
            render_short(item['fecha'])
