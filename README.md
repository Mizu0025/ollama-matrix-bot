# 🤖 Ollama Matrix Bot

A lightweight, modular Matrix bot that brings local Large Language Models (LLMs) to your chat rooms using **Ollama**.

## ✨ Features

- **Local LLM Integration**: Interface with any model available in your local Ollama instance.
- **Persistent Chat History**: Maintains context window for rooms, saved across restarts.
- **Rich Formatting**: Automatically converts AI Markdown (code blocks, bold, italics) into Matrix-friendly HTML.
- **Multi-room Support**: Independent conversation contexts for every room the bot is in.
- **Strict Triggers**: Designed to avoid accidental activations (requires fixed `!command` syntax).
- **Dockerized**: Clean, non-root deployment optimized for Docker Compose.

---

## 🚀 Quick Start

### 1. Requirements
- A Matrix account and Access Token.
- [Ollama](https://ollama.com/) running with an accessible API (e.g., `http://192.168.1.x:11434`).

### 2. Configuration
The bot is configured via environment variables. Create a `.env` file or define them in your compose file:

```env
MATRIX_URL=https://matrix.org
MATRIX_ID=@your_bot_id:matrix.org
MATRIX_TOKEN=syt_your_access_token_here
OLLAMA_URL=http://your-host-ip:11434
OLLAMA_MODEL=gemma3:12b
```

### 3. Deployment (Docker Compose)
This is the recommended way to run the bot to ensure proper file permissions.

```yaml
services:
  ollama-bot:
    build: ./path/to/bot
    container_name: ollama_bot
    user: "1000:1000" # Use your host UID:GID (check with `id` command)
    environment:
      - PYTHONUNBUFFERED=1
      - MATRIX_URL=${MATRIX_URL}
      - MATRIX_ID=${MATRIX_ID}
      - MATRIX_TOKEN=${MATRIX_TOKEN}
      - OLLAMA_URL=${OLLAMA_URL}
      - OLLAMA_MODEL=${OLLAMA_MODEL}
    volumes:
      - ./store:/app/store
    restart: unless-stopped
```

### 4. Run Locally
```bash
pip install -r requirements.txt
python main.py
```

---

## 🛠 Commands

The bot uses strict `!command` triggers (no space allowed after the `!`).

| Command | Description |
| :--- | :--- |
| `!<prompt>` | Ask the AI anything. |
| `!model <name>`| Switch active model (e.g., `!model llama3`). |
| `!models` | List all local models available in Ollama. |
| `!clear` | Wipe conversation history for the current room. |
| `!help` | Show this help menu. |

---

## 📂 Project Structure

- `main.py`: Tiny entry point.
- `handlers.py`: Core logic for Matrix events and command routing.
- `ollama_client.py`: Ollama API communication and Markdown formatting.
- `data_manager.py`: Handles state persistence and room context history.
- `config.py`: Centralized environment variables and logging.

---

## 🔒 Persistence & Security

- **Storage**: All persistent data is stored in `/app/store`. This includes:
  - `bot_data.json`: Memory and model settings.
  - `session.txt`: Matrix login session (prevents re-logins).
- **Permissions**: By using the `user: "1000:1000"` directive in Docker Compose, the bot runs with your host user privileges. This ensures any files created in the `./store` volume are owned by you and not `root`.
- **Strict Triggers**: The bot ignores `! command` to prevent accidental triggers in general conversation.
