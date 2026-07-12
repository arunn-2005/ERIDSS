from pathlib import Path


def extract_txt_text(file_path: Path) -> str:
    """
    Extract text from a TXT file.
    """

    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()