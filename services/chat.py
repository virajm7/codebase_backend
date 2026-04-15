from services.llm import call_llm
from services.file_tree import get_file_content
from services.response_formatter import format_chat_response


def build_chat_prompt(question, descriptions, repo_path):
    # 🔹 STEP 1 — find relevant files (keyword match)
    relevant_files = []

    for file, desc in descriptions.items():
        if any(word.lower() in desc.lower() for word in question.split()):
            relevant_files.append(file)

    # 🔹 fallback if nothing matched
    if not relevant_files:
        relevant_files = list(descriptions.keys())[:2]

    # 🔹 STEP 2 — load file content
    context = ""
    for file in relevant_files[:3]:  # limit to 3 files
        code = get_file_content(repo_path, file)
        context += f"\n\nFILE: {file}\n{code}"

    # 🔥 SYSTEM PROMPT (IMPROVED)
    system_prompt = """
You are a senior software engineer.

STRICT RULES:
- Explain clearly and in detail
- Use simple English
- Always reference file names
- If code is relevant, include it inside ``` blocks
- Use bullet points where helpful
- Keep answer clean and structured
- Do NOT add unnecessary text
"""

    # 🔥 FINAL PROMPT
    prompt = f"""
{system_prompt}

User Question:
{question}

Code Context:
{context}

Answer:
"""

    return prompt, relevant_files


def chat_with_repo(question, descriptions, repo_path):
    # 🔹 STEP 1 — build prompt
    prompt, used_files = build_chat_prompt(question, descriptions, repo_path)

    # 🔹 STEP 2 — call LLM
    raw_answer = call_llm(prompt)

    # 🔹 STEP 3 — format response
    formatted = format_chat_response(raw_answer)

    return {
        "response": formatted,
        "used_files": used_files
    }