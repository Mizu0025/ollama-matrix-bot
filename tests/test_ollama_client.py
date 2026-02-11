import pytest
import respx
from httpx import Response
from ollama_client import markdown_to_html, fetch_ollama_models, chat_with_ollama

def Should_ConvertMarkdownToHtml_WhenCalledWithMarkdownText():
    # Arrange
    text = "Hello **bold** and *italic*\n`code`"
    
    # Act
    html = markdown_to_html(text)
    
    # Assert
    assert "<b>bold</b>" in html
    assert "<i>italic</i>" in html
    assert "<code>code</code>" in html
    assert "<br/>" in html

@pytest.mark.asyncio
@respx.mock
async def Should_ReturnModelList_WhenFetchOllamaModelsSucceeds():
    # Arrange
    respx.get("http://localhost:11434/api/tags").mock(return_value=Response(200, json={
        "models": [{"name": "model1"}, {"name": "model2"}]
    }))
    
    # Act
    models = await fetch_ollama_models()
    
    # Assert
    assert models == ["model1", "model2"]

@pytest.mark.asyncio
@respx.mock
async def Should_ReturnAiResponse_WhenChatWithOllamaSucceeds():
    # Arrange
    respx.post("http://localhost:11434/api/chat").mock(return_value=Response(200, json={
        "message": {"content": "AI response"}
    }))
    
    # Act
    response = await chat_with_ollama("test-model", "sys prompt", [{"role": "user", "content": "hi"}])
    
    # Assert
    assert response == "AI response"
