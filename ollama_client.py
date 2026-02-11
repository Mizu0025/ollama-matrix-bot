import httpx
import re
from config import OLLAMA_URL, logger

def markdown_to_html(text):
    """Simple conversion of markdown to Matrix-friendly HTML."""
    html = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    html = re.sub(r"```(.*?)\n(.*?)\n?```", r'<pre><code>\2</code></pre>', html, flags=re.DOTALL)
    html = re.sub(r"`(.*?)`", r"<code>\1</code>", html)
    html = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", html)
    html = re.sub(r"\*(.*?)\*", r"<i>\1</i>", html)
    html = html.replace("\n", "<br/>")
    return html

async def fetch_ollama_models():
    try:
        async with httpx.AsyncClient() as client:
            res = await client.get(f"{OLLAMA_URL}/api/tags")
            return [m['name'] for m in res.json().get('models', [])]
    except Exception as e:
        logger.error(f"Error fetching models: {e}")
        raise e

async def chat_with_ollama(model, system_prompt, messages):
    payload = {
        "model": model,
        "messages": [{"role": "system", "content": system_prompt}] + messages,
        "stream": False
    }
    async with httpx.AsyncClient(timeout=600.0) as client:
        response = await client.post(f"{OLLAMA_URL}/api/chat", json=payload)
        response.raise_for_status()
        return response.json().get('message', {}).get('content', 'No response.')
