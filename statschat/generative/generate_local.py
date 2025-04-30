"""Module to generates responses using a pre-trained locally run language model."""
# pip install sentencepiece
# pip install protobuf
# pip install 'accelerate>=0.26.0'

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import json
from statschat.generative.prompts_local import (
    _extractive_prompt,
    _core_prompt,
    _format_instructions,
)


# Define a function to generate responses
def generate_response(question, model, tokenizer):
    """
    Generate a response to the given question using the pre-trained model.

    Args:
        question (str): The input question to generate a response for.

    Returns
    -------
        str: The generated response.
    """
    print("Generating input tokens...")
    input_ids = tokenizer(question, return_tensors="pt").input_ids.to(model.device)
    print("Generating response...")
    output = model.generate(input_ids, max_new_tokens=1000)
    raw_response = tokenizer.decode(output[0], skip_special_tokens=True)
    return raw_response


# Define a function to format the response
def format_response(raw_response):
    """
    Format the raw response from the model.

    Args:
        raw_response (str): The raw response from the model.

    Returns
    -------
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
    user_input = _core_prompt + _extractive_prompt + _format_instructions
    raw_response = generate_response(user_input, model, tokenizer)
    formatted_response = format_response(raw_response)
    if formatted_response["answer_provided"]:
        print("Answer provided:", formatted_response["most_likely_answer"])
    else:
        print("No answer provided.")
