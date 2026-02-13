import sys
from unittest.mock import AsyncMock, MagicMock, patch

# Mock modules
mock_nio = MagicMock()
mock_nio.UploadResponse = MagicMock
sys.modules["nio"] = mock_nio
mock_botlib = MagicMock()
sys.modules["simplematrixbotlib"] = mock_botlib

import pytest
import io
import nio
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
@patch("handlers.ComfyUIClient")
@patch("httpx.AsyncClient")
async def test_fate_command_success(mock_httpx, mock_comfy_client_class, mock_data, mock_bot, mock_room):
    # Arrange
    handler = None
    def capture_handler(f):
        nonlocal handler
        handler = f
        return f
    mock_bot.listener.on_message_event = capture_handler
    register_handlers(mock_bot)
    
    message = MagicMock()
    message.body = "!fate a beautiful sunset"
    message.sender = "@user:test"
    
    mock_comfy = mock_comfy_client_class.return_value
    mock_comfy.request_generation = AsyncMock(return_value={"job_id": "job123", "queue_position": 1})
    mock_comfy.wait_for_job = AsyncMock(return_value={"status": "completed", "images": ["http://example.com/image.webp"]})
    
    mock_resp = AsyncMock()
    mock_resp.status_code = 200
    mock_resp.content = b"fake_image_data"
    mock_resp.headers = {"Content-Type": "image/webp"}
    mock_resp.raise_for_status = MagicMock()
    
    mock_httpx_instance = mock_httpx.return_value.__aenter__.return_value
    mock_httpx_instance.get.return_value = mock_resp
    
    upload_resp = MagicMock(spec=nio.UploadResponse)
    upload_resp.content_uri = "mxc://example.com/image123"
    mock_bot.api.async_client.upload.return_value = upload_resp
    
    # Act
    await handler(mock_room, message)
    
    # Assert
    mock_comfy.request_generation.assert_called_once_with("a beautiful sunset", "@user:test")
    mock_comfy.wait_for_job.assert_called_once_with("job123")
    
    # Check if the image URL was sent in a text message
    # Filter room_send calls to find the one containing the image URL
    sent_image_msg = False
    for call in mock_bot.api.async_client.room_send.call_args_list:
        content = call[1]["content"]
        if "http://example.com/image.webp" in content["body"]:
            sent_image_msg = True
            assert content["msgtype"] == "m.text"
            break
    
    assert sent_image_msg, "Image URL was not sent in any message"
