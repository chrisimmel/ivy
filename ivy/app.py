import traceback
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from ivy.llm import TextResponse, generate_response
from ivy.prompt_registry import PromptRegistry
from ivy.utils import get_markdown_from_web_page, is_url

app = FastAPI()


class DynamicPromptRequest(BaseModel):
    """Request model for dynamic prompt endpoints."""
    prompt_id: str = Field(..., description="The ID of the prompt to use")
    parameters: dict[str, Any] = Field(..., description="The parameters for the prompt")


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.post("/generate", response_model=TextResponse)
async def generate_prompt(request: DynamicPromptRequest) -> TextResponse:
    """Generate a response using any registered prompt."""
    try:
        print(f"Received request: {request}")
        # Validate that the prompt exists and all required parameters are provided
        prompt = PromptRegistry().get_prompt(request.prompt_id)

        # Validate that all required parameters are provided
        required_param_names = {param.name for param in prompt.parameters}
        provided_params = dict(request.parameters)
        provided_param_names = set({key for key, value in provided_params.items() if value is not None})

        for param in prompt.parameters:
            if param.allow_url:
                value = request.parameters.get(param.name)
                if value and is_url(value):
                    print(f"Getting text from web page at {value}")
                    text = await get_markdown_from_web_page(value)
                    provided_params[param.name] = text

        if missing := required_param_names - provided_param_names:
            raise HTTPException(
                status_code=400,
                detail=f"Missing required parameters: {', '.join(missing)}"
            )

        if extra := provided_param_names - required_param_names:
            raise HTTPException(
                status_code=400,
                detail=f"Unexpected parameters provided: {', '.join(extra)}"
            )

        response = await generate_response(
            prompt_id=request.prompt_id,
            args=provided_params
        )

        print(f"Genereated response: {response}")

        return response
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))
