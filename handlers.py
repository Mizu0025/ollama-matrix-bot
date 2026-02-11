import simplematrixbotlib as botlib
import nio
import httpx
from config import logger, SYSTEM_INSTRUCTION
from data_manager import DataManager
from ollama_client import markdown_to_html, fetch_ollama_models, chat_with_ollama

data = DataManager()

def register_handlers(bot):
    @bot.listener.on_message_event
    async def handle_message(room, message):
        # logging
        logger.info(f"--- Event Received from {message.sender} ---")
        
        # Strict parsing: MUST start with "!" and have NO space after it
        body = getattr(message, 'body', '').strip()
        mxc_url = getattr(message, 'url', None)
        is_image = mxc_url and mxc_url.startswith("mxc://")

        if not body.startswith("!") or body.startswith("! "):
            return
            
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
            try:
                html = markdown_to_html(text)
                content = {
                    "msgtype": "m.text",
                    "body": text,
                    "format": "org.matrix.custom.html",
                    "formatted_body": html
                }
                await bot.api.async_client.room_send(
                    room_id=room.room_id,
                    message_type="m.room.message",
                    content=content
                )
            except Exception as e:
                logger.error(f"❌ Failed to send message: {e}")
                await bot.api.send_text_message(room.room_id, text)

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
                "• `!model <name>` - Switch model\n"
                "• `!models` - List local models\n"
                "• `!avatar <url>` - Update bot avatar from URL\n"
                "• `!avatar` (with image upload) - Update bot avatar\n"
                "• `!clear` - Reset history"
            )
            return

        if command == "avatar":
            if is_image:
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
                            image_data, 
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
