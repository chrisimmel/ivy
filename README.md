# Ivy

Ivy is a simple FastAPI service that performs text processing tasks using an LLM. It provides a REST API for text generation and processing, with a CLI tool available for convenient interaction.

## Prerequisites

- Python 3.11 or higher
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

You will need an API key for any LLM provider referenced by the prompts (currently OpenAI, Anthropic, and Mistral).

Copy .env.template to .env, and set your values for `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, and `MISTRAL_API_KEY`.

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

Once the service is running, you can see full API documentation at:

- Interactive API docs: http://localhost:8000/docs
- Alternative API docs: http://localhost:8000/redoc

There are two endpoints:

- /health - a simple endpoint to test whether the service is up.
- /generate - a generic endpoint that lets you use any of the prompts with given parameters.

You can test the API directly via curl or Postman.

```bash
curl -X POST \
    http://localhost:8000/generate \
    -H "Content-Type: application/json" \
    -d '{
      "prompt_id": "sentiment",
      "parameters": {
        "text": "I really love using this service! It makes my work so much easier."
      }
    }'
```

```bash
curl -X POST \
    http://localhost:8000/generate \
    -H "Content-Type: application/json" \
    -d '{
      "prompt_id": "summarize",
      "parameters": {
        "text": "https://www.lettria.com/"
      }
    }'
```

## Using the CLI

The CLI tool provides a convenient way to interact with the service. Each text processing capability defined in the prompt registry is automatically available as a top-level command.

### Basic Usage

```bash
# Check service health
ivy health
```

```bash
# List available commands
ivy --help
```

### Text Processing Commands

All text processing capabilities are available as direct commands:

```bash
# Sentiment analysis
ivy sentiment --text "Everyone loves cute fuzzy animals"
```

```bash
# Text summarization
ivy summarize --text "Lorem ipsum dolor sit amet, consectetur adipiscing elit..."
```

```bash
# Get keywords from text
ivy keywords --text "Artificial intelligence and machine learning are transforming..."
```

```bash
# Translate text
ivy translate --text "Hello, world" --language "Spanish"
```

```bash
# Compare texts
ivy compare --text1 "ABC" --text2 "123"
```

### Drawing Text from URLs

A URL can be given for any parameter that otherwise would take input text, in which case
the text will be drawn from a markdown rendering of the web page at the given URL.

```bash
# Sentiment analysis
ivy sentiment --text https://shakespearequoteoftheday.com/
```

```bash
# Text summarization
ivy summarize --text https://fr.wikipedia.org/wiki/Oulipo
```

```bash
# Translate text
ivy translate --text https://en.wikipedia.org/wiki/Armenians --language "Արեւմտահայերէն"
```

```bash
# Compare texts
ivy compare --text1 https://github.com/chrisimmel/calliope --text2 https://chrisimmel.com/collection/calliope
```

### Command Help

Each command provides detailed help with its options:

```bash
# Get help for a specific command
ivy sentiment --help
```

### Adding New Prompts

The service and CLI dynamically load commands from the prompt registry. To add a new prompt, simply create a new YAML file in the `ivy/prompts/` directory with the appropriate structure.
See the existing ones for examples. Each prompt can have its own specialized parameters, and
these will automatically be reflected in the CLI and help.

You may also reference additional LLM providers and models. Support is included for OpenAI, Anthropic, and Mistral, but any provider supported by the
[Instructor library](https://github.com/567-labs/instructor) can be supported if you add the needed
library dependencies.

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
├── models.py           # Pydantic models
├── prompt_registry.py  # Prompt management system
├── prompts/            # YAML prompt definitions
│   ├── sentiment.yaml  # Sentiment analysis prompt
│   └── summarize.yaml  # Text summarization prompt
│   └── etc.            # Other prompts
├── pyproject.toml      # Project metadata and dependencies
├── README.md           # This file
└── utils.py            # Text utility functions
```
