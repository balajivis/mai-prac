
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain.schema.document import Document
import json 
import ollama

# Parse PDF
reader = PdfReader('arso.pdf')
text = ""
for i in range(0, len(reader.pages)):
    page = reader.pages[i]
    text += page.extract_text() + " "

# 3. Split document
documents = [Document(page_content=text, metadata={"source": "local"})]
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=200, chunk_overlap=40)
all_splits = text_splitter.split_documents(documents)

def triplextract(text, entity_types, predicates):
    input_format = """
        **Entity Types:**
        {entity_types}

        **Predicates:**
        {predicates}

        **Text:**
        {text}
        """

    message = input_format.format(
                entity_types = json.dumps({"entity_types": entity_types}),
                predicates = json.dumps({"predicates": predicates}),
                text = text)

    # Pass the message as a single string
    prompt = message
    output = ollama.generate(model='sciphi/triplex', prompt=prompt)
    return output

entity_types = [
    "PRODUCT",
    "ROBOT",
    "SURVEY",
]

predicates = [
    "USES",
    "SCORES",
]

prediction = triplextract(text, entity_types, predicates)
print(prediction)