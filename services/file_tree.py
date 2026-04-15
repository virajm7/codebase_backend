import os

def get_file_tree(repo_path):
    files = []

    for root, dirs, filenames in os.walk(repo_path):
        # ignore useless folders
        dirs[:] = [d for d in dirs if d not in [
            ".git", "__pycache__", "node_modules", "venv", "dist", "build"
        ]]

        for file in filenames:
            if file.endswith((".py", ".js", ".ts")):
                full_path = os.path.join(root, file)

                # clean path (remove repo prefix)
                clean_path = full_path.replace(repo_path + os.sep, "")
                files.append(clean_path)

    return files


def build_tree_structure(files):
    tree = {}

    for file_path in files:
        parts = file_path.split(os.sep)

        current = tree
        for i, part in enumerate(parts):
            if part not in current:
                # 🔥 FIX: file = None
                if i == len(parts) - 1:
                    current[part] = None
                else:
                    current[part] = {}

            current = current[part] if current[part] is not None else {}

    return tree
    tree = {}

    for file_path in files:
        parts = file_path.split(os.sep)

        current = tree
        for part in parts:
            if part not in current:
                current[part] = {}
            current = current[part]

    return tree

def format_tree(tree, prefix=""):
    lines = []

    keys = list(tree.keys())
    for i, key in enumerate(keys):
        is_last = i == len(keys) - 1

        connector = "└── " if is_last else "├── "
        lines.append(prefix + connector + key)

        if tree[key]:  # if folder has children
            extension = "    " if is_last else "│   "
            lines.extend(format_tree(tree[key], prefix + extension))

    return lines

from services.llm import call_llm


def summarize_file(repo_path, file_path):
    full_path = os.path.join(repo_path, file_path)

    try:
        with open(full_path, "r", errors="ignore") as f:
            code = f.read()[:1000]

        prompt = f"""
        Explain this code file in ONE short line.

        File path: {file_path}

        Code:
        {code}
        """

        result = call_llm(prompt)

        print(f"SUCCESS: {file_path}")  # debug
        return result.strip()

    except Exception as e:
        print(f"ERROR in {file_path}: {e}")  # 🔥 IMPORTANT DEBUG
        return "Could not analyze"

import time

def add_file_descriptions(repo_path, files):
    descriptions = {}

    for file in files:
        print(f"Analyzing: {file}")

        desc = summarize_file(repo_path, file)
        descriptions[file] = desc

        time.sleep(2)  # 🔥 IMPORTANT: prevent rate limit

    return descriptions

def summarize_all_files(repo_path, files):
    combined_code = ""

    for file in files:
        full_path = os.path.join(repo_path, file)

        try:
            with open(full_path, "r", errors="ignore") as f:
                code = f.read()[:800]  # limit per file

            combined_code += f"\n\nFILE: {file}\n{code}"

        except:
            continue

    prompt = f"""
    You are analyzing a codebase.

    For each file below, give ONE line description.

    Return in JSON format:
    {{
        "file_path": "description"
    }}

    Code:
    {combined_code}
    """

    result = call_llm(prompt)

    print("BATCH RESULT:", result)

    return result

def format_tree_with_desc(tree, descriptions, prefix=""):
    lines = []

    keys = list(tree.keys())
    for i, key in enumerate(keys):
        is_last = i == len(keys) - 1

        connector = "└── " if is_last else "├── "

        # full path build (important)
        current_path = key if prefix == "" else prefix.replace("│   ", "").replace("    ", "") + key

        # normalize path
        desc = descriptions.get(current_path.replace("\\", "/"), "")

        if desc:
            line = f"{connector}{key} → {desc}"
        else:
            line = f"{connector}{key}"

        lines.append(line)

        if tree[key]:
            extension = "    " if is_last else "│   "
            lines.extend(format_tree_with_desc(tree[key], descriptions, prefix + extension))

    return lines

def generate_project_summary(repo_path, files):
    combined_code = ""

    for file in files[:5]:  # limit for safety
        full_path = os.path.join(repo_path, file)

        try:
            with open(full_path, "r", errors="ignore") as f:
                code = f.read()[:500]

            combined_code += f"\n\nFILE: {file}\n{code}"

        except:
            continue

    prompt = f"""
    You are analyzing a codebase.

    Give a HIGH LEVEL summary of this project.

    Include:
    - what the project does
    - main components
    - tech stack

    Keep it short (3-5 lines).

    Code:
    {combined_code}
    """

    return call_llm(prompt)

def get_file_content(repo_path, file_path):
    import os

    full_path = os.path.join(repo_path, file_path)

    try:
        with open(full_path, "r", errors="ignore") as f:
            return f.read()[:5000]  # limit size
    except:
        return ""

import re

def extract_imports(code):
    imports = []

    # match: from services.utils import ...
    pattern1 = r'from\s+([\w\.]+)\s+import'

    # match: import services.utils
    pattern2 = r'import\s+([\w\.]+)'

    matches = re.findall(pattern1, code) + re.findall(pattern2, code)

    for match in matches:
        # convert dot path → file path
        file_path = match.replace(".", "/") + ".py"
        imports.append(file_path)

    return imports