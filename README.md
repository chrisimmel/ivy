# Ivy

Ivy is a simple FastAPI service that performs text processing tasks using an LLM. It provides a REST API for text generation and processing, with a CLI tool available for convenient interaction.

## Prerequisites

- Python 3.8 or higher
- [uv](https://github.com/astral-sh/uv) (Python package installer and resolver)

## Quick Start

1. Install uv (if you haven't already):

   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. Create and activate a virtual environment:

   ```bash
   uv venv
   source .venv/bin/activate  # On Unix/macOS
   # or
   .venv\Scripts\activate     # On Windows
   ```

3. Install dependencies:

   ```bash
   uv pip install -e ".[dev]"
   ```

## Environment

You will need an API key for any LLM provider referenced by the prompts (currently
OpenAI and Anthropic).

Copy .env.template to .env, and set your values for `OPENAI_API_KEY` and `ANTHROPIC_API_KEY`.

## Running the Service

### Development Mode

Start the service with auto-reload for development:

```bash
uvicorn ivy.app:app --reload
```

The service will be available at http://localhost:8000

### Production Mode

For production deployment, use multiple workers and proper host binding:

```bash
uvicorn ivy.app:app --host 0.0.0.0 --port 8000 --workers 4
```

### API Documentation

Once the service is running, you can access:

- Interactive API docs: http://localhost:8000/docs
- Alternative API docs: http://localhost:8000/redoc

## Using the CLI

The CLI tool provides a convenient way to interact with the service. Each text processing capability defined in the prompt registry is automatically available as a top-level command.

### Basic Usage

```bash
# Check service health
ivy health

# List available commands
ivy --help
```

### Text Processing Commands

All text processing capabilities are available as direct commands:

```bash
# Sentiment analysis
ivy sentiment --text "I love this project!"

# Text summarization
ivy summarize --text "Lorem ipsum dolor sit amet, consectetur adipiscing elit..."

# Get keywords from text
ivy keywords --text "Artificial intelligence and machine learning are transforming..."

# Translate text
ivy translate --text "Hello, world!" --language "Spanish"
```

### Command Help

Each command provides detailed help with its options:

```bash
# Get help for a specific command
ivy sentiment --help
```

### Custom Server

By default, the CLI connects to a local server at http://localhost:8000, but you can specify a different server:

```bash
# Connect to a different server
ivy --base-url http://custom-server:8080 sentiment --input-text "Amazing work!"
```

### Adding New Prompts

The service and CLI dynamically load commands from the prompt registry. To add a new prompt, simply create a new YAML file in the `ivy/prompts/` directory with the appropriate structure.
See the existing ones for examples. Each prompt can have its own specialized parameters, and
these will automatically be reflected in the CLI and help.
s
You may also reference additional LLM providers and models. Any provider supported by the
[Instructor library](https://github.com/567-labs/instructor) is nominally supported, but only the library dependencies for OpenAI and Anthropic are installed by default.

## Development

- Install development dependencies (already included in the quick start)
- Lint code: `ruff check .`

## Project Structure

```text
ivy/
├── app.py              # FastAPI service implementation
├── cli/                # CLI implementation
│   └── cli.py          # Dynamic CLI using Click
├── llm.py              # LLM service integration layer
├── prompt_registry.py  # Prompt management system
├── prompts/            # YAML prompt definitions
│   ├── sentiment.yaml  # Sentiment analysis prompt
│   └── summarize.yaml  # Text summarization prompt
│   └── etc.            # Other prompts
├── pyproject.toml      # Project metadata and dependencies
└── README.md           # This file
```
