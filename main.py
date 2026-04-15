from fastapi import FastAPI
from pydantic import BaseModel
import json
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


@app.get("/")
def home():
    return {"message": "Running"}


# 🔥 CLEAN JSON FIX FUNCTION (OUTSIDE)
def clean_llm_json(output: str):
    output = output.strip()

    # remove ```json or ```
    if output.startswith("```"):
        parts = output.split("```")
        if len(parts) >= 2:
            output = parts[1]

    # remove 'json' prefix
    if output.startswith("json"):
        output = output[4:]

    # remove ending ```
    if output.endswith("```"):
        output = output[:-3]

    return output.strip()


@app.post("/analyze")
def analyze(data: RepoRequest):
    # 🔹 STEP 1 — clone repo
    path = clone_repo(data.repo_url)

    # 🔹 STEP 2 — get files
    files = get_file_tree(path)

    # 🔹 STEP 3 — get file descriptions (batch LLM)
    batch_result = summarize_all_files(path, files)

    try:
        cleaned = clean_llm_json(batch_result)
        descriptions = json.loads(cleaned)
    except Exception as e:
        print("JSON parse error:", e)
        descriptions = {}

    # 🔹 STEP 4 — build tree
    tree = build_tree_structure(files)

    # 🔹 STEP 5 — merge tree + descriptions
    tree_lines = format_tree_with_desc(tree, descriptions)
    pretty_tree = "\n".join(tree_lines)

    # 🔹 STEP 6 — project summary
    project_summary = generate_project_summary(path, files)

    return {
        "repo_name": path.split("/")[-1],
        "pretty_tree": pretty_tree,
        "descriptions": descriptions,
        "project_summary": project_summary,
        "total_files": len(files)
    }

class ChatRequest(BaseModel):
    repo_url: str
    question: str

@app.post("/chat")
def chat(data: ChatRequest):
    path = clone_repo(data.repo_url)
    files = get_file_tree(path)

    # reuse descriptions (IMPORTANT)
    batch_result = summarize_all_files(path, files)

    try:
        cleaned = clean_llm_json(batch_result)
        descriptions = json.loads(cleaned)
    except:
        descriptions = {}

    result = chat_with_repo(data.question, descriptions, path)

    return result