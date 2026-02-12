import sys
from unittest.mock import AsyncMock, MagicMock, patch

# Mock modules that might not be installed in the test environment
mock_nio = MagicMock()
mock_nio.UploadResponse = MagicMock
sys.modules["nio"] = mock_nio

mock_botlib = MagicMock()
sys.modules["simplematrixbotlib"] = mock_botlib

import nio
import simplematrixbotlib as botlib

import pytest
import io
from handlers import register_handlers

@pytest.fixture
def mock_bot():
    bot = MagicMock()
    bot.api = MagicMock()
    bot.api.async_client = AsyncMock()
    bot.api.send_text_message = AsyncMock()
    bot.listener = MagicMock()
    return bot

@pytest.fixture
def mock_room():
    room = MagicMock()
    room.room_id = "!test:room"
    return room

@patch("handlers.DataManager")
@patch("handlers.fetch_ollama_models")
@patch("handlers.chat_with_ollama")
async def Should_SetAvatarAndUpload_WhenAvatarFromUrlSucceeds(mock_chat, mock_fetch, mock_data, mock_bot, mock_room):
    # Arrange
    # Capture the handle_message function
    handler = None
    def capture_handler(f):
        nonlocal handler
        handler = f
        return f
    mock_bot.listener.on_message_event = capture_handler
    
    register_handlers(mock_bot)
    
    message = MagicMock()
    message.body = "!avatar http://example.com/image.png"
    message.sender = "@user:test"
    message.url = None
    
    # Mock httpx response
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.headers = {"Content-Type": "image/png"}
    mock_resp.content = b"fake_image_data"
    
    # Mock upload response
    upload_resp = MagicMock(spec=nio.UploadResponse)
    upload_resp.content_uri = "mxc://example.com/123"
    mock_bot.api.async_client.upload.return_value = upload_resp
    
    # Act
    with patch("httpx.AsyncClient.get", return_value=mock_resp):
        await handler(mock_room, message)
    
    # Assert
    # Verify httpx was called (via the mock_resp check inside the handler logic)
    # Check if upload was called with BytesIO
    mock_bot.api.async_client.upload.assert_called_once()
    args, kwargs = mock_bot.api.async_client.upload.call_args
    assert isinstance(args[0], io.BytesIO)
    assert args[0].getvalue() == b"fake_image_data"
    
    # Check if set_avatar_url was called
    mock_bot.api.async_client.set_avatar_url.assert_called_once_with("mxc://example.com/123")

@patch("handlers.DataManager")
async def Should_ExtractMxcFromNestedSource_WhenDirectlyUploaded(mock_data, mock_bot, mock_room):
    # Arrange
    handler = None
    def capture_handler(f):
        nonlocal handler
        handler = f
        return f
    mock_bot.listener.on_message_event = capture_handler
    register_handlers(mock_bot)
    
    # Scenario: MXC in source.content.file.url (common for encrypted/specific clients)
    message = MagicMock()
    message.body = "!avatar"
    message.sender = "@user:test"
    message.url = None
    message.source = {
        "content": {
            "file": {
                "url": "mxc://example.com/uploaded_direct"
            }
        }
    }
    
    # Act
    await handler(mock_room, message)
    
    # Assert
    mock_bot.api.async_client.set_avatar_url.assert_called_once_with("mxc://example.com/uploaded_direct")

@patch("handlers.DataManager")
async def Should_ExtractMxcFromStandardUrl_WhenDirectlyUploaded(mock_data, mock_bot, mock_room):
    # Arrange
    handler = None
    def capture_handler(f):
        nonlocal handler
        handler = f
        return f
    mock_bot.listener.on_message_event = capture_handler
    register_handlers(mock_bot)
    
    # Scenario: Standard message.url attribute
    message = MagicMock()
    message.body = "!avatar"
    message.sender = "@user:test"
    message.url = "mxc://example.com/standard_mxc"
    
    # Act
    await handler(mock_room, message)
    
    # Assert
    mock_bot.api.async_client.set_avatar_url.assert_called_once_with("mxc://example.com/standard_mxc")

@patch("handlers.DataManager")
async def Should_NotUploadAndReportError_WhenUrlIsNotAnImage(mock_data, mock_bot, mock_room):
    # Arrange
    handler = None
    def capture_handler(f):
        nonlocal handler
        handler = f
        return f
    mock_bot.listener.on_message_event = capture_handler
    register_handlers(mock_bot)
    
    message = MagicMock()
    message.body = "!avatar http://example.com/not-image.txt"
    message.sender = "@user:test"
    
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.headers = {"Content-Type": "text/plain"}
    
    # Act
    with patch("httpx.AsyncClient.get", return_value=mock_resp):
        await handler(mock_room, message)
    
    # Assert
    mock_bot.api.async_client.upload.assert_not_called()
    mock_bot.api.async_client.room_send.assert_called() # Should send an error message
