# main.py
import os
import json
import importlib
from fbchat import Client, ThreadType
from fbchat.models import Message
from config import APPSTATE_FILE, PREFIX, ADMIN_UID, BOT_NAME
from utils.logger import log

# Load appstate
with open(APPSTATE_FILE, "r") as f:
    appstate = json.load(f)

# Initialize Client
client = Client(session_cookies=appstate)

# Load all commands dynamically
COMMANDS = {}
commands_path = "commands"
for file in os.listdir(commands_path):
    if file.endswith(".py") and file != "__init__.py":
        command_name = file[:-3]  # Remove .py extension
        COMMANDS[command_name] = importlib.import_module(f"{commands_path}.{command_name}")

# Message Listener
class Bot(Client):
    def onMessage(self, author_id, message_object, thread_id, thread_type, **kwargs):
        if author_id == self.uid:  # Ignore bot's own messages
            return

        message_text = message_object.text or ""
        log(f"Message received from {author_id}: {message_text}")

        if message_text.startswith(PREFIX):
            command_name = message_text[len(PREFIX):].split(" ")[0]
            if command_name in COMMANDS:
                if author_id == ADMIN_UID:
                    COMMANDS[command_name].execute(self, author_id=author_id, 
                                                   message_text=message_text, 
                                                   thread_id=thread_id, 
                                                   thread_type=thread_type)
                    log(f"Command executed: {command_name} by {author_id}")
                else:
                    self.send(Message(text="Only admin can execute commands!"), thread_id=thread_id, thread_type=thread_type)
                    log(f"Unauthorized command attempt: {command_name} by {author_id}")
            else:
                self.send(Message(text="Unknown command!"), thread_id=thread_id, thread_type=thread_type)
                log(f"Unknown command: {command_name} by {author_id}")

# Start Bot
if __name__ == "__main__":
    bot = Bot(session_cookies=appstate)
    log(f"{BOT_NAME} is running!")

    try:
        bot.listen()
    except KeyboardInterrupt:
        log("Bot stopped.")