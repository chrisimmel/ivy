from typing import Any

from ivy.models import TextTaskPrompt
from ivy.utils import get_markdown_from_web_page, is_url


async def prepare_params(prompt: TextTaskPrompt, params: dict[str, Any]) -> dict[str, Any]:
    required_param_names = {param.name for param in prompt.parameters}
    provided_param_names = set({key for key, value in params.items() if value is not None})

    output_params = dict(params)

    if missing := required_param_names - provided_param_names:
        raise ValueError(f"Missing required parameters: {', '.join(missing)}")

    if extra := provided_param_names - required_param_names:
        raise ValueError(f"Unexpected parameters provided: {', '.join(extra)}")

    for param in prompt.parameters:
        if param.allow_url and param.name in params:
            value = params.get(param.name)
            if value and is_url(value):
                # The text value is a URL, so replace it with markdown text from the corresponding web page.
                print(f"Getting text from web page at {value}")
                text = await get_markdown_from_web_page(value)
                output_params[param.name] = text

    return output_params
