from pydantic import BaseModel, Field
from typing import Union, Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
import logging
import torch
from datetime import datetime
from markupsafe import escape
from transformers import AutoModelForCausalLM, AutoTokenizer

from statschat import load_config
from statschat.generative.local_llm import (
    similarity_search,
    generate_response,
    format_response,
)
from statschat.generative.prompts_local import (
    _extractive_prompt,
    _core_prompt,
    _format_instructions,
)

# Config file to load
CONFIG = load_config(name="main")

# define session_id that will be used for log file and feedback
SESSION_NAME = f"statschat_api_{format(datetime.now(), '%Y_%m_%d_%H:%M')}"

logger = logging.getLogger(__name__)
log_fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(
    level=logging.INFO,
    format=log_fmt,
    # filename=f"log/{SESSION_NAME}.log",
    filemode="a",
)


app = FastAPI(
    title="KNBS StatsChat API",
    description=(
        "Read more in [blog post]"
        + "(https://datasciencecampus.ons.gov.uk/using-large-language-models-llms-to-improve-website-search-experience-with-statschat/)"  # noqa: E501
        + " or see [the code repository]"
        + "(https://github.com/datasciencecampus/statschat-app). "
        + "Frontend UI available internally [here]"
        + "(http://localhost:5000)."
    ),
    summary="""Experimental search of Kenya National Bureau of Statistics publications.
        Using retrieval augmented generation (RAG).""",
    version="0.1.1",
    contact={
        "name": "Kenya National Bureau of Statistics",
        "email": "test@knbs.com",
    },
)


@app.get("/", tags=["Principle Endpoints"])
async def about():
    """Access the API documentation in json format.

    Returns:
        Redirect to /openapi.json
    """
    response = RedirectResponse(url="/openapi.json")
    return response


@app.get("/search", tags=["Principle Endpoints"])
async def search(
    q: str,
    content_type: Union[str, None] = "latest",
    debug: bool = True,
):
    """Search KNBS publications and bulletins for a question.

    Args:
        q (str): Question to be answered based on KNBS publications and bulletins.
        content_type (Union[str, None], optional): Type of content to be searched.
            Currently accepted values: 'latest' to search the latest bulletins only
            or 'all' to search any publications and bulletins.
            Optional, defaults to 'latest'.
        debug (bool, optional): Flag to return debug information (full LLM response).
            Optional, defaults to True.

    Raises:
        HTTPException: 422 Validation error.

    Returns:
        HTTPresponse: 200 JSON with fields: question, content_type, answer, references
            and optionally debug_response.
    """
    question = escape(q).strip()
    if question in [None, "None", ""]:
        raise HTTPException(status_code=422, detail="Empty question")

    if content_type not in ["latest", "all"]:
        logger.warning('Unknown content type. Fallback to "latest".')
        content_type = "latest"

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

    # Get the most relevant text chunks
    relevant_texts = similarity_search(question, latest_filter=True)

    specific_prompt = _extractive_prompt.format(
        QuestionPlaceholder=question,
        ContextPlaceholder1=relevant_texts[0]["page_content"],
        ContextPlaceholder2=relevant_texts[1]["page_content"],
    )
    user_input = _core_prompt + specific_prompt + _format_instructions

    raw_response = generate_response(user_input, model, tokenizer)
    formatted_response = format_response(raw_response)

    # If no suitable answer
    if formatted_response.get("most_likely_answer") is None:
        results = {
            "question": question,
            "content_type": content_type,
            "answer": "No suitable answer, but relevant information may in a PDF.",
            "references": relevant_texts[0]["page_url"],
            "context_from": formatted_response["where_context_from"],
            "context_reference": formatted_response["context_reference"],
            "relevant_publication_one": relevant_texts[0]["title"],
            "relevant_publication_two": relevant_texts[1]["title"],
        }

    else:
        results = {
            "question": question,
            "content_type": content_type,
            "answer": formatted_response["most_likely_answer"],
            "references": relevant_texts[0]["page_url"],
            "context_from": formatted_response["where_context_from"],
            "context_reference": formatted_response["context_reference"],
            "relevant_publication_one": relevant_texts[0]["title"],
            "relevant_publication_two": relevant_texts[1]["title"],
        }

    logger.info(f"Sending following response: {results}")
    return results


class Feedback(BaseModel):
    rating: Union[str, int] = Field(
        description="""Recorded rating of the last answer.
        If thumbs are used then values are '1' for thumbs up
        and '0' for thumbs down."""
    )
    rating_comment: Optional[str] = Field(
        description="""Recorded comment on the last answer. Optional."""
    )
    question: Optional[str] = Field(description="""Last question. Optional.""")
    content_type: Optional[str] = Field(description="""Last content type. Optional.""")
    answer: Optional[str] = Field(description="""Last answer. Optional.""")


@app.post("/feedback", status_code=202, tags=["Principle Endpoints"])
async def record_rating(feedback: Feedback):
    """Records feedback on a previous answer.

    Args:
        feedback (Feedback): Recorded rating of the last answer.
            Required fields: rating (str or int).
            Optional fields: question, content_type, answer.

    Raises:
        HTTPException: 422 Validation error.

    Returns:
        HTTPResponse: 202 with empty body to indicate successfully added feedback.
    """
    logger.info(f"Recorded answer feedback: {feedback}")
    return ""
