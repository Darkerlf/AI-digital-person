def chunk_text(content_text: str, target_size: int = 600) -> list[dict[str, str | int]]:
    paragraphs = [paragraph.strip() for paragraph in content_text.splitlines() if paragraph.strip()]
    if not paragraphs and content_text.strip():
        paragraphs = [content_text.strip()]

    chunks: list[dict[str, str | int]] = []
    current = ""
    chunk_index = 0

    for paragraph in paragraphs:
        if len(current) + len(paragraph) > target_size and current:
            chunks.append(
                {
                    "chunk_index": chunk_index,
                    "chunk_text": current,
                    "token_count": len(current),
                    "source_section": f"chunk-{chunk_index}",
                }
            )
            chunk_index += 1
            current = paragraph
        else:
            current = f"{current}\n{paragraph}".strip()

    if current:
        chunks.append(
            {
                "chunk_index": chunk_index,
                "chunk_text": current,
                "token_count": len(current),
                "source_section": f"chunk-{chunk_index}",
            }
        )

    return chunks
