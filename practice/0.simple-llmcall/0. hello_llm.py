import re
from dotenv import load_dotenv
load_dotenv()

from langchain_groq import ChatGroq
llm_groq = ChatGroq(model_name="llama3-70b-8192")

from langchain_community.llms import Ollama
llm = Ollama(model="gemma2:2b") 

llm_picker = "ollama" # or "groq"

def chat():
    print("Welcome to the chat! Type '/bye' to end the session.")
    valid_pattern = re.compile("^[\w\s\W]+$")
    
    while True:
        user_input = input("You: ")
        
    
        if valid_pattern.match(user_input):
            
            if llm_picker == "ollama":
                response = llm.invoke(user_input) # If you are using Ollama
            else:
                response = llm_groq.invoke(user_input).content # If you are using Groq
        else:
            response = "Type something valid, bro."
        
        if user_input.lower() == "/bye":
            print("Session ended. Goodbye!")
            break
        
        response = "Assistant: " + response
        print(response)

if __name__ == "__main__":
    chat()

