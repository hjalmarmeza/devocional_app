import os
import json
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# Scopes necesarios para subir videos
SCOPES = ['https://www.googleapis.com/auth/youtube.upload', 'https://www.googleapis.com/auth/youtube']

def get_new_token():
    # Ruta al archivo de credenciales que encontramos
    creds_path = '../MusiChris-Studio/credentials.json'
    
    if not os.path.exists(creds_path):
        print(f"❌ Error: No se encontró {creds_path}")
        return

    flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
    # Esto abrirá el navegador en tu Mac
    creds = flow.run_local_server(port=0)

    # Convertir a JSON
    token_data = {
        'token': creds.token,
        'refresh_token': creds.refresh_token,
        'token_uri': creds.token_uri,
        'client_id': creds.client_id,
        'client_secret': creds.client_secret,
        'scopes': creds.scopes
    }

    print("\n" + "="*50)
    print("🚀 ¡TOKEN GENERADO CON ÉXITO!")
    print("Copia el siguiente bloque JSON y pégalo en el Secret YOUTUBE_TOKEN de GitHub:")
    print("="*50 + "\n")
    print(json.dumps(token_data, indent=2))
    print("\n" + "="*50)

if __name__ == "__main__":
    try:
        get_new_token()
    except Exception as e:
        print(f"❌ Error durante la autenticación: {e}")
        print("Asegúrate de tener instalado: pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client")
