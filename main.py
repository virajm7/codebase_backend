from fastapi import FastAPI
from pydantic import BaseModel
import json

from core.state import save_state, load_state

from services.chat import chat_with_repo
from services.clone_repo import clone_repo
from services.file_tree import (
    get_file_tree,
    build_tree_structure,
    summarize_all_files,
    format_tree_with_desc,
    generate_project_summary
)

app = FastAPI()


class RepoRequest(BaseModel):
    repo_url: str


class ChatRequest(BaseModel):
    question: str


@app.get("/")
def home():
    return {"message": "Running"}


# 🔥 FIXED JSON CLEANER
def clean_llm_json(output: str):
    output = output.strip()

    if output.startswith("```"):
        parts = output.split("```")
        if len(parts) >= 2:
            output = parts[1]

    if output.startswith("json"):
        output = output[4:]

    if output.endswith("```"):
        output = output[:-3]

    # 🔥 IMPORTANT FIX
    if "}" in output:
        output = output[:output.rfind("}") + 1]

    return output.strip()


# =====================
# LOAD
# =====================
@app.post("/load")
def load_repo_api(data: RepoRequest):
    path = clone_repo(data.repo_url)
    repo_name = path.split("/")[-1]

    save_state({
        "name": repo_name,
        "path": path
    })

    return {"message": f"Repo '{repo_name}' loaded successfully"}


# =====================
# ANALYZE
# =====================
@app.post("/analyze")
def analyze():
    state = load_state()

    if not state.get("path"):
        return {"error": "No repo loaded. Call /load first."}

    path = state["path"]

    files = get_file_tree(path)

    batch_result = summarize_all_files(path, files)

    try:
        cleaned = clean_llm_json(batch_result)
        descriptions = json.loads(cleaned)

        # 🔥 FIX BACKSLASH ISSUE
        descriptions = {
            k.replace("\\", "/"): v
            for k, v in descriptions.items()
        }

    except Exception as e:
        print("JSON parse error:", e)
        descriptions = {}

    # 🔥 BUILD TREE DICT
    tree = build_tree_structure(files)

    project_summary = generate_project_summary(path, files)

    state.update({
        "files": files,
        "descriptions": descriptions
    })
    save_state(state)

    return {
        "repo_name": state["name"],
        "tree_dict": tree,  # 🔥 IMPORTANT
        "project_summary": project_summary,
        "total_files": len(files)
    }


# =====================
# CHAT
# =====================
@app.post("/chat")
def chat_api(data: ChatRequest):
    state = load_state()

    if not state.get("path"):
        return {"error": "No repo loaded. Call /load first."}

    if not state.get("descriptions"):
        return {"error": "Repo not analyzed. Call /analyze first."}

    result = chat_with_repo(
        data.question,
        state["descriptions"],
        state["path"]
    )

    return result