from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from langserve import add_routes

from langchain.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_community.llms import Ollama
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma

from langchain_groq import ChatGroq
from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

# 1. Setup the FastAPI app
app = FastAPI(
    title="Modern AI Practitioner",
    version="1.0",
    description="For class coding",
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Load our DB
embeddings = OllamaEmbeddings(model="mxbai-embed-large")
vector_db = Chroma(persist_directory="../0.simple-llmcall/doc_vectors", embedding_function=embeddings)

# 3. Setup the LLM chain
llm = ChatGroq(model_name="llama3-70b-8192")
#llm = Ollama(model="gemma:2b")

template = """
Your name is Mitra. You are a customer service assistant for Modern AI Pro. 
Kindly answer the customer request about this: {question}
Stick to the main topic -- related to AI bootcamp -- and when something is not relevant
gently prod the customer back to the conversation. Answer in 3 sentences or less 
where possible. 
Use this context retrieved from the database: {context}

"""

prompt = ChatPromptTemplate.from_template(template)

entry_point = RunnableParallel({"context": vector_db.as_retriever(), 
                                "question": RunnablePassthrough()})

# Add the routes for the customer service chatbot
add_routes(
    app,
    entry_point | prompt | llm | StrOutputParser(),
    path="/customer-service",
)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)
