import asyncio
import logging
import json
import os
import re

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from groq import Groq
from datetime import datetime
from typing import List, Dict, Optional
from deep_translator import GoogleTranslator
from dataclasses import dataclass

API_Telegram = '' # Insert your Telegram Bot API key here
API_GROQ = "" # Insert your Groq API key here


# configurazione dei logging / logging configuration
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

logger = logging.getLogger(__name__)

# Lista IA disponibili / Available AI models
MODEL_LIST = [
    'llama-3.1-8b-instant',            #0
    'llama-3.3-70b-versatile',         #1
    'meta-llama/llama-guard-4-12b',    #2
    'openai/gpt-oss-120b',             #3
    'openai/gpt-oss-20b',              #4
    'whisper-large-v3',                #5
    'whisper-large-v3-turbo',          #6
    'meta-llama/llama-4-maverick-17b-128e-instruct',   #7
    'moonshotai/kimi-k2-instruct',     #8
    'playai-tts',                      #9
    'qwen/qwen3-32b'                   #10
    ]

MODEL_LIST_PRINT = [
    'llama-3.1-8b-instant → Meta',            #0
    'llama-3.3-70b-versatile → Meta',         #1
    'meta-llama/llama-guard-4-12b → Meta'   ,    #2
    'openai/gpt-oss-120b → OpenAI',             #3
    'openai/gpt-oss-20b → OpenAI',              #4
    'whisper-large-v3 → OpenAI',                #5
    'whisper-large-v3-turbo → OpenAI',          #6
    'meta-llama/llama-4-maverick-17b-128e-instruct → Meta',   #7
    'moonshotai/kimi-k2-instruct → MoonshotAI',     #8
    'playai-tts → PlayAI',                      #9
    'qwen/qwen3-32b → Alibaba Cloud'                   #10
    ]

SELECTED_MODEL = MODEL_LIST[10]  # Modello predefinito / Default model


#comandi disponibili / available commands
cmds = {
    '/start': '→ Avvia il bot',
    '/help': '→ Mostra questa guida',
    '/act': '→ attiva ascolto in Chat',
    '/deact': '→ disattiva ascolto in chat',
    '/ai': '→ risponde alla domanda anche se non è attivo',
    '/listmodel': '→ Mostra i modelli disponibili',
    '/setmodel': '→ Imposta un modello',
    '/listlang': '→ Esempi di lingue da selezionare',
    '/setlang': '→ Cambia lingua per le info',
    '/reset': '→ Resetta la chat',
}

supported_lang = [
                    "it",  # Italiano
                    "en",  # English
                    "es",  # Spanish
                    "ru",  # Russian
                    "hi",  # Hindi
                    "fr",  # French
                    "ar",  # Modern Standard Arabic
                    "bn",  # Bengali
                    "pt",  # Portuguese
                    "ur",  # Urdu
                    "id",  # Indonesian
                    "de",  # German
                    "ja",  # Japanese
                    "tr"  # Turkish
                    ]
    

# /setlang per cambiare lingua. Di default è in italiano / Setlang to change language. Default is italian
if not os.path.exists(".txt"):  # Scegli il percorso dove salvare il file lang.txt / Choose the path where to save lang.txt
    with open (".txt", "x") as f: #inserisci il percorso dove aprire il file lang.txt / insert the path where to open lang.txt
        with open (".txt", "w") as f:f.write("it")  #inserisci il percorso dove aprire il file lang.txt / insert the path where to open lang.txt

with open ("", "r") as f: lg = f.read() #inserisci il percorso dove aprire il file lang.txt / insert the path where to open lang.txt

SETTINGS_FILE = "" # Path to settings file (chat_states.json)

# Carica i settings / Load settings
def load_states():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Errore caricando chat_states.json: {e}")
            return {}
    return {}

# Salva i settings / Save settings
def save_states():
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(chat_states, f, indent=4, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Errore salvando chat_states.json: {e}")

setlang = lg
chat_states = load_states()
fantasy = 0.6
is_reset = False

# stato della chat per ogni utente / chat state for each user
def get_chat_state(chat_id):
    if str(chat_id) not in chat_states:
        chat_states[str(chat_id)] = {
            'listening': False,
            'model': SELECTED_MODEL,
            'lang': setlang,
            'history': [],
            'file_context': ""
        }
        save_states()
    return chat_states[str(chat_id)]

# formattazione risposta IA / format IA response
def clean_re(text: str) -> str:
    return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()

# funzione per ottenere data e ora attuali / function to get current date and time
def get_current_time():
    now = datetime.now()
    data = now.strftime(f'{"%d/%m/%Y"}-{"%H:%M:%S"}')
    return data

# funzione per tradurre messaggi del bot nella lingua selezionata / function to translate bot messages into the selected language
def translate_chat_bot(message_key, target_lang=setlang, *format_args):
    try:
        message = GoogleTranslator(source="it", target=target_lang).translate(message_key)
    
        if format_args:
            try:
                message = message.format(*format_args)
            except:
                pass
        return message
    except Exception as e:
        logging.error(f"Error: {e}")
        return message_key

# funzione per rilevare se il messaggio chiede l'ora o la data / funcion to detect if the message asks for time or date
def detect_time_or_date(user_msg: str, setlang: str) -> Optional[str]:
    try:
        translated = GoogleTranslator(source=setlang, target="it").translate(user_msg).lower()

        if "che ore sono" in translated or "che ora è" in translated:
            return "time"
        if "che giorno è oggi" in translated or "che giorno è" in translated:
            return "date"
    except Exception as e:
        logger.error(f"Error: {e}")
    return None
 
# comando /start 
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global setlang
    chat_id = update.effective_chat.id
    state = get_chat_state(chat_id)
    message_start = translate_chat_bot("Ciao! Sono un bot AI. Usa /help per le varie info", setlang)
    await update.message.reply_text(message_start)
    
# comando /help
async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global setlang
    chat_id = update.effective_chat.id
    state = get_chat_state(chat_id)
    for c, d in cmds.items():
        await update.message.reply_text(f"{c} {translate_chat_bot(d, state['lang'])}")

#comando /act
async def activate_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global setlang
    chat_id = update.effective_chat.id
    state = get_chat_state(chat_id)
    state["listening"] = True
    message = translate_chat_bot("Modalità ascolto attivata!", setlang)
    await update.message.reply_text(message)
    
#comando /deact
async def deactivate_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global setlang
    chat_id = update.effective_chat.id
    state = get_chat_state(chat_id)
    state["listening"] = False
    message = translate_chat_bot("Modalità ascolto disattivata!", setlang)
    await update.message.reply_text(message)

#def client Groq
def create_client() -> Groq:
    return Groq(api_key=API_GROQ)

#def groq_resp 
def groq_response(user_msg: str, model: str, identita: str = "Tu ti chiami Judy, un intelligenza artificiale utile e amichevole. Se non capisci, rispondi chiaramente che non hai capito. Parli in maniera chiara ed educata.", cronologia: list = []) -> str:
    global is_reset, fantasy
    if is_reset:
        cronologia.clear()
        is_reset = False

    client = create_client()
    messages = [{'role': 'system', 'content': identita}]
    messages.extend(cronologia)
    messages.append({'role': 'user', 'content': user_msg})
    
    try:
        chat_completions = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=fantasy
        )
        completed_re = chat_completions.choices[0].message.content
        return clean_re(completed_re)
    
    
    except Exception as e:
        logger.error(e)
        
# risposta automatica se attivo / automatic response if active
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global setlang
    chat_id = update.effective_chat.id
    state = get_chat_state(chat_id)
    if not state['listening']:
        return

    user_msg = update.message.text.lower()
    check = detect_time_or_date(user_msg, state['lang'])

    if check == "time":
        current_time = get_current_time()
        await update.message.reply_text(translate_chat_bot(f"Sono le {current_time}", setlang))
        return

    if check == "date":
        current_time = get_current_time()
        await update.message.reply_text(translate_chat_bot(f"Oggi è {current_time}", setlang))
        return
        
    await context.bot.send_chat_action(chat_id=chat_id, action="typing")
    try:
        response = groq_response(user_msg, state['model'], cronologia= state['history'])
        state['history'].append({'role': 'user', 'content': user_msg})
        state['history'].append({'role': 'assistant', 'content': response})
        save_states()
        await update.message.reply_text(response)

    except Exception as e:
        await update.message.reply_text(translate_chat_bot(f"Errore {e}", setlang))
    
#comando /ai
async def ai_chat (update: Update, context: ContextTypes.DEFAULT_TYPE):
    global setlang
    state = get_chat_state(update.effective_chat.id)
    user_msg = " ".join(context.args)
    if not user_msg:
        await update.message.reply_text(f"{translate_chat_bot(' Errore: Usa /ai [domanda]', setlang)}")
        return
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    response = groq_response(user_msg, state['model'])
    await update.message.reply_text(response)

#comando /listmodel
async def list_model(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global setlang
    chat_id = update.effective_chat.id
    state = get_chat_state(chat_id)

    await update.message.reply_text(f"{translate_chat_bot("Questi sono i modelli disponibili", setlang)}")
    for i, model in enumerate(MODEL_LIST_PRINT, 0):
        await update.message.reply_text(f"{i}: {model} ")
    
#comando /setmodel
async def set_model(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global setlang
    chat_id = update.effective_chat.id
    state = get_chat_state(chat_id)
    if not context.args:
        message = translate_chat_bot("Modello non valido! Usa il comando: /listmodel ", setlang)
        await update.message.reply_text(message)
        return
    try:
        model_num = int(context.args[0])
        if 0 <= model_num < len(MODEL_LIST):
            state['model'] = MODEL_LIST[model_num]
            save_states()
            message = translate_chat_bot(f"Modello impostato: {MODEL_LIST_PRINT[model_num]}", setlang)
            await update.message.reply_text(message)
        else:
            message = translate_chat_bot("Modello non valido! Usa il comando: /listmodel ", setlang)
            await update.message.reply_text(message)

    except:
        message = translate_chat_bot("Modello non valido! Usa il comando: /listmodel ", setlang)
        await update.message.reply_text(message)

# comando /listlang
async def list_lang(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global setlang
    chat_id = update.effective_chat.id
    state = get_chat_state(chat_id)
    await update.message.reply_text(f"{translate_chat_bot("Questi sono alcuni esempi di lingue disponibili", setlang)}")
    for l in supported_lang:
        await update.message.reply_text(f"{l}")

# comando /setlang
async def set_lang(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global setlang
    chat_id = update.effective_chat.id
    state = get_chat_state(chat_id)
    if not context.args:
        message = translate_chat_bot("Lingua non valida! Prova a usare /listlang", setlang)
        await update.message.reply_text(message)
        return
    new_lang = context.args[0].lower()
    if new_lang not in supported_lang:
        await update.message.reply_text(f"{translate_chat_bot(f"Lingua non supportata! Prova /listlang", setlang)}")
    else:
        setlang = new_lang
        state['lang'] = new_lang
        save_states()
        await update.message.reply_text(translate_chat_bot(f"Lingua impostata a {new_lang}", setlang))
        with open (".txt", "w") as f: f.write(new_lang)  # Path to settings file → ".txt"
        
#comando /reset
async def reset_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global SELECTED_MODEL, is_reset
    chat_id = update.effective_chat.id
    state = get_chat_state(chat_id)
    is_reset = True
    SELECTED_MODEL = MODEL_LIST[10]
    state['listening'] = False
    state['model'] = SELECTED_MODEL
    setlang = "it"
    state['lang'] = "it"
    with open (".txt", "w") as f: f.write('it')  # Path to settings file → ".txt"
    state['history'] = []
    state['file_context'] = ""
    save_states()
    await update.message.reply_text(translate_chat_bot(f"Reset completato!", setlang))


# Creazione dell'applicazione del bot / Create the bot application
app = Application.builder().token(API_Telegram).build()

#===Risposta Automatica===# 
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
#===Comandi===#
app.add_handler(CommandHandler('start', start))
app.add_handler(CommandHandler('help', help_cmd))
app.add_handler(CommandHandler('act', activate_list))
app.add_handler(CommandHandler('deact', deactivate_list))
app.add_handler(CommandHandler('ai', ai_chat))
app.add_handler(CommandHandler('listmodel', list_model))
app.add_handler(CommandHandler('setmodel', set_model))
app.add_handler(CommandHandler('listlang', list_lang))
app.add_handler(CommandHandler('setlang', set_lang))
app.add_handler(CommandHandler('reset', reset_chat))

# Avvio del bot / Start the bot
if __name__ == "__main__":
    app.run_polling()




