"""Module to generates responses using a pre-trained locally run language model."""
# pip install sentencepiece
# pip install protobuf
# pip install 'accelerate>=0.26.0'

import torch
import logging
from langchain_community.vectorstores import FAISS
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from transformers import AutoModelForCausalLM, AutoTokenizer
from pathlib import Path
import json
from statschat.generative.prompts_local import (
    _extractive_prompt,
    _core_prompt,
    _format_instructions,
)

# pip install 'accelerate>=0.26.0'
# install sentencepiece

@staticmethod
def flatten_meta(d):
    """Utility, raise metadata within nested dicts."""
    return d | d.pop("metadata")


def similarity_search(
    query: str, latest_filter: bool = True, return_dicts: bool = True
) -> list[dict]:
    """
    Returns k document chunks with the highest relevance to the
    query

    Args:
        query (str): Question for which most relevant publications will
        be returned
        return_dicts: if True, data returned as dictionary, key = rank

    Returns:
        List[dict]: List of top k article chunks by relevance
    """
        
    logger = logging.getLogger(__name__)
    logger.info("Retrieving most relevant text chunks")
    faiss_db_root = "data/db_langchain"
    
    # Check directories exist in "SETUP" MODE to avoid error
    BASE_DIR = Path.cwd().joinpath("data")
    DB_LANGCHAIN_DIR = BASE_DIR.joinpath("db_langchain")
    DB_LANGCHAIN_UPDATE_DIR = BASE_DIR.joinpath("db_langchain_update")
    
    if DB_LANGCHAIN_UPDATE_DIR.exists():
        faiss_db_root_latest = "data/db_langchain_latest"
        
    elif DB_LANGCHAIN_DIR.exists():
        faiss_db_root_latest = "data/db_langchain"
        
    k_docs = 3
    similarity_threshold = 2.0
    embedding_model_name = "sentence-transformers/all-mpnet-base-v2"
    embeddings = HuggingFaceEmbeddings(model_name=embedding_model_name)

    if latest_filter:
        db_latest = FAISS.load_local(
            faiss_db_root_latest, embeddings, allow_dangerous_deserialization=True
        )
        top_matches = db_latest.similarity_search_with_score(query=query, k=k_docs)
    else:
        db = FAISS.load_local(
            faiss_db_root, embeddings, allow_dangerous_deserialization=True
        )
        top_matches = db.similarity_search_with_score(query=query, k=k_docs)

    # filter to document matches with similarity scores less than...
    # i.e. closest cosine distances to query
    top_matches = [x for x in top_matches if x[-1] <= similarity_threshold]

    if return_dicts:
        return [
            flatten_meta(doc[0].dict()) | {"score": float(doc[1])}
            for doc in top_matches
        ]
    return top_matches


# Define a function to generate responses
def generate_response(question: str, model: str, tokenizer) -> str:
    """
    Generate a response to the given question using the pre-trained model.

    Args:
        question (str): The input question to generate a response for.
        model (str): The model from huggingface that is being downloaded
        tokenizer (): Pretrained tokenizer from huggingface

    Returns
        str: The generated response.
    """
    print("Generating input tokens...")
    input_ids = tokenizer(question, return_tensors="pt").input_ids.to(model.device)
    print("Generating response...")
    output = model.generate(input_ids, max_new_tokens=1000)
    raw_response = tokenizer.decode(output[0], skip_special_tokens=True)
    return raw_response


# Define a function to format the response
def format_response(raw_response: str) -> dict:
    """
    Format the raw response from the model.

    Args:
        raw_response (str): The raw response from the model.

    Returns
        dict: The formatted response.
    """
    if "==ANSWER==" in raw_response:
        raw_response = raw_response.split("==ANSWER==")[1]
    clean_response = (
        raw_response.replace("“", '"')
        .replace("”", '"')
        .replace("‘", "'")
        .replace("’", "'")
        .strip()
    )
    try:
        validated_answer = json.loads(clean_response)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        validated_answer = {"error": f"Invalid JSON format: {e}"}
    return validated_answer


# Example usage
if __name__ == "__main__":
    verbose = False

    # For a question, retreive the most relevant text chunks
    #question = "What is the leading cause of death in Kenya in 2023?"
    question = "What was inflation in Kenya in 2022?"
    #question = "How is inflation calculated?"
    
    # Get the most relevant text chunks
    relevant_texts = similarity_search(question, latest_filter=True)
    

    if verbose:
        print("Relevant text chunks retrieved:")
        for i, text in enumerate(relevant_texts):
            print(f"Rank {i + 1}: {text['page_content']} (Score: {text['score']})")

    # Extract the most relevant text chunk data
    key_context_1 = relevant_texts[0]["page_content"]
    key_title_1 = relevant_texts[0]["title"]
    key_url_1 = relevant_texts[0]["page_url"]
    key_date_1 = relevant_texts[0]["date"]
    result_score_1 = relevant_texts[0]["score"]
    
    key_context_2 = relevant_texts[1]["page_content"]
    key_title_2 = relevant_texts[1]["title"]
    key_url_2 = relevant_texts[1]["page_url"]
    key_date_2 = relevant_texts[1]["date"]
    result_score_2 = relevant_texts[1]["score"]
    

    # Choose your model (e.g., Mistral-7B, DeepSeek, Llama-3, etc.)
    MODEL_ID = "mistralai/Mistral-7B-Instruct-v0.3"  # Change this if needed
    # Load model and tokenizer
    print("Building the tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)

    print("Loading the model...")
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID,
        torch_dtype=torch.float16,  # Use float16 for efficiency if using a GPU
        device_map="auto",  # Automatically selects GPU if available
    )
    print("Model loaded successfully.")
    specific_prompt = _extractive_prompt.format(
        QuestionPlaceholder=question, 
        ContextPlaceholder1=key_context_1, 
        ContextPlaceholder2=key_context_2,
    )
    user_input = _core_prompt + specific_prompt + _format_instructions

    if verbose:
        print(user_input)

    raw_response = generate_response(user_input, model, tokenizer)
    formatted_response = format_response(raw_response)
    
    if formatted_response["answer_provided"] and result_score_1 or result_score_2 < 0.5: #check
        print(f"Question: {question}")
        
        # If no suitable answer
        if formatted_response.get("most_likely_answer") is None:
            print("Answer provided: No suitable answer found. However relevant information may be found in a PDF. Please check the link(s) provided.")
        else:
            print("Answer provided:", formatted_response["most_likely_answer"])
            
        print("Context from:", formatted_response["where_context_from"])
        print("Text:", formatted_response["context_reference"])
        
        print("These answers are based on the following:")
        print("RELEVANT PUBLICATIONS")
        print("(ONE)")
        print(f"Title: {key_title_1}")
        print(f"Date: {key_date_1}")
        print(f"URL: {key_url_1}")
        print(f"Score: {round(result_score_1, 2)}")
    
        print("(TWO)")
        print(f"Title: {key_title_2}")
        print(f"Date: {key_date_2}")
        print(f"URL: {key_url_2}")
        print(f"Score: {round(result_score_2, 2)}")
        
        print("(RESPONSE)")
        print(f"{formatted_response['reasoning']}")
        
    elif result_score_1 < 0.5:
        print(f"Question: {question}")
        print("Answer not provided, as the context found wasn't easily quotable.")
        print("There may be relevant information in the following publication:")
        print("This comes from:", formatted_response["context_from"])
        print(formatted_response["context_from_text"])
        
        print("These answers are based on the following:")
        print("(RELEVANT PUBLICATIONS)")
        print("(ONE)")
        print(f"Title: {key_title_1}")
        print(f"Date: {key_date_1}")
        print(f"URL: {key_url_1}")
        print(f"Score: {round(result_score_1, 2)}")
        print(f"This comes from: {key_context_1}")
   
        print("(TWO)")
        print(f"Title: {key_title_2}")
        print(f"Date: {key_date_2}")
        print(f"URL: {key_url_2}")
        print(f"Score: {round(result_score_2, 2)}")
        print(f"This comes from: {key_context_2}")
        
        print("(RESPONSE)")
        print(f"{formatted_response['reasoning']}")
        
    else:
        print("Answer not provided, and the context is not relevant.")

#No suitable answer found.However relevant information may be found in a PDF.Please check the link(s) provided.