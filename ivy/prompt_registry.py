from pathlib import Path

import yaml

from ivy.models import TextTaskPrompt


class PromptRegistry:
    """A registry of prompts for text processing tasks."""
    _prompts_dir: Path | None = None

    def __init__(self, prompts_dir: Path | None = None):
        """Initialize the prompt registry.

        Args:
            prompts_dir: Optional directory containing prompt YAML files. If not provided,
                        will use the default prompts directory in the ivy package.
        """
        if prompts_dir is None:
            # Use the prompts directory in the ivy package
            self._prompts_dir = Path(__file__).parent / "prompts"
        else:
            self._prompts_dir = prompts_dir

        # Load all prompts from the directory
        self._prompts = {}
        self._load_prompts()

    def _load_prompts(self) -> None:
        """Load all prompts from the prompts directory."""
        if not self._prompts_dir or not self._prompts_dir.exists():
            return

        for yaml_file in self._prompts_dir.glob("*.yaml"):
            try:
                with open(yaml_file) as f:
                    yaml_data = yaml.safe_load(f)
                    prompt = TextTaskPrompt.from_yaml(yaml_data)
                    self.register_prompt(prompt)
            except Exception as e:
                print(f"Error loading prompt from {yaml_file}: {e}")

    def register_prompt(self, prompt: TextTaskPrompt) -> None:
        """Register a prompt for a text processing task."""
        if prompt.prompt_id in self._prompts:
            raise ValueError(f"Prompt with ID {prompt.prompt_id} already registered")
        self._prompts[prompt.prompt_id] = prompt

    def get_prompt(self, prompt_id: str) -> TextTaskPrompt:
        """Get a prompt for a text processing task."""
        if prompt_id not in self._prompts:
            raise KeyError(f"Prompt {prompt_id} not found in registry")
        return self._prompts[prompt_id]

    def list_prompts(self) -> list[str]:
        """List all registered prompt IDs."""
        return list(self._prompts.keys())
