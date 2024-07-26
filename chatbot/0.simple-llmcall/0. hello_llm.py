import re
from langchain_groq import ChatGroq
from dotenv import load_dotenv
load_dotenv()
llm = ChatGroq(model_name="llama3-70b-8192")

def chat():
    print("Welcome to the chat! Type '/bye' to end the session.")
    valid_pattern = re.compile("^[\w\s\W]+$")
    
    while True:
        user_input = input("You: ")
        
    
        if valid_pattern.match(user_input):
            response = llm.invoke(user_input).content
        else:
            response = "Type something valid, bro."
        
        if user_input.lower() == "/bye":
            print("Session ended. Goodbye!")
            break
        
        response = "Assistant: " + response
        print(response)

if __name__ == "__main__":
    chat()

