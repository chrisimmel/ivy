#!/usr/bin/env python
import asyncio
import sys
from typing import Any

import click
import httpx

from ivy.llm import generate_response
from ivy.models import TextTaskPrompt
from ivy.params import prepare_params
from ivy.prompt_registry import PromptRegistry

DEFAULT_BASE_URL = "http://localhost:8000"
API_TIMEOUT_SECONDS = 120.0


prompt_registry = PromptRegistry()


class CliContext:
    """Context for CLI commands."""

    def __init__(self, base_url: str = DEFAULT_BASE_URL, use_api: bool = False):
        self.base_url = base_url
        self.use_api = use_api


@click.group()
@click.option(
    "--base-url",
    default=DEFAULT_BASE_URL,
    help=f"Base URL for the Ivy service. Default: {DEFAULT_BASE_URL}",
)
@click.option(
    "--use-api",
    is_flag=True,
    help="Use the API to generate responses. Default: False",
)
@click.pass_context
def cli(ctx: click.Context, base_url: str, use_api: bool) -> None:
    """Ivy CLI for interacting with the Ivy service."""
    ctx.obj = CliContext(base_url=base_url, use_api=use_api)


@cli.command()
@click.pass_context
def health(ctx: click.Context) -> None:
    """Check the health of the Ivy service."""
    base_url = ctx.obj.base_url
    try:
        with httpx.Client() as client:
            response = client.get(f"{base_url}/health")
            response.raise_for_status()
            click.echo("✅ Service is healthy")
            click.echo(f"Response: {response.json()}")
    except httpx.ConnectError:
        click.echo(f"❌ Could not connect to service at {base_url}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Health check failed: {e}", err=True)
        sys.exit(1)


async def generate_directly(prompt: TextTaskPrompt, args: dict[str, str], base_url: str) -> None:
    """Generate a response directly with no API call to the Ivy service."""
    params = await prepare_params(prompt, args)
    response = await generate_response(prompt=prompt, args=params, debug=False)

    click.echo("\n")
    click.echo(response.output_text)


async def generate_with_api(prompt: TextTaskPrompt, args: dict[str, str], base_url: str) -> None:
    """Generate a response with an API call to the Ivy service."""
    try:
        async with httpx.AsyncClient() as client:
            # Post to the /generate endpoint with the prompt_id and parameters.
            response = await client.post(
                f"{base_url}/generate",
                json={"prompt_id": prompt.prompt_id, "parameters": args},
                timeout=API_TIMEOUT_SECONDS,
            )
            response.raise_for_status()
            response_data = response.json()
            click.echo("\n")
            if "output_text" in response_data:
                click.echo(response_data["output_text"])
            else:
                for key, value in sorted(response_data.items()):
                    click.echo(f"{key}: {value}")
    except httpx.ConnectError:
        click.echo(f"❌ Could not connect to service at {base_url}. Be sure the Ivy service is running.", err=True)
        sys.exit(1)
    except httpx.HTTPStatusError as e:
        click.echo(f"❌ HTTP error {e.response.status_code}: {e.response.text}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Unexpected error: {e}", err=True)
        sys.exit(1)


def create_command_callback(prompt_id: str) -> callable:
    """Create a callback function for a specific prompt command."""
    prompt = prompt_registry.get_prompt(prompt_id)

    @click.pass_context
    def callback(ctx: click.Context, **kwargs: Any) -> None:
        """Dynamically generated command callback."""

        callback = generate_with_api if ctx.obj.use_api else generate_directly
        asyncio.run(callback(prompt, kwargs, ctx.obj.base_url))

    # The callback's docstring comes directly from the prompt description.
    callback.__doc__ = prompt.description
    return callback


def register_prompt_commands() -> None:
    """Register commands for all available prompts dynamically."""
    # Create an ivy subcommand for each prompt...
    for prompt_id in prompt_registry.list_prompts():
        prompt = prompt_registry.get_prompt(prompt_id)
        callback = create_command_callback(prompt_id)

        # Dynamically build the command with the parameters from the prompt.
        param_options = []
        for param in prompt.parameters:
            # Other parameters are all required.
            param_options.append(
                click.Option(
                    [f"--{param.name}"],
                    required=True,
                    help=param.description,
                )
            )

        # Create a new command with the parameters.
        command = click.Command(
            name=prompt_id,
            callback=callback,
            help=prompt.description,
            params=param_options,
        )

        # Add the command directly to the main CLI group.
        cli.add_command(command)


# Register all prompt commands
register_prompt_commands()


if __name__ == "__main__":
    cli(obj=CliContext())
