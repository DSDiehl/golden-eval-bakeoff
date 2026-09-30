"""Prompt loader utility for versioned markdown constitutions."""

from pathlib import Path

PROMPTS_DIR = Path(__file__).parent


def load_prompt(name: str) -> str:
    """Loads prompt text from a markdown file in the prompts directory.

    Args:
        name: Filename or base name of the prompt (e.g., 'coordinator.md' or 'coordinator').

    Returns:
        The markdown prompt content as a string.

    Raises:
        FileNotFoundError: If the specified prompt markdown file does not exist.
    """
    filename = name if name.endswith(".md") else f"{name}.md"
    file_path = PROMPTS_DIR / filename
    if not file_path.exists():
        raise FileNotFoundError(f"Prompt file '{file_path}' not found.")
    return file_path.read_text(encoding="utf-8").strip()
