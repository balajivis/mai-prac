# FOLLOW All these instructions below!

# Install Tesseract locally
# On Mac use brew install tesseract, 
# on Windows use: https://github.com/UB-Mannheim/tesseract/wiki
# Then pip install pytesseract

# Create a new Conda environment conda create -n mai-prac2 python==3.10.12
# pip install -r requirements.txt

from PIL import Image
import io
import base64
import gradio as gr
import torch
from transformers import pipeline

# Check if GPU is available and set device accordingly
device = 0 if torch.cuda.is_available() else -1

table_processor = pipeline(
    "document-question-answering",
    model="impira/layoutlm-document-qa",
)

def process_file(message, history):
    if message["files"] and message["text"]:
        # Open the first file (assuming it's an image)
        
        try:
            # Perform document question answering
            image_path = message["files"][0]['path']
            query = message["text"]
            
            result = table_processor(image_path, query)
            # Extract just the answer from the result
            if isinstance(result, list) and len(result) > 0:
                answer = result[0]['answer']
            else:
                answer = "No answer found."
            return answer
        except Exception as e:
            return str(e)

# Create a Gradio interface
demo = gr.ChatInterface(
    fn=process_file,
    title="Mitra Robot Enterprise Chat",
    multimodal=True
)

# Launch the Gradio interface
demo.launch(share=True, debug=True)