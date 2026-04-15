from services.llm import call_llm
from services.file_tree import get_file_content
from services.response_formatter import format_chat_response


# =========================
# 🔥 FILE SCORING
# =========================
def score_file(question, file_path, description):
    score = 0
    q_words = question.lower().split()

    file_lower = file_path.lower()
    desc_lower = description.lower()

    for word in q_words:
        if word in file_lower:
            score += 3  # strong match
        if word in desc_lower:
            score += 2  # medium match

    return score


# =========================
# 🔥 SMART RETRIEVAL
# =========================
def get_relevant_files(question, descriptions):
    scored = []

    for file, desc in descriptions.items():
        s = score_file(question, file, desc)
        scored.append((file, s))

    # sort descending
    scored.sort(key=lambda x: x[1], reverse=True)

    # pick top 5 relevant
    top_files = [f for f, s in scored[:5] if s > 0]

    # fallback
    if not top_files:
        top_files = list(descriptions.keys())[:3]

    return top_files


# =========================
# 🔥 BUILD PROMPT
# =========================
def build_chat_prompt(question, descriptions, repo_path):
    relevant_files = get_relevant_files(question, descriptions)
    

    context = ""
    for file in relevant_files:
        code = get_file_content(repo_path, file)

        context += f"""
FILE: {file}
{code}

-------------------
"""

    # 🔥 detect code intent
    wants_code = any(word in question.lower() for word in [
        "code", "function", "implementation", "show"
    ])

    extra_instruction = ""
    if wants_code:
        extra_instruction = "\nUser specifically wants CODE. Include full function code."

    # 🔥 STRONG SYSTEM PROMPT
    system_prompt = """
You are a senior software engineer and codebase assistant.

Your job is to deeply understand and explain a codebase.

=========================
BEHAVIOR RULES
=========================

- Understand user intent, even if the question is informal or unclear
  Example:
  "proj" → "project"
  "where ai used" → "where is AI used in code"

- NEVER say "not found" unless absolutely certain
- If something is not directly visible, infer from:
  - file names
  - imports
  - structure
  - common patterns

- Always try to give a useful answer

=========================
CONTEXT USAGE
=========================

- Use ONLY the provided code as primary source
- But you are allowed to:
  - infer relationships
  - explain architecture
  - connect multiple files

- If user asks follow-up (like "show code"):
  → refer to previous discussion

=========================
OUTPUT FORMAT
=========================

1. Clear explanation (simple English)
2. Bullet points (key insights)
3. Code block (if user asks for code)

=========================
CODE RULES
=========================

- ALWAYS use triple backticks for code
- Use correct language (python, js, etc.)
- Keep proper indentation
- DO NOT compress code into one line
- DO NOT mix explanation inside code block

=========================
IMPORTANT
=========================

- Be confident
- Be helpful
- Think like a human developer, not a strict parser
"""
    prompt = f"""
{system_prompt}

{extra_instruction}

User Question:
{question}

Code Context:
{context}

Answer:
"""

    return prompt, relevant_files


# =========================
# 💬 CHAT FUNCTION
# =========================
def chat_with_repo(question, descriptions, repo_path):
    from core.state import load_state, save_state

    state = load_state()

    history = state.get("chat_history", [])

    # 🔥 Add current user message
    history.append({
        "role": "user",
        "content": question
    })

    # 🔥 Get last user question (important for follow-ups)
    last_user_question = None
    for msg in reversed(history[:-1]):
        if msg["role"] == "user":
            last_user_question = msg["content"]
            break

    # 🔥 Build base prompt
    prompt, used_files = build_chat_prompt(question, descriptions, repo_path)

    # 🔥 IMPROVED MEMORY FORMAT
    history_text = ""

    if last_user_question:
        history_text += f"Previous user question: {last_user_question}\n"

    history_text += "Recent conversation:\n"

    for msg in history[-6:]:
        role = "User" if msg["role"] == "user" else "Assistant"
        history_text += f"{role}: {msg['content']}\n"

    # 🔥 FINAL PROMPT
    final_prompt = f"""
You are continuing a conversation about a codebase like GitHub Copilot Chat.

=========================
CONVERSATION RULES
=========================

- This is a multi-turn conversation
- Use previous messages to understand user intent
- Follow-up questions MUST depend on previous context

Examples:
- "show code" → show code of last discussed file
- "where is it used?" → refer to last mentioned function/file
- "what about this?" → infer from previous answer

=========================
MEMORY HANDLING
=========================

- Always look at previous user question before answering
- If current question is vague:
  → connect it to last discussed topic

- NEVER ignore conversation history
- NEVER treat each question independently

=========================
SMART INTERPRETATION
=========================

- Understand short/informal queries:
  "proj" → project
  "utils?" → explain utils.py
  "where ai used" → where is AI used in code

- If unclear, make best logical assumption instead of failing

=========================
CONTEXT PRIORITY
=========================

1. Previous conversation (VERY IMPORTANT)
2. Current question
3. Code context

=========================
OUTPUT FORMAT
=========================

1. Explanation (simple English)
2. Bullet points
3. Code block (if needed)

=========================
CRITICAL
=========================

- DO NOT say "not found" unless 100% sure
- ALWAYS try to give a useful answer
- Think like a senior developer helping a junior

-------------------------

Previous Conversation:
{history_text}

-------------------------

{prompt}
"""

    raw_answer = call_llm(final_prompt)

    if raw_answer:
        raw_answer = raw_answer.replace("\\n", "\n")

    # 🔥 Save assistant reply
    history.append({
        "role": "assistant",
        "content": raw_answer
    })

    state["chat_history"] = history
    save_state(state)

    formatted = format_chat_response(raw_answer)

    return {
        "response": formatted,
        "used_files": used_files
    }