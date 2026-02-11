import json
import os
from config import DATA_FILE, DEFAULT_MODEL, logger

class DataManager:
    def __init__(self):
        self.room_contexts = {}
        self.current_model = DEFAULT_MODEL
        self.load_data()

    def load_data(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r") as f:
                    data = json.load(f)
                    self.room_contexts = data.get("contexts", {})
                    self.current_model = data.get("current_model", DEFAULT_MODEL)
                logger.info("✅ Persistence data loaded.")
            except Exception as e:
                logger.error(f"Failed to load persistence data: {e}")

    def save_data(self):
        try:
            with open(DATA_FILE, "w") as f:
                json.dump({
                    "contexts": self.room_contexts,
                    "current_model": self.current_model
                }, f, indent=4)
        except Exception as e:
            logger.error(f"Failed to save persistence data: {e}")

    def get_room_context(self, room_id):
        if room_id not in self.room_contexts:
            self.room_contexts[room_id] = {
                "system": "You are a helpful software assistant.",
                "messages": []
            }
        return self.room_contexts[room_id]

    def set_model(self, model_name):
        self.current_model = model_name
        self.save_data()

    def clear_history(self, room_id):
        if room_id in self.room_contexts:
            self.room_contexts[room_id]["messages"] = []
            self.save_data()
