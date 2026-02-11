import simplematrixbotlib as botlib
from config import MATRIX_URL, MATRIX_ID, MATRIX_TOKEN, SESSION_FILE, logger
from handlers import register_handlers

def main():
    # 1. Define credentials with specific session file path
    creds = botlib.Creds(
        homeserver=MATRIX_URL, 
        username=MATRIX_ID, 
        access_token=MATRIX_TOKEN,
        session_stored_file=SESSION_FILE
    )

    # 2. Define config
    config = botlib.Config()
    config.encryption_enabled = False
    config.join_on_invite = True 

    # 3. Initialize bot
    bot = botlib.Bot(creds, config)
    
    # 4. Register handlers
    register_handlers(bot)

    # 5. Run
    logger.info("Starting Bot...")
    bot.run()

if __name__ == "__main__":
    main()
