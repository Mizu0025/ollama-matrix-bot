import pytest
import respx
from httpx import Response
from ollama_client import markdown_to_html, fetch_ollama_models, chat_with_ollama

def test_markdown_to_html():
    text = "Hello **bold** and *italic*\n`code`"
    html = markdown_to_html(text)
    assert "<b>bold</b>" in html
    assert "<i>italic</i>" in html
    assert "<code>code</code>" in html
    assert "<br/>" in html

@pytest.mark.asyncio
@respx.mock
async def test_fetch_ollama_models_success():
    respx.get("http://localhost:11434/api/tags").mock(return_value=Response(200, json={
        "models": [{"name": "model1"}, {"name": "model2"}]
    }))
    
    models = await fetch_ollama_models()
    assert models == ["model1", "model2"]

@pytest.mark.asyncio
@respx.mock
async def test_chat_with_ollama_success():
    respx.post("http://localhost:11434/api/chat").mock(return_value=Response(200, json={
        "message": {"content": "AI response"}
    }))
    
    response = await chat_with_ollama("test-model", "sys prompt", [{"role": "user", "content": "hi"}])
    assert response == "AI response"
