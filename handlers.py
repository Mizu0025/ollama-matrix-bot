import simplematrixbotlib as botlib
import nio
import httpx
import io
from config import logger, SYSTEM_INSTRUCTION
from data_manager import DataManager
from ollama_client import markdown_to_html, fetch_ollama_models, chat_with_ollama
from comfyui_client import ComfyUIClient
from utils import split_text_into_chunks

data = DataManager()

def register_handlers(bot):
    @bot.listener.on_message_event
    async def handle_message(room, message):
        # logging
        logger.info(f"--- Event Received from {message.sender} ---")
        
        body = getattr(message, 'body', '').strip()
        # Robust MXC URL extraction for uploaded media
        mxc_url = getattr(message, 'url', None)
        if not mxc_url and hasattr(message, 'source'):
            content = message.source.get('content', {})
            mxc_url = content.get('url') or content.get('file', {}).get('url')
        
        is_media = mxc_url and isinstance(mxc_url, str) and mxc_url.startswith("mxc://")

        if not body.startswith("!") or body.startswith("! "):
            return

        logger.info(f"Command detected: {body} (is_media: {is_media})")
            
        if not botlib.MessageMatch(room, message, bot, "!").is_not_from_this_bot():
            return

        # Extract command and args
        content = body[1:]
        args = content.split()
        if not args:
            return
            
        command = args[0].lower()
        context = data.get_room_context(room.room_id)

        # Helper for sending messages
        async def send_formatted(text):
            chunks = split_text_into_chunks(text)
            for chunk in chunks:
                try:
                    html = markdown_to_html(chunk)
                    content = {
                        "msgtype": "m.text",
                        "body": chunk,
                        "format": "org.matrix.custom.html",
                        "formatted_body": html
                    }
                    await bot.api.async_client.room_send(
                        room_id=room.room_id,
                        message_type="m.room.message",
                        content=content
                    )
                except Exception as e:
                    logger.error(f"❌ Failed to send message chunk: {e}")
                    await bot.api.send_text_message(room.room_id, chunk)

        # Command Logic
        if command == "model":
            if len(args) > 1:
                data.set_model(args[1])
                await send_formatted(f"✅ Model switched to: `{data.current_model}`")
            else:
                await send_formatted(f"🤖 Current model: `{data.current_model}`")
            return

        if command == "models":
            try:
                models = await fetch_ollama_models()
                await send_formatted("**Loaded models:**\n" + "\n".join([f"- `{m}`" for m in models]))
            except Exception as e:
                await send_formatted(f"❌ Error fetching models: {e}")
            return

        if command in ["reset", "clear"]:
            data.clear_history(room.room_id)
            await send_formatted("🧹 History cleared for this room.")
            return

        if command == "help":
            await send_formatted(
                "🤖 **Ollama Bot Help**\n\n"
                "• `!<prompt>` - Chat with AI\n"
                "• `!fate <prompt>` - Generate an image\n"
                "• `!model <name>` - Switch model\n"
                "• `!models` - List local models\n"
                "• `!avatar <url>` - Update bot avatar from URL\n"
                "• `!avatar` (with image upload) - Update bot avatar\n"
                "• `!clear` - Reset history"
            )
            return

        if command == "avatar":
            if is_media:
                try:
                    await bot.api.async_client.set_avatar_url(mxc_url)
                    await send_formatted("✅ Avatar updated successfully from uploaded image!")
                except Exception as e:
                    logger.error(f"Failed to set avatar: {e}")
                    await send_formatted(f"❌ Failed to update avatar: {e}")
                return

            if len(args) > 1:
                url = args[1]
                await send_formatted("⏳ Downloading image...")
                try:
                    async with httpx.AsyncClient(timeout=30.0) as client:
                        resp = await client.get(url, follow_redirects=True)
                        if resp.status_code != 200:
                            await send_formatted(f"❌ Failed to download image: HTTP {resp.status_code}")
                            return
                        
                        content_type = resp.headers.get("Content-Type", "")
                        if not content_type.startswith("image/"):
                            await send_formatted(f"❌ URL does not point to an image (Content-Type: {content_type})")
                            return
                        
                        image_data = resp.content
                        if len(image_data) > 10 * 1024 * 1024:  # 10MB limit
                            await send_formatted("❌ Image is too large (max 10MB)")
                            return

                        upload_resp = await bot.api.async_client.upload(
                            io.BytesIO(image_data), 
                            content_type=content_type, 
                            filename="avatar"
                        )
                        
                        if isinstance(upload_resp, nio.UploadResponse):
                            await bot.api.async_client.set_avatar_url(upload_resp.content_uri)
                            await send_formatted("✅ Avatar updated successfully from URL!")
                        else:
                            await send_formatted(f"❌ Failed to upload image to Matrix.")
                except Exception as e:
                    logger.error(f"Error updating avatar: {e}")
                    await send_formatted(f"❌ Error updating avatar: {str(e)}")
            else:
                await send_formatted("❓ Usage: `!avatar <url>` or upload an image with the caption `!avatar`.")
            return

        if command == "fate":
            prompt = " ".join(args[1:])
            if not prompt:
                await send_formatted("❓ Usage: `!fate <prompt>`")
                return

            await send_formatted(f"🎨 Requesting image generation for: `{prompt}`...")
            
            try:
                comfy_client = ComfyUIClient()
                
                # 1. Request generation
                resp = await comfy_client.request_generation(prompt, message.sender)
                job_id = resp.get("job_id")
                queue_pos = resp.get("queue_position", "unknown")
                
                if not job_id:
                    await send_formatted(f"❌ Failed to get job ID from service: `{resp}`")
                    return

                await send_formatted(f"✅ Job queued! ID: `{job_id}`, Position: {queue_pos}")
                
                # 2. Wait for completion
                await bot.api.async_client.room_typing(room.room_id, True)
                result = await comfy_client.wait_for_job(job_id)
                
                # Assume result contains image URL(s)
                image_urls = []
                if isinstance(result, dict):
                    # Check common response patterns
                    if "result" in result and isinstance(result["result"], dict) and "images" in result["result"]:
                        image_urls = result["result"]["images"]
                    elif "images" in result:
                        image_urls = result["images"]
                    elif "url" in result:
                        image_urls = [result["url"]]
                
                if not image_urls:
                    await send_formatted(f"⚠ Generation completed but no image URL was found in response.")
                    logger.warning(f"No image URLs in result: {result}")
                    return

                for img_url in image_urls:
                    # If the URL is relative, prepend the base URL
                    full_url = img_url
                    if img_url.startswith("/"):
                        full_url = f"{comfy_client.base_url}{img_url}"
                    
                    await send_formatted(f"🖼 **Generated Image:** {full_url}")

            except Exception as e:
                logger.error(f"Error in !fate command: {e}")
                await send_formatted(f"❌ Error during image generation: {str(e)}")
            finally:
                await bot.api.async_client.room_typing(room.room_id, False)
            return


        # Standard AI Query
        prompt = " ".join(args)
        context["messages"].append({"role": "user", "content": prompt})
        
        if len(context["messages"]) > 20:
            context["messages"] = context["messages"][-20:]

        logger.info(f"Querying {data.current_model}...")
        await bot.api.async_client.room_typing(room.room_id, True)

        try:
            ai_msg = await chat_with_ollama(data.current_model, SYSTEM_INSTRUCTION, context["messages"])
            context["messages"].append({"role": "assistant", "content": ai_msg})
            data.save_data()
            await send_formatted(ai_msg)
        except Exception as e:
            await send_formatted(f"⚠ Error: {str(e)}")
        finally:
            await bot.api.async_client.room_typing(room.room_id, False)
