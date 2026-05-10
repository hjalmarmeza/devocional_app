import os
import datetime
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
import json

def upload_to_youtube(video_path, title, description, tags):
    print(f"🚀 Iniciando motor de subida ministerial para: {video_path}")
    
    # Cargar credenciales y token
    creds_json = os.environ.get('YOUTUBE_CREDENTIALS')
    token_json = os.environ.get('YOUTUBE_TOKEN')
    
    if not creds_json or not token_json:
        print("❌ Faltan secretos de YouTube")
        return

    creds_data = json.loads(creds_json)
    token_data = json.loads(token_json)
    
    # Extraer client_id y client_secret de las credenciales
    client_info = creds_data.get('installed') or creds_data.get('web') or creds_data
    
    # Asegurar que el token tenga lo necesario
    if 'client_id' not in token_data:
        token_data['client_id'] = client_info.get('client_id')
    if 'client_secret' not in token_data:
        token_data['client_secret'] = client_info.get('client_secret')
    if 'token_uri' not in token_data:
        token_data['token_uri'] = "https://oauth2.googleapis.com/token"

    credentials = Credentials.from_authorized_user_info(token_data)
    youtube = build('youtube', 'v3', credentials=credentials)

    body = {
        'snippet': {
            'title': title[:100],
            'description': description,
            'tags': tags,
            'categoryId': '22' # People & Blogs
        },
        'status': {
            'privacyStatus': os.environ.get('YOUTUBE_PRIVACY', 'public'),
            'selfDeclaredMadeForKids': False
        }
    }

    media = MediaFileUpload(video_path, chunksize=-1, resumable=True)
    
    request = youtube.videos().insert(
        part='snippet,status',
        body=body,
        media_body=media
    )

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"📊 Progreso: {int(status.progress() * 100)}%")

    print(f"✅ ¡GLORIA A DIOS! Video subido. ID: {response['id']}")
    print(f"🔗 URL: https://youtu.be/{response['id']}")
    return response['id']

def save_status(fecha, video_id):
    json_path = "devocionales_2026.json"
    if os.path.exists(json_path):
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        for item in data:
            if item['fecha'] == fecha:
                item['publicado'] = True
                item['youtube_id'] = video_id
                break
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print(f"💾 Estado actualizado en JSON para {fecha}")

if __name__ == "__main__":
    today = datetime.date.today().strftime("%Y-%m-%d")
    json_path = "devocionales_2026.json"
    
    # Valores por defecto
    title_yt = f"Palabra de Vida - {today} #Shorts"
    desc_yt = "🌬️ Recibe esta palabra de bendición hoy. #Shorts #Fe #Dios"
    tags_yt = ["MusiChris Devocional", "Fe", "Dios", "Cristiano"]
    
    target_item = None

    if os.path.exists(json_path):
        from ai_optimizer import get_ai_optimized_metadata
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            print(f"📦 [SISTEMA] Motor de Subida: {len(data)} devocionales detectados en base de datos.")
            
        # 1. Buscar hoy
        for item in data:
            if item['fecha'] == today:
                target_item = item
                break
        
        # 2. Si no hay hoy, buscar primer pendiente
        if not target_item:
            print(f"ℹ️ No se encontró devocional para {today}. Buscando primer pendiente...")
            for item in data:
                if not item.get('publicado', False):
                    target_item = item
                    break
    
    if not target_item:
        print("⚠️ No hay devocionales pendientes para procesar.")
        exit(0)

    # Verificar si ya se publicó (segunda capa de seguridad)
    if target_item.get('publicado', False):
        print(f"✅ El devocional de {target_item['fecha']} ya consta como publicado.")
        exit(0)

    # --- OPTIMIZACIÓN POR IA ---
    print(f"🧠 Optimizando metadatos por IA para: {target_item['titulo']}...")
    ai_meta = get_ai_optimized_metadata(target_item['reflexion'], target_item['versiculo'], target_item['titulo'])
    
    if ai_meta:
        title_yt = ai_meta.get('titulo', title_yt)
        desc_yt = f"🔥 {ai_meta.get('descripcion', desc_yt)}\n\n📖 Versículo: {target_item['versiculo']}\n\n✨ MusiChris Devocional: Tu dosis diaria de paz.\n\n#Shorts #Dios #Fe #MusiChrisDevocional"
        tags_yt = ai_meta.get('tags', tags_yt)
    else:
        title_yt = f"{target_item['titulo']} | MusiChris Devocional #Shorts"
        desc_yt = f"🔥 {target_item['titulo']}\n\n{target_item['reflexion'][:200]}...\n\n📖 Versículo: {target_item['versiculo']}\n\n✨ MusiChris Devocional: Tu dosis diaria de paz.\n\n#Shorts #Dios #Fe #MusiChrisDevocional"

    # Ruta del video
    video_path = f"shorts/{target_item['fecha']}_short.mp4"

    if os.path.exists(video_path):
        video_id = upload_to_youtube(
            video_path=video_path,
            title=title_yt,
            description=desc_yt,
            tags=tags_yt
        )
        if video_id:
            save_status(target_item['fecha'], video_id)
    else:
        print(f"❌ Archivo de video no encontrado: {video_path}")
