def format_chat_response(raw_output: str):
    return {
        "answer": raw_output.strip(),
        "summary": raw_output.split("\n")[0] if raw_output else "",
        "has_code": "```" in raw_output,
        "code_blocks": extract_code_blocks(raw_output),
        "bullets": extract_bullets(raw_output)
    }


def extract_code_blocks(text):
    blocks = []
    parts = text.split("```")

    for i in range(1, len(parts), 2):
        blocks.append(parts[i].strip())

    return blocks


def extract_bullets(text):
    lines = text.split("\n")
    bullets = []

    for line in lines:
        if line.strip().startswith(("-", "*", "•")):
            bullets.append(line.strip())

    return bullets