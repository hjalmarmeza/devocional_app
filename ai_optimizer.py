import os
import requests
import json

def get_ai_optimized_metadata(reflexion, versiculo, titulo_original):
    print("🧠 Consultando a la IA para optimizar metadatos devocionales...")
    
    prompt = f"""
    Como experto en crecimiento de YouTube Cristiano y Psicología de Clic, optimiza el siguiente devocional.
    
    TÍTULO ORIGINAL: {titulo_original}
    VERSÍCULO: {versiculo}
    REFLEXIÓN: {reflexion}
    
    TU MISIÓN:
    1. Genera un TÍTULO (máx 100 caracteres) que use "Curiosidad" o "Beneficio Espiritual". Debe incitar a hacer clic inmediatamente sin ser clickbait engañoso. Usa 1 emoji.
    2. Genera una DESCRIPCIÓN que resuma la esencia en 2 líneas potentes y termine con una pregunta para generar comentarios.
    3. Genera 10 TAGS dinámicos.

    FORMATO DE SALIDA (ESTRICTO JSON):
    {{
        "titulo": "Nuevo Título",
        "descripcion": "Nueva descripción...",
        "tags": ["tag1", "tag2"]
    }}
    """

    # Jerarquía de Fallback
    endpoints = [
        {
            "name": "Cerebras",
            "url": "https://api.cerebras.ai/v1/chat/completions",
            "key": os.environ.get("CEREBRAS_API_KEY"),
            "model": "llama3.1-70b"
        },
        {
            "name": "DeepInfra",
            "url": "https://api.deepinfra.com/v1/openai/chat/completions",
            "key": os.environ.get("DEEPINFRA_API_KEY"),
            "model": "meta-llama/Meta-Llama-3.1-70B-Instruct"
        },
        {
            "name": "DeepSeek",
            "url": "https://api.deepseek.com/v1/chat/completions",
            "key": os.environ.get("DEEPSEEK_API_KEY"),
            "model": "deepseek-chat"
        }
    ]

    for provider in endpoints:
        if not provider["key"]: continue
        
        try:
            print(f"📡 Intentando con {provider['name']}...")
            response = requests.post(
                provider["url"],
                headers={"Authorization": f"Bearer {provider['key']}", "Content-Type": "application/json"},
                json={
                    "model": provider["model"],
                    "messages": [{"role": "system", "content": "Eres un experto en marketing ministerial y YouTube SEO."}, {"role": "user", "content": prompt}],
                    "response_format": {"type": "json_object"} if provider['name'] != "Cerebras" else None
                },
                timeout=15
            )
            
            if response.status_code == 200:
                content = response.json()['choices'][0]['message']['content']
                # Limpiar por si la IA devuelve markdown
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0]
                return json.loads(content)
                
        except Exception as e:
            print(f"❌ Error con {provider['name']}: {e}")

    print("⚠️ No se pudo contactar con ninguna IA, usando metadatos por defecto.")
    return None
