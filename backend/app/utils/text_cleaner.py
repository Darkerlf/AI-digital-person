def normalize_text(content_text: str) -> str:
    lines = [line.strip() for line in content_text.splitlines()]
    cleaned = [line for line in lines if line]
    return "\n".join(cleaned) if cleaned else content_text.strip()
