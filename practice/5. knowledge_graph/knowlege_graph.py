import json
import os
from transformers import AutoModelForCausalLM, AutoTokenizer

def get_model_and_tokenizer(model_name, local_dir="local_model"):
    model_path = os.path.join(local_dir, model_name.replace("/", "_"))
    
    if os.path.exists(model_path):
        print(f"Loading model and tokenizer from local directory: {model_path}")
        model = AutoModelForCausalLM.from_pretrained(model_path).to('cpu').eval()
        tokenizer = AutoTokenizer.from_pretrained(model_path)
    else:
        print(f"Downloading model and tokenizer from Hugging Face hub: {model_name}")
        model = AutoModelForCausalLM.from_pretrained(model_name, trust_remote_code=True).to('cpu').eval()
        tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
        model.save_pretrained(model_path)
        tokenizer.save_pretrained(model_path)
    
    return model, tokenizer

def triplextract(model, tokenizer, text, entity_types, predicates):

    input_format = """Perform Named Entity Recognition (NER) and extract knowledge graph triplets from the text. NER identifies named entities of given entity types, and triple extraction identifies relationships between entities using specified predicates.
      
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

    messages = [{'role': 'user', 'content': message}]
    input_ids = tokenizer.apply_chat_template(messages, add_generation_prompt=True, return_tensors="pt").to("cuda")
    output = tokenizer.decode(model.generate(input_ids=input_ids, max_length=2048)[0], skip_special_tokens=True)
    return output

model_name = "sciphi/triplex"
model, tokenizer = get_model_and_tokenizer(model_name)

entity_types = ["LOCATION", "POSITION", "DATE", "CITY", "COUNTRY", "NUMBER"]
predicates = ["POPULATION", "AREA"]
text = """
San Francisco,[24] officially the City and County of San Francisco, is a commercial, financial, and cultural center in Northern California. 

With a population of 808,437 residents as of 2022, San Francisco is the fourth most populous city in the U.S. state of California behind Los Angeles, San Diego, and San Jose.
"""

prediction = triplextract(model, tokenizer, text, entity_types, predicates)
print(prediction)
