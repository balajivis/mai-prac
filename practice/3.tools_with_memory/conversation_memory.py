import json
import os

MEMORY_FILE = 'conversation_memory.json'

def load_memory(user_id):
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, 'r') as f:
            memory = json.load(f)
            #return 5 if you need
            return memory.get(user_id, [])
    return []

def save_memory(user_id, messages):
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, 'r') as f:
            memory = json.load(f)
    else:
        memory = {}

    memory[user_id] = messages

    with open(MEMORY_FILE, 'w') as f:
        json.dump(memory, f, indent=4)
