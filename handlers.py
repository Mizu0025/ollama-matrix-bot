import simplematrixbotlib as botlib
from config import logger, SYSTEM_INSTRUCTION
from data_manager import DataManager
from ollama_client import markdown_to_html, fetch_ollama_models, chat_with_ollama
from utils import split_text_into_chunks

data = DataManager()

def register_handlers(bot):
    @bot.listener.on_message_event
    async def handle_message(room, message):
        # logging
        logger.info(f"--- Event Received from {message.sender} ---")
        
        # Strict parsing: MUST start with "!" and have NO space after it
        body = message.body.strip()
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
                "• `!model <name>` - Switch model\n"
                "• `!models` - List local models\n"
                "• `!clear` - Reset history"
            )
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
