"""LLM service layer using Instructor for structured output."""

import instructor
from dotenv import load_dotenv

from ivy.models import TextResponse, TextTaskPrompt

# Load environment variables (for API keys)
load_dotenv()


async def generate_response(prompt: TextTaskPrompt, args: dict[str, str], debug: bool = False) -> TextResponse:
    """Generate a structured greeting based on input text.

    Args:
        prompt_id: The ID of the prompt to use
        args: A dictionary of arguments to pass to the prompt

    Returns:
        A TextResponse object
    """
    provider_model_id = f"{prompt.model_provider}/{prompt.model_name}"

    if debug:
        print(f"Calling prompt {prompt.prompt_id} with model {provider_model_id} and parameters {args}")

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
