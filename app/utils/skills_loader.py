from pathlib import Path


def load_skill(skill_path: str) -> str:
    """
    Load a Markdown skill file.
    """

    path = Path(skill_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Skill file not found: {skill_path}"
        )

    return path.read_text(
        encoding="utf-8"
    )
