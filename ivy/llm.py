"""LLM service layer using Instructor for structured output."""

import instructor
from dotenv import load_dotenv
from pydantic import BaseModel, Field

from ivy.models import TextResponse
from ivy.prompt_registry import PromptRegistry

# Load environment variables (for API keys)
load_dotenv()


async def generate_response(prompt_id: str, args: dict[str, str]) -> TextResponse:
    """Generate a structured greeting based on input text.

    Args:
        prompt_id: The ID of the prompt to use
        args: A dictionary of arguments to pass to the prompt

    Returns:
        A TextResponse object
    """
    prompt = PromptRegistry().get_prompt(prompt_id)
    provider_model_id = f"{prompt.model_provider}/{prompt.model_name}"

    print(f"Calling prompt {prompt.prompt_id} with parameters {args}")

    # Initialize provider and model of choice.
    client = instructor.from_provider(provider_model_id, async_client=True)

    user_prompt = prompt.format(args=args)

    return await client.chat.completions.create(
        response_model=TextResponse,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a helpful assistant that processes text as prompted. "
                    "Respond in a structured format with the output text and language."
                ),
            },
            {"role": "user", "content": user_prompt},
        ],
    )
