"""Module to generates responses using a pre-trained locally run language model."""
# pip install sentencepiece
# pip install protobuf
# pip install 'accelerate>=0.26.0'

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


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
    return tokenizer.decode(output[0], skip_special_tokens=True)


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
    question = "What was inflation in Kenya in December 2021?"

    user_input = question
    response = generate_response(user_input, model, tokenizer)
    print(response)
