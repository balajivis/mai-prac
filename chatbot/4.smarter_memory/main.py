from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
from conversation_memory import load_memory, update_memory, summarize_memory
from llm_tools import call_llm
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class InvokeRequest(BaseModel):
    input: str
    config: Dict[str, Any]
    kwargs: Dict[str, Any]

@app.get("/")
def read_root():
    return {"message": "Welcome to the Scheduler API"}

@app.post("/customer-service/invoke")
async def invoke(request: InvokeRequest):
   
    try:
        user_id = request.kwargs.get('user_id', 'default_user')
        memory = load_memory(user_id)
        print(memory["session_memory"])
        response = call_llm(request.input, memory)
                
        print(response)
        # Update session memory with the new interaction
        session_message = f"User: {request.input}\nAssistant: {response}"
        print(session_message)
        update_memory(user_id, session_message)
        summarize_memory(user_id)

        return {"output": response}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
