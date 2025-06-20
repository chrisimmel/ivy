import traceback
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from ivy.llm import TextResponse, generate_response
from ivy.params import prepare_params
from ivy.prompt_registry import PromptRegistry

app = FastAPI()


class DynamicPromptRequest(BaseModel):
    """Request model for dynamic prompt endpoints."""

    prompt_id: str = Field(..., description="The ID of the prompt to use")
    parameters: dict[str, Any] = Field(..., description="The parameters for the prompt")


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.post("/generate", response_model=TextResponse)
async def generate_prompt_response(request: DynamicPromptRequest) -> TextResponse:
    """Generate a response using any registered prompt."""
    try:
        print(f"Received request: {request}")
        # Validate that the prompt exists and all required parameters are provided.
        # Use a fresh registry instance to ensure we have the latest prompts.
        prompt = PromptRegistry().get_prompt(request.prompt_id)

        try:
            params = await prepare_params(prompt, request.parameters)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

        # Make the LLM call to generate the response.
        response = await generate_response(prompt=prompt, args=params, debug=True)

        print(f"Generated response: {response}")

        return response
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))
