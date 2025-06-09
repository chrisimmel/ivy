"""Pydantic models and related types and constants."""

from pydantic import BaseModel, Field


class PromptParameter(BaseModel):
    """A parameter for a prompt."""

    name: str = Field(..., description="The name of the parameter")
    description: str = Field(..., description="The description of the parameter")
    type: str = Field(..., description="The type of the parameter")
    allow_url: bool = Field(..., description="Whether input can be taken from a URL")


class TextTaskPrompt(BaseModel):
    """A prompt for a text processing task."""

    prompt_id: str = Field(..., description="The prompt ID, a human-readable, meaningful, unique identifier")
    description: str = Field(..., description="A short description of the prompt")
    user_prompt: str = Field(..., description="The user prompt, with placeholders for any parameters.")
    model_provider: str = Field(..., description="The model provider")
    model_name: str = Field(..., description="The model name")
    parameters: list[PromptParameter] = Field(..., description="The parameters for the prompt.")

    def format(self, args: dict[str, str]) -> str:
        """Format the prompt with the given arguments."""
        user_prompt_text = self.user_prompt
        parameter_names = [parameter.name for parameter in self.parameters]

        for key in args.keys():
            if key not in parameter_names:
                raise ValueError(f"Unknown parameter {key} not found in prompt {self.prompt_id}")

        for parameter in self.parameters:
            if parameter.name not in args:
                raise ValueError(f"Parameter {parameter.name} not found for prompt {self.prompt_id} and args {args}")

            user_prompt_text = user_prompt_text.replace("{{" + parameter.name + "}}", args[parameter.name])

        return user_prompt_text

    @classmethod
    def from_yaml(cls, yaml_data: dict) -> "TextTaskPrompt":
        """Create a TextTaskPrompt from YAML data."""
        return cls(**yaml_data)


class TextResponse(BaseModel):
    """A structured text response."""

    output_text: str = Field(..., description="The text output")
    input_language: str = Field(..., description="The language or languages of the input text")
    output_language: str = Field(..., description="The language of the output text")
