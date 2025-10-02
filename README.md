# 🤖 Judy - Telegram AI Assistant Bot

Judy is an advanced Telegram bot powered by [Groq](https://groq.com/) and state-of-the-art Large Language Models (LLMs), designed to interact intelligently with users, handle custom commands, remember conversation history, and support multiple languages.

---

## 🔧 Key Features

- **Real-time AI responses** via Groq and LLMs (e.g., Llama, Qwen, GPT-OSS)
- **Listening mode**: toggle automatic replies to messages in chat (`/act` / `/deact`)
- **Conversation memory**: retains chat context until reset
- **Multilingual support**: bot messages automatically translated into 14 languages
- **Dynamic AI model selection**: choose from 11 different models
- **Persistent settings**: chat state, model, and language saved to disk

---

## 🚀 Requirements

- Python 3.8+
- A Telegram bot token (get one from [@BotFather](https://t.me/BotFather))
- A Groq API key ([Groq Console](https://console.groq.com/))
- Required Python packages:
  ```bash
  pip install python-telegram-bot groq deep-translator
  
---

## 📥 Installation

Clone the repository
- git clone https://github.com/your-username/judy-telegram-ai-bot.git
- cd judy-telegram-ai-bot

Set up your API keys
Open the main script (e.g., bot.py) and replace the empty strings:

- API_Telegram = 'YOUR_TELEGRAM_BOT_TOKEN_HERE'
- API_GROQ = "YOUR_GROQ_API_KEY_HERE"

Configure file paths
Locate and update these lines in the code:

# Example (replace empty strings with actual paths):
- LANG_FILE = "lang.txt"
- SETTINGS_FILE = "chat_states.json"
Ensure the bot has write permissions in the working directory.

Run the bot

- python bot.py

✅ The files lang.txt and chat_states.json will be created automatically on first run. 

---

## 📜 Commands

- /start → Start the bot
- /help → Show help menu
- /act → Enable auto-reply mode
- /deact → Disable auto-reply mode
- /ai [question] → Get an AI response without enabling listening mode
- /listmodel → List all available AI models
- /setmodel [index] → Set AI model (e.g.,/setmodel 10for Qwen)
- /listlang → Show supported language codes
- /setlang [code] → Change bot language (e.g.,/setlang en)
- /reset → Clear chat history and reset settings

---

## 🌍 Supported Languages

- it → Italian
- en → English
- es → Spanish
- ru → Russian
- hi → Hindi
- fr → French
- ar → Arabic
- bn → Bengali
- pt → Portuguese
- ur → Urdu
- id → Indonesian
- de → German
- ja → Japanese
- tr → Turkish

Default language: Italian (it) 

---

## 🤖 Available AI Models
Judy supports the following models via Groq:

- 0 → llama-3.1-8b-instant Meta
- 1 → llama-3.3-70b-versatile Meta
- 2 → meta-llama/llama-guard-4-12b Meta
- 3 → openai/gpt-oss-120b OpenAI
- 4 → openai/gpt-oss-20b OpenAI
- 5 → whisper-large-v3 OpenAI (audio-only)
- 6 → whisper-large-v3-turbo OpenAI (audio-only)
- 7 → meta-llama/llama-4-maverick-17b-128e-instruct Meta
- 8 → moonshotai/kimi-k2-instruct Moonshot AI
- 9 → playai-tts PlayAI (TTS-only)
- 10 → qwen/qwen3-32b Alibaba Cloud

💡 Recommendation: Use /setmodel 10 for the powerful Qwen/Qwen3-32B model. 

---

## ⚙️ Customization
Default model: Change SELECTED_MODEL = MODEL_LIST[10] in the code.
Creativity level: Adjust the fantasy variable (default: 0.6).
Bot personality: Edit the system prompt in the groq_response() function.

---

## 🙌 Acknowledgements
Groq – for ultra-fast LLM inference
python-telegram-bot
deep-translator

---

## ⚠️ Important Notes
🔒 Never commit your API keys to version control.
The bot only replies automatically when listening mode is ON (/act).
Audio/TTS models (e.g., Whisper, PlayAI) are listed for reference but not used for text generation.
For production use with many users, consider optimizing chat_states.json storage.
