import json
import re
import asyncio
from telethon import TelegramClient, errors

# --- CONFIGURACIÓN ---
API_ID = 31937146
API_HASH = 'cec9369855620dd376a75ff387eeecd0'

# ID del canal (El script intentará buscarlo en tus chats si falla el acceso directo)
# Asegúrate de que TU usuario está unido a este canal.
CHANNEL_ID_NUM = 1002474087426  # Ponemos el número base (sin el -100) para buscarlo mejor

OUTPUT_FILE = 'cineantiguo_telegram.json'

# --- FUNCIONES DE EXTRACCIÓN (Igual que antes) ---
def parse_message(text, message_id, channel_id):
    if not text: return None
    
    lines = text.split('\n')
    title = lines[0].strip().replace('*', '').replace('_', '') if lines else "Desconocido"

    movie = {
        "id": message_id,
        "title": title,
        "year": "", "duration": "", "director": "", "actors": "", "plot": "",
        "cover": "https://via.placeholder.com/300x450?text=Sin+Cover",
        # Reconstrucción del link para canales privados
        "telegramLink": f"https://t.me/c/{str(channel_id).replace('-100', '')}/{message_id}"
    }

    # Regex para datos
    year_match = re.search(r'(?:Año|Year|Estreno)[\s:]*(\d{4})', text, re.IGNORECASE)
    if year_match: movie["year"] = year_match.group(1)
    
    dur_match = re.search(r'(?:Duración|Duration|Tiempo)[\s:]*(.*?)(?:\n|$)', text, re.IGNORECASE)
    if dur_match: movie["duration"] = dur_match.group(1).strip()
    
    dir_match = re.search(r'(?:Director|Dir|Dirección)[\s:]*(.*?)(?:\n|$)', text, re.IGNORECASE)
    if dir_match: movie["director"] = dir_match.group(1).strip()
        
    act_match = re.search(r'(?:Reparto|Cast|Actores|Interpretes)[\s:]*(.*?)(?:\n|$)', text, re.IGNORECASE)
    if act_match: movie["actors"] = act_match.group(1).strip()
        
    plot_match = re.search(r'(?:Sinopsis|Argumento|Plot|Resumen)[\s:]*(.*)', text, re.IGNORECASE | re.DOTALL)
    if plot_match: movie["plot"] = plot_match.group(1).strip()
    elif len(text) > 100: movie["plot"] = text[:300] + "..."

    return movie

import json
import re
import asyncio
import traceback
from telethon import TelegramClient, errors

# --- CONFIGURACIÓN ---
API_ID = 31937146
API_HASH = 'cec9369855620dd376a75ff387eeecd0'

# Pon aquí el número tal cual lo tienes (sin signos raros)
# El script probará automáticamente las variantes necesarias (-100, etc.)
CHANNEL_ID_INPUT = 1002474087426 

OUTPUT_FILE = 'cineantiguo_telegram.json'

# --- FUNCIONES DE EXTRACCIÓN ROBUSTAS ---
def parse_message(text, message_id, channel_id):
    if not text: return None
    
    try:
        # Protección contra IndexError en el título
        lines = text.split('\n')
        title = "Desconocido"
        if lines and len(lines) > 0:
            title = lines[0].strip().replace('*', '').replace('_', '')
            if not title: title = "Sin Título"
        
        movie = {
            "id": message_id,
            "title": title,
            "year": "", "duration": "", "director": "", "actors": "", "plot": "",
            "cover": "https://via.placeholder.com/300x450?text=Sin+Cover",
            "telegramLink": f"https://t.me/c/{str(channel_id).replace('-100', '')}/{message_id}"
        }

        # Regex seguro
        year_match = re.search(r'(?:Año|Year|Estreno)[\s:]*(\d{4})', text, re.IGNORECASE)
        if year_match: movie["year"] = year_match.group(1)
        
        dur_match = re.search(r'(?:Duración|Duration|Tiempo)[\s:]*(.*?)(?:\n|$)', text, re.IGNORECASE)
        if dur_match: movie["duration"] = dur_match.group(1).strip()
        
        dir_match = re.search(r'(?:Director|Dir|Dirección)[\s:]*(.*?)(?:\n|$)', text, re.IGNORECASE)
        if dir_match: movie["director"] = dir_match.group(1).strip()
            
        act_match = re.search(r'(?:Reparto|Cast|Actores|Interpretes)[\s:]*(.*?)(?:\n|$)', text, re.IGNORECASE)
        if act_match: movie["actors"] = act_match.group(1).strip()
            
        plot_match = re.search(r'(?:Sinopsis|Argumento|Plot|Resumen)[\s:]*(.*)', text, re.IGNORECASE | re.DOTALL)
        if plot_match: movie["plot"] = plot_match.group(1).strip()
        elif len(text) > 50: movie["plot"] = text[:300] + "..."

        return movie
    except Exception as e:
        # Si un mensaje concreto falla, lo ignoramos y seguimos
        print(f"⚠️ Error leyendo mensaje {message_id}: {e}")
        return None

async def get_entity_safe(client, input_id):
    """Intenta encontrar el canal probando diferentes formatos de ID"""
    potential_ids = [
        input_id,                # Tal cual
        int(f"-100{input_id}"),  # Formato estándar canal privado
        int(f"-{input_id}")      # Formato grupo antiguo o si el user puso el 100
    ]
    
    print(f"🔍 Buscando canal (Probando variantes de ID: {input_id})...")
    
    for pid in potential_ids:
        try:
            entity = await client.get_entity(pid)
            print(f"✅ ¡Canal encontrado con ID: {pid}!")
            print(f"   Nombre: {getattr(entity, 'title', 'Desconocido')}")
            return entity
        except (ValueError, errors.ChannelPrivateError):
            continue
        except Exception:
            continue
            
    # Si falla el acceso directo, buscamos en la lista de chats
    print("⚠️ Acceso directo fallido. Buscando en tu lista de chats...")
    async for dialog in client.iter_dialogs():
        d_id_str = str(dialog.id)
        input_str = str(input_id)
        # Comprobar si el ID del input está contenido en el ID del chat
        if input_str in d_id_str:
            print(f"✅ ¡Canal encontrado en tus chats: {dialog.name} (ID: {dialog.id})!")
            return dialog.entity
            
    return None

async def main():
    print("------------------------------------------------")
    print("   EXTRACTOR DE CINE TELEGRAM (VERSIÓN SEGURA)  ")
    print("------------------------------------------------")
    
    async with TelegramClient('sesion_cine_segura', API_ID, API_HASH) as client:
        try:
            entity = await get_entity_safe(client, CHANNEL_ID_INPUT)
            
            if not entity:
                print("\n❌ ERROR: No se encuentra el canal.")
                print("SOLUCIÓN: Abre la app de Telegram y asegúrate de que estás UNIDO al canal.")
                return

            print("📥 Descargando películas...")
            movies_list = []
            count = 0
            
            # Usamos un iterador seguro
            async for message in client.iter_messages(entity, limit=None):
                if message.text:
                    movie_data = parse_message(message.text, message.id, entity.id)
                    if movie_data:
                        movies_list.append(movie_data)
                        count += 1
                        if count % 50 == 0:
                            print(f"   ...procesadas {count} fichas")
            
            print(f"\n🎉 ¡TERMINADO! {len(movies_list)} películas extraídas.")
            
            with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
                json.dump(movies_list, f, ensure_ascii=False, indent=2)
            
            print(f"💾 Archivo guardado: {OUTPUT_FILE}")
            
        except Exception as e:
            print(f"\n❌ Ocurrió un error inesperado:")
            traceback.print_exc()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"Error fatal: {e}")