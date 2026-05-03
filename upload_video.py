import os
import datetime
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
import json

def upload_to_youtube(video_path, title, description, tags):
    print(f"🚀 Iniciando motor de subida ministerial para: {video_path}")
    
    # Cargar credenciales desde variables de entorno (GitHub Secrets)
    creds_json = os.environ.get('YOUTUBE_CREDENTIALS')
    token_json = os.environ.get('YOUTUBE_TOKEN')
    
    if not creds_json or not token_json:
        print("❌ Error: Faltan secretos YOUTUBE_CREDENTIALS o YOUTUBE_TOKEN.")
        return

    # Parsear JSONs
    creds_data = json.loads(creds_json)
    token_data = json.loads(token_json)
    
    # Manejar si el token es solo el refresh_token
    if isinstance(token_data, str):
        token_data = {
            "refresh_token": token_data,
            "client_id": creds_data['installed']['client_id'],
            "client_secret": creds_data['installed']['client_secret'],
            "token_uri": "https://oauth2.googleapis.com/token"
        }

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
            'privacyStatus': 'public', # Publicación directa a las 7:00 AM España
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
    # Ejemplo de uso para el devocional de hoy
    today = datetime.date.today().strftime("%Y-%m-%d")
    path = f"Devocional/shorts/{today}_short.mp4"
    
    if os.path.exists(path):
        upload_to_youtube(
            video_path=path,
            title=f"Devocional Diario {today} #Shorts",
            description="🌬️ Camina con fe hoy. Una palabra de victoria para tu vida.\n\n#Shorts #Fe #Cristiano",
            tags=["Devocional", "MusiChris", "Fe"]
        )
    else:
        print(f"⚠️ Archivo no encontrado: {path}")
