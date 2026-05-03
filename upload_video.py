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
            'privacyStatus': 'unlisted',
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

if __name__ == "__main__":
    today = datetime.date.today().strftime("%Y-%m-%d")
    path = f"shorts/{today}_short.mp4"
    json_path = "devocionales_2026.json"
    
    # Intentar obtener datos dinámicos del JSON
    title_yt = f"Palabra de Vida - {today} #Shorts"
    desc_yt = "🌬️ Recibe esta palabra de bendición hoy. #Shorts #Fe #Dios"
    
    if os.path.exists(json_path):
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for item in data:
                if item['fecha'] == today:
                    title_yt = f"{item['titulo']} | Musichris Studio #Shorts"
                    desc_yt = f"🔥 {item['titulo']}\n\n{item['reflexion'][:200]}...\n\n📖 Versículo: {item['versiculo']}\n\n✨ Únete a nuestra comunidad en Musichris Studio: @Musichris_Studio\n\n#Shorts #Dios #Fe #Victoria #MusichrisStudio #Cristiano"
                    break

    if os.path.exists(path):
        upload_to_youtube(
            video_path=path,
            title=title_yt,
            description=desc_yt,
            tags=["Musichris Studio", "Devocional", "Fe", "Dios", "Victoria", "Cristiano", "Palabra de Vida"]
        )
    else:
        print(f"⚠️ Archivo no encontrado: {path}")
