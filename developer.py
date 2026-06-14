"""
developer.py — Jarvis Advanced Developer Assistant
Features:
  1. AI Code Generator  — voice-ல் describe பண்ணா code generate ஆகும்
  2. Live Terminal       — voice-ல் terminal commands run பண்ணலாம்
  3. Create files        — py/html/js/css
  4. Run code            — output speak பண்ணும்
  5. Open project        — VS Code
  6. Git commands        — status/commit/push/pull
  7. Install packages    — pip install
  8. Bug fixer           — AI-ல் fix பண்ணும்
  9. Code explainer      — AI-ல் explain பண்ணும்
  10. Requirements gen   — auto requirements.txt
"""
import os
import subprocess
import datetime

# ─────────────────────────────────────────────────────────────
#  SETTINGS
# ─────────────────────────────────────────────────────────────
DEFAULT_PROJECT_FOLDER = r"C:\Users\prave\OneDrive\Desktop\Jarvis"
VSCODE_CMD             = "code"

FILE_TEMPLATES = {
    ".py":   '# Python file created by Jarvis\n# Created: {date}\n\nprint("Hello from Jarvis!")\n',
    ".html": '<!DOCTYPE html>\n<html lang="en">\n<head>\n    <meta charset="UTF-8">\n    <title>Page</title>\n</head>\n<body>\n    <h1>Hello from Jarvis!</h1>\n</body>\n</html>\n',
    ".js":   '// JavaScript file created by Jarvis\n// Created: {date}\n\nconsole.log("Hello from Jarvis!");\n',
    ".css":  '/* CSS file created by Jarvis */\n/* Created: {date} */\n\nbody {{\n    margin: 0;\n    padding: 0;\n}}\n',
    ".txt":  'Text file created by Jarvis\nCreated: {date}\n',
    ".json": '{{\n    "created": "{date}"\n}}\n',
}

# ─────────────────────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────────────────────
def _run_command(cmd, cwd=None):
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True,
            text=True, cwd=cwd or DEFAULT_PROJECT_FOLDER,
            timeout=30
        )
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except subprocess.TimeoutExpired:
        return "", "Command timed out", 1
    except Exception as e:
        return "", str(e), 1


def _get_extension(file_type):
    mapping = {
        "python": ".py", "py": ".py",
        "html":   ".html", "web": ".html",
        "javascript": ".js", "js": ".js",
        "css":    ".css", "style": ".css",
        "text":   ".txt", "txt": ".txt",
        "json":   ".json",
        "java":   ".java",
        "c":      ".c",   "cpp": ".cpp",
    }
    return mapping.get(file_type.lower().strip(), ".py")


def _clean_ai_code(code_text):
    """AI response-ல் இருக்கற markdown code blocks remove பண்ணும்."""
    lines = code_text.split('\n')
    clean = []
    in_block = False
    for line in lines:
        if line.strip().startswith('```'):
            in_block = not in_block
            continue
        clean.append(line)
    return '\n'.join(clean).strip()


# ─────────────────────────────────────────────────────────────
#  1. AI CODE GENERATOR 🤖
# ─────────────────────────────────────────────────────────────
def ai_generate_code(description, file_type="python", speak_fn=None):
    """
    Voice description → AI code generate → file save → VS Code open.
    Example: "create a calculator" → calculator.py with full code
    """
    from chatgpt import ask_chatgpt

    if speak_fn:
        speak_fn(f"Generating {file_type} code for {description}. Please wait.")

    # AI prompt
    ext    = _get_extension(file_type)
    lang   = file_type.capitalize()
    prompt = (
        f"Write complete working {lang} code for: {description}. "
        f"Requirements: "
        f"1. Complete functional code only. "
        f"2. No explanations, no markdown, no backticks. "
        f"3. Add comments for key sections. "
        f"4. Make it production ready. "
        f"Return ONLY the raw code."
    )

    code = ask_chatgpt(prompt)
    code = _clean_ai_code(code)

    if not code or len(code) < 10:
        return "Sorry, AI could not generate code. Please try again."

    # Filename from description
    filename = (
        description.lower()
        .replace(" ", "_")
        .replace("a ", "")
        .replace("an ", "")
        .replace("the ", "")
        [:25]
        .strip("_")
    )
    filename = filename + ext
    filepath = os.path.join(DEFAULT_PROJECT_FOLDER, filename)

    # Save file
    try:
        os.makedirs(DEFAULT_PROJECT_FOLDER, exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(code)
        # Open in VS Code
        os.system(f'{VSCODE_CMD} "{filepath}"')
        lines = len(code.split('\n'))
        return (
            f"Code generated! {filename} created with {lines} lines. "
            f"Opening in VS Code now."
        )
    except Exception as e:
        return f"Could not save file: {e}"


# ─────────────────────────────────────────────────────────────
#  2. LIVE TERMINAL CONTROL 🖥️
# ─────────────────────────────────────────────────────────────

# Safe commands list — dangerous commands block பண்றோம்
BLOCKED_COMMANDS = [
    "rm -rf", "del /f", "format", "shutdown", "rmdir /s",
    "del *", ":(){:|:&};:", "mkfs", "dd if="
]

def _is_safe_command(cmd):
    """Dangerous commands block பண்ணும்."""
    cmd_lower = cmd.lower()
    for blocked in BLOCKED_COMMANDS:
        if blocked in cmd_lower:
            return False
    return True


def run_terminal_command(command_text, cwd=None, speak_fn=None):
    """
    Voice-ல் சொன்ன terminal command run பண்ணும்.
    Output-ஐ speak பண்ணும்.
    """
    if not _is_safe_command(command_text):
        return "Sorry, that command is blocked for safety reasons."

    if speak_fn:
        speak_fn(f"Running: {command_text}")

    stdout, stderr, code = _run_command(command_text, cwd=cwd)

    if code == 0:
        if stdout:
            # Long output trim பண்ணு
            output = stdout[:300] if len(stdout) > 300 else stdout
            # Newlines → spaces for speaking
            output_spoken = output.replace('\n', '. ').replace('  ', ' ')
            return f"Done. Output: {output_spoken[:200]}"
        return "Command completed successfully."
    else:
        error = stderr[:150] if stderr else "Unknown error"
        return f"Command failed: {error}"


# Voice command → actual terminal command mapping
TERMINAL_VOICE_MAP = {
    # Python
    "python version":          "python --version",
    "check python":            "python --version",
    "pip version":             "pip --version",
    "list packages":           "pip list",
    "installed packages":      "pip list",

    # System
    "check disk":              "wmic logicaldisk get size,freespace,caption",
    "disk space":              "wmic logicaldisk get size,freespace,caption",
    "system info":             "systeminfo | findstr /C:\"OS Name\" /C:\"Total Physical Memory\"",
    "ip address":              "ipconfig | findstr IPv4",
    "network info":            "ipconfig | findstr IPv4",
    "running processes":       "tasklist | head -10",
    "cpu usage":               "wmic cpu get loadpercentage",

    # Files
    "list directory":          "dir",
    "show directory":          "dir",
    "current directory":       "cd",
    "where am i":              "cd",

    # Git shortcuts
    "git log":                 "git log --oneline -5",
    "recent commits":          "git log --oneline -5",
    "git branches":            "git branch",
    "show branches":           "git branch",

    # Venv
    "create virtual environment": "python -m venv venv",
    "create venv":             "python -m venv venv",
    "activate venv":           r"venv\Scripts\activate",

    # Tests
    "run tests":               "python -m pytest -v",
    "run pytest":              "python -m pytest -v",

    # Misc
    "clear terminal":          "cls",
    "ping google":             "ping google.com -n 4",
}


def handle_terminal_voice(command, cwd=None, speak_fn=None):
    """
    Voice command-ஐ terminal command-ஆ convert பண்ணி run பண்ணும்.
    """
    command_lower = command.lower().strip()

    # Direct map check
    for voice_cmd, terminal_cmd in TERMINAL_VOICE_MAP.items():
        if voice_cmd in command_lower:
            return run_terminal_command(terminal_cmd, cwd=cwd, speak_fn=speak_fn)

    # "run [command]" pattern — direct command
    for prefix in ["run command ", "terminal ", "execute command ",
                   "run in terminal ", "command "]:
        if command_lower.startswith(prefix):
            actual_cmd = command[len(prefix):].strip()
            if actual_cmd:
                return run_terminal_command(actual_cmd, cwd=cwd, speak_fn=speak_fn)

    return None


# ─────────────────────────────────────────────────────────────
#  3. BUG FIXER 🐛
# ─────────────────────────────────────────────────────────────
def fix_bugs(filename, speak_fn=None):
    """
    File-ஐ AI-கிட்ட அனுப்பி bugs fix பண்ணும்.
    """
    from chatgpt import ask_chatgpt

    filepath = os.path.join(DEFAULT_PROJECT_FOLDER, filename)
    if not filename.endswith(".py"):
        filepath += ".py"

    if not os.path.exists(filepath):
        return f"File {filename} not found."

    if speak_fn:
        speak_fn(f"Analyzing {filename} for bugs. Please wait.")

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            code = f.read()[:2000]

        prompt = (
            f"Fix all bugs in this Python code. "
            f"Return ONLY the fixed code, no explanation, no markdown:\n\n{code}"
        )
        fixed_code = ask_chatgpt(prompt)
        fixed_code = _clean_ai_code(fixed_code)

        if fixed_code and len(fixed_code) > 10:
            # Backup original
            backup_path = filepath + ".backup"
            with open(backup_path, "w", encoding="utf-8") as f:
                f.write(code)

            # Save fixed code
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(fixed_code)

            os.system(f'{VSCODE_CMD} "{filepath}"')
            return (
                f"Bugs fixed in {filename}! "
                f"Original saved as {filename}.backup. "
                f"Opening fixed version in VS Code."
            )
        return "AI could not fix the bugs. Please check manually."
    except Exception as e:
        return f"Error fixing bugs: {e}"


# ─────────────────────────────────────────────────────────────
#  4. CODE EXPLAINER 🔍
# ─────────────────────────────────────────────────────────────
def explain_code(filename, speak_fn=None):
    """File-ஐ AI-கிட்ட அனுப்பி explain பண்ணும்."""
    from chatgpt import ask_chatgpt

    filepath = os.path.join(DEFAULT_PROJECT_FOLDER, filename)
    if not filename.endswith(".py"):
        filepath += ".py"

    if not os.path.exists(filepath):
        return f"File {filename} not found."

    if speak_fn:
        speak_fn(f"Reading {filename}...")

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            code = f.read()[:1500]

        prompt = (
            f"Explain this code in simple English in exactly 3 sentences. "
            f"Be concise and clear:\n\n{code}"
        )
        explanation = ask_chatgpt(prompt)
        return explanation
    except Exception as e:
        return f"Error explaining code: {e}"


# ─────────────────────────────────────────────────────────────
#  5. FILE OPERATIONS
# ─────────────────────────────────────────────────────────────
def create_file(filename, file_type="python", folder=None):
    folder = folder or DEFAULT_PROJECT_FOLDER
    ext    = _get_extension(file_type)

    if not any(filename.endswith(e) for e in FILE_TEMPLATES.keys()):
        filename = filename + ext

    filename = filename.strip().replace(" ", "_")
    filepath = os.path.join(folder, filename)

    if os.path.exists(filepath):
        return f"File {filename} already exists."

    date    = datetime.datetime.now().strftime("%d %b %Y %I:%M %p")
    content = FILE_TEMPLATES.get(ext, "# Created by Jarvis\n").format(date=date)

    try:
        os.makedirs(folder, exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        os.system(f'{VSCODE_CMD} "{filepath}"')
        return f"File {filename} created and opened in VS Code"
    except Exception as e:
        return f"Could not create file: {e}"


def run_python_file(filename, folder=None):
    folder = folder or DEFAULT_PROJECT_FOLDER
    if not filename.endswith(".py"):
        filename += ".py"
    filepath = os.path.join(folder, filename)
    if not os.path.exists(filepath):
        return f"File {filename} not found."
    stdout, stderr, code = _run_command(f'python "{filepath}"', cwd=folder)
    if code == 0:
        output = stdout[:200] if stdout else "no output"
        return f"Ran successfully. Output: {output}"
    error = stderr[:150] if stderr else "unknown error"
    return f"Error: {error}"


def list_files(folder=None, extension=None):
    folder = folder or DEFAULT_PROJECT_FOLDER
    if not os.path.exists(folder):
        return "Folder not found."
    try:
        all_files = os.listdir(folder)
        if extension:
            ext   = _get_extension(extension)
            files = [f for f in all_files if f.endswith(ext)]
        else:
            files = [f for f in all_files
                     if os.path.isfile(os.path.join(folder, f))]
        if not files:
            return "No files found."
        shown = files[:5]
        if len(files) > 5:
            return f"Found {len(files)} files. First 5: {', '.join(shown)}"
        return f"Found {len(files)} file{'s' if len(files)>1 else ''}: {', '.join(files)}"
    except Exception as e:
        return f"Error listing files: {e}"


# ─────────────────────────────────────────────────────────────
#  6. PROJECT OPERATIONS
# ─────────────────────────────────────────────────────────────
def open_project(project_path=None):
    path = project_path or DEFAULT_PROJECT_FOLDER
    if not os.path.exists(path):
        return "Project folder not found."
    os.system(f'{VSCODE_CMD} "{path}"')
    return "Opening project in VS Code"


def install_package(package_name, speak_fn=None):
    if not package_name or package_name == "none":
        return "No package name provided."
    package_name = package_name.strip().lower()
    if speak_fn:
        speak_fn(f"Installing {package_name}")
    stdout, stderr, code = _run_command(f"pip install {package_name}")
    if code == 0:
        return f"Package {package_name} installed successfully"
    return f"Could not install {package_name}: {stderr[:100]}"


# ─────────────────────────────────────────────────────────────
#  7. GIT COMMANDS
# ─────────────────────────────────────────────────────────────
def git_status(folder=None):
    folder = folder or DEFAULT_PROJECT_FOLDER
    stdout, stderr, code = _run_command("git status --short", cwd=folder)
    if code != 0:
        return "This folder is not a git repository."
    if not stdout:
        return "Git: everything is up to date"
    lines = stdout.split('\n')
    return f"Git: {len(lines)} file{'s' if len(lines)>1 else ''} changed"


def git_commit(message, folder=None):
    folder = folder or DEFAULT_PROJECT_FOLDER
    if not message or message == "none":
        message = f"Update {datetime.datetime.now().strftime('%d %b %Y')}"
    _run_command("git add .", cwd=folder)
    stdout, stderr, code = _run_command(f'git commit -m "{message}"', cwd=folder)
    if code == 0:
        return f"Committed: {message}"
    return f"Git commit failed: {stderr[:80]}"


def git_push(folder=None):
    folder = folder or DEFAULT_PROJECT_FOLDER
    stdout, stderr, code = _run_command("git push", cwd=folder)
    return "Code pushed to GitHub" if code == 0 else f"Push failed: {stderr[:80]}"


def git_pull(folder=None):
    folder = folder or DEFAULT_PROJECT_FOLDER
    stdout, stderr, code = _run_command("git pull", cwd=folder)
    return "Pulled latest changes" if code == 0 else f"Pull failed: {stderr[:80]}"


# ─────────────────────────────────────────────────────────────
#  8. REQUIREMENTS GENERATOR
# ─────────────────────────────────────────────────────────────
def generate_requirements(folder=None):
    folder = folder or DEFAULT_PROJECT_FOLDER
    imports = set()
    stdlib  = {"os","sys","re","json","time","datetime","math","random",
               "threading","subprocess","pathlib","collections","itertools",
               "functools","typing","abc","io","copy","hashlib","base64"}
    try:
        for fname in os.listdir(folder):
            if fname.endswith(".py"):
                fpath = os.path.join(folder, fname)
                with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith("import "):
                            pkg = line.split()[1].split(".")[0]
                            if pkg not in stdlib:
                                imports.add(pkg)
                        elif line.startswith("from "):
                            pkg = line.split()[1].split(".")[0]
                            if pkg not in stdlib:
                                imports.add(pkg)

        req_path = os.path.join(folder, "requirements.txt")
        with open(req_path, "w") as f:
            f.write("\n".join(sorted(imports)))

        return f"requirements.txt created with {len(imports)} packages: {', '.join(sorted(imports))}"
    except Exception as e:
        return f"Error: {e}"


# ─────────────────────────────────────────────────────────────
#  MAIN COMMAND HANDLER
# ─────────────────────────────────────────────────────────────
def handle_dev_command(command, listen_fn, speak_fn):
    cmd = command.lower().strip()

    # ── AI CODE GENERATOR ─────────────────────────────────────
    if any(w in cmd for w in [
        "generate code", "generate a", "generate an",
        "create a code", "write code", "write a code",
        "code for", "make a program", "build a",
        "ai generate", "generate python", "generate html",
        "generate javascript", "generate script"
    ]):
        # File type detect
        file_type = "python"
        for ft in ["html", "javascript", "js", "css", "python"]:
            if ft in cmd:
                file_type = ft
                break

        speak_fn("What should I code for you?")
        description = listen_fn()
        if description and description != "none":
            return ai_generate_code(description, file_type, speak_fn=speak_fn)
        return "No description heard. Please try again."

    # ── TERMINAL COMMANDS ─────────────────────────────────────
    elif any(w in cmd for w in [
        "terminal", "run command", "execute command",
        "command ", "python version", "check python",
        "pip version", "list packages", "installed packages",
        "check disk", "disk space", "system info",
        "ip address", "network info", "current directory",
        "where am i", "git log", "recent commits",
        "git branches", "show branches",
        "create virtual environment", "create venv",
        "activate venv", "run tests", "run pytest",
        "clear terminal", "ping google"
    ]):
        result = handle_terminal_voice(cmd, speak_fn=speak_fn)
        if result:
            return result
        # Direct command
        speak_fn("What command should I run?")
        user_cmd = listen_fn()
        if user_cmd and user_cmd != "none":
            return run_terminal_command(user_cmd, speak_fn=speak_fn)
        return "No command heard."

    # ── BUG FIXER ─────────────────────────────────────────────
    elif any(w in cmd for w in [
        "fix bugs", "fix code", "debug file",
        "fix errors", "fix my code", "find bugs"
    ]):
        speak_fn("Which file should I fix?")
        filename = listen_fn()
        if filename and filename != "none":
            return fix_bugs(filename, speak_fn=speak_fn)
        return "No filename heard."

    # ── CODE EXPLAINER ────────────────────────────────────────
    elif any(w in cmd for w in [
        "explain code", "explain file",
        "what does this code do", "describe code"
    ]):
        speak_fn("Which file should I explain?")
        filename = listen_fn()
        if filename and filename != "none":
            return explain_code(filename, speak_fn=speak_fn)
        return "No filename heard."

    # ── CREATE FILE ───────────────────────────────────────────
    elif any(w in cmd for w in [
        "create file", "new file", "make file",
        "create python", "new python", "create html",
        "create javascript", "create css"
    ]):
        file_type = "python"
        for ft in ["python", "html", "javascript", "js", "css", "text", "json"]:
            if ft in cmd:
                file_type = ft
                break
        speak_fn("What should I name the file?")
        filename = listen_fn()
        if filename and filename != "none":
            return create_file(filename, file_type)
        return "No filename heard."

    # ── RUN CODE ──────────────────────────────────────────────
    elif any(w in cmd for w in [
        "run code", "run file", "run python",
        "execute file", "execute code"
    ]):
        speak_fn("Which file should I run?")
        filename = listen_fn()
        if filename and filename != "none":
            speak_fn(f"Running {filename}")
            return run_python_file(filename)
        return "No filename heard."

    # ── OPEN PROJECT ──────────────────────────────────────────
    elif any(w in cmd for w in [
        "open project", "open vs code",
        "open vscode", "open code editor"
    ]):
        return open_project()

    # ── LIST FILES ────────────────────────────────────────────
    elif any(w in cmd for w in [
        "list files", "show files", "what files"
    ]):
        ext = None
        for ft in ["python", "html", "javascript", "css"]:
            if ft in cmd:
                ext = ft
                break
        return list_files(extension=ext)

    # ── INSTALL PACKAGE ───────────────────────────────────────
    elif any(w in cmd for w in [
        "install package", "install library",
        "pip install", "install module"
    ]):
        speak_fn("Which package should I install?")
        package = listen_fn()
        if package and package != "none":
            return install_package(package, speak_fn=speak_fn)
        return "No package name heard."

    # ── REQUIREMENTS ──────────────────────────────────────────
    elif any(w in cmd for w in [
        "generate requirements", "create requirements",
        "requirements file", "requirements txt"
    ]):
        return generate_requirements()

    # ── GIT ───────────────────────────────────────────────────
    elif any(w in cmd for w in ["git status", "check git", "git changes"]):
        return git_status()

    elif any(w in cmd for w in [
        "git commit", "commit code", "commit changes", "save to git"
    ]):
        speak_fn("What is the commit message?")
        message = listen_fn()
        return git_commit(message)

    elif any(w in cmd for w in ["git push", "push code", "push to github"]):
        speak_fn("Pushing code, please wait")
        return git_push()

    elif any(w in cmd for w in ["git pull", "pull code", "sync code"]):
        return git_pull()

    return None