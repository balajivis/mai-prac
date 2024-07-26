import json
import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
client = Groq()
MODEL = 'llama3-groq-70b-8192-tool-use-preview'

MEMORY_FILE = 'conversation_memory.json'

def load_memory(user_id):
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, 'r') as f:   
            memory = json.load(f)
            return memory.get(user_id, {"session_memory": "", "long_term_memory": ""})
    return {"session_memory": "", "long_term_memory": ""}

def save_memory(user_id, session_memory, long_term_memory):
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, 'r') as f:
            memory = json.load(f)
    else:
        memory = {}

    memory[user_id] = {
        "session_memory": session_memory,
        "long_term_memory": long_term_memory
    }

    with open(MEMORY_FILE, 'w') as f:
        json.dump(memory, f, indent=4)

def update_memory(user_id, session_message, long_term_message=None):
    memory = load_memory(user_id)
    memory['session_memory'] += f"\n{session_message}"
    if long_term_message:
        memory['long_term_memory'] += f"\n{long_term_message}"
    save_memory(user_id, memory['session_memory'], memory['long_term_memory'])

def summarize_memory(user_id):
    #print("Inside summarize")
    memory = load_memory(user_id)
    session_memory = memory['session_memory']
    #print(session_memory)
    if session_memory:
        messages = [
            {
                "role": "system",
                "content": """You are an intelligent memory manager designed to assist another LLM in summarizing user interactions. 
                Your task is to condense a JSON conversation into key pieces of information that are crucial for task completion. 
                Focus on extracting the user's name, phone number, and the specific tasks they are attempting to accomplish.
                Do not respond like you will do with a user. Please summarize the following JSON conversation:
                """
            },
            {
                "role": "user",
                "content": session_memory,
            }
        ]
        response = client.chat.completions.create(model=MODEL,messages=messages).choices[0].message.content
        #print("Summary response: ", response)
        memory['session_memory'] = response
        #print(memory['session_memory'])
        save_memory(user_id, memory['session_memory'], memory['long_term_memory'])
        return response
    return ""
