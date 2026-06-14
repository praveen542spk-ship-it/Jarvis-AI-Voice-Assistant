"""
tasks.py — Jarvis Personal Assistant
- Add / view / complete / delete tasks
- Set reminder — 5 மணி ஆனா உடனே voice-ல் சொல்லும் (no popup)
- Tasks saved to tasks.json
"""
import json
import os
import threading
import time
import datetime
import re
import subprocess

TASKS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tasks.json")


# ─────────────────────────────────────────────────────────────
#  STORAGE
# ─────────────────────────────────────────────────────────────
def _load_tasks():
    if os.path.exists(TASKS_FILE):
        try:
            with open(TASKS_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return []
    return []


def _save_tasks(tasks):
    try:
        with open(TASKS_FILE, "w") as f:
            json.dump(tasks, f, indent=2)
    except Exception as e:
        print(f"[Tasks] Save error: {e}")


# ─────────────────────────────────────────────────────────────
#  SPEAK — subprocess use பண்றோம் (thread-safe, no popup)
# ─────────────────────────────────────────────────────────────
def _speak_in_thread(text):
    """
    Reminder thread-ல் இருந்து safe-ஆ speak பண்ண
    subprocess use பண்றோம் — no popup, direct voice.
    """
    safe_text = text.replace("'", "").replace('"', "")
    script = (
        "import pyttsx3;"
        "e=pyttsx3.init();"
        "e.setProperty('rate', 160);"
        "e.setProperty('volume', 1.0);"
        f"e.say('{safe_text}');"
        "e.runAndWait();"
        "e.stop()"
    )
    try:
        subprocess.run(["python", "-c", script], timeout=20)
    except Exception as e:
        print(f"[Speak] Error: {e}")


# ─────────────────────────────────────────────────────────────
#  TASK OPERATIONS
# ─────────────────────────────────────────────────────────────
def add_task(task_text):
    task_text = task_text.strip()
    if not task_text or task_text == "none":
        return "No task text provided."
    tasks = _load_tasks()
    task  = {
        "id":      len(tasks) + 1,
        "text":    task_text,
        "done":    False,
        "created": datetime.datetime.now().strftime("%d %b %Y %I:%M %p")
    }
    tasks.append(task)
    _save_tasks(tasks)
    return f"Task added: {task_text}"


def get_all_tasks():
    tasks = _load_tasks()
    if not tasks:
        return "You have no tasks. Say add task to create one."
    pending   = [t for t in tasks if not t["done"]]
    completed = [t for t in tasks if t["done"]]
    result = ""
    if pending:
        result += f"You have {len(pending)} pending task{'s' if len(pending)>1 else ''}. "
        for t in pending:
            result += f"Task {t['id']}: {t['text']}. "
    else:
        result += "No pending tasks. "
    if completed:
        result += f"And {len(completed)} completed task{'s' if len(completed)>1 else ''}."
    return result.strip()


def get_pending_tasks():
    tasks   = _load_tasks()
    pending = [t for t in tasks if not t["done"]]
    if not pending:
        return "No pending tasks. All done!"
    result = f"You have {len(pending)} pending task{'s' if len(pending)>1 else ''}. "
    for t in pending:
        result += f"Task {t['id']}: {t['text']}. "
    return result.strip()


def complete_task(task_id_or_text):
    tasks = _load_tasks()
    if not tasks:
        return "You have no tasks."
    matched = None
    try:
        task_id = int(task_id_or_text)
        for t in tasks:
            if t["id"] == task_id:
                matched = t
                break
    except (ValueError, TypeError):
        search = str(task_id_or_text).lower()
        for t in tasks:
            if search in t["text"].lower():
                matched = t
                break
    if matched:
        matched["done"]      = True
        matched["completed"] = datetime.datetime.now().strftime("%d %b %Y %I:%M %p")
        _save_tasks(tasks)
        return f"Task completed: {matched['text']}"
    return f"Could not find task {task_id_or_text}."


def delete_task(task_id_or_text):
    tasks = _load_tasks()
    if not tasks:
        return "You have no tasks."
    try:
        task_id   = int(task_id_or_text)
        new_tasks = [t for t in tasks if t["id"] != task_id]
    except (ValueError, TypeError):
        search    = str(task_id_or_text).lower()
        new_tasks = [t for t in tasks if search not in t["text"].lower()]
    if len(new_tasks) < len(tasks):
        _save_tasks(new_tasks)
        return "Task deleted successfully."
    return "Could not find task to delete."


def clear_completed():
    tasks   = _load_tasks()
    pending = [t for t in tasks if not t["done"]]
    removed = len(tasks) - len(pending)
    _save_tasks(pending)
    return f"Cleared {removed} completed task{'s' if removed!=1 else ''}."


def clear_all_tasks():
    tasks = _load_tasks()
    total = len(tasks)
    if total == 0:
        return "No tasks to delete."
    _save_tasks([])
    return f"All {total} tasks deleted successfully."


# ─────────────────────────────────────────────────────────────
#  TIME PARSER
# ─────────────────────────────────────────────────────────────
def _parse_time(time_str):
    """
    Any time format parse பண்ணும்.
    "5 pm" / "5:00 pm" / "5:23 pm" / "17:30" / "five pm"
    Returns: datetime object or None
    """
    if not time_str:
        return None

    original = time_str
    s = time_str.lower().strip()

    # Normalize variations → standard
    # "p.m." / "p m" / "pm" → "pm"
    # "a.m." / "a m" / "am" → "am"
    import re as _re
    s = _re.sub(r'p[\.\s]*m\.?', 'pm', s)
    s = _re.sub(r'a[\.\s]*m\.?', 'am', s)

    # Word → number
    word_map = {
        "one":"1","two":"2","three":"3","four":"4","five":"5",
        "six":"6","seven":"7","eight":"8","nine":"9","ten":"10",
        "eleven":"11","twelve":"12","o'clock":"","o clock":"","oclock":""
    }
    for w, d in word_map.items():
        s = s.replace(w, d)
    s = s.strip()

    # am/pm detect
    is_pm = None
    if "pm" in s:
        is_pm = True
        s = s.replace("pm","").strip()
    elif "am" in s:
        is_pm = False
        s = s.replace("am","").strip()

    hour = minute = None

    # "5:23" or "5:00" format
    m = re.search(r"(\d{1,2})[:\s](\d{2})", s)
    if m:
        hour   = int(m.group(1))
        minute = int(m.group(2))
    else:
        # Just hour "5"
        m = re.search(r"(\d{1,2})", s)
        if m:
            hour   = int(m.group(1))
            minute = 0

    if hour is None:
        print(f"[TimeParser] FAILED: '{original}'")
        return None

    # Apply am/pm
    if is_pm is True:
        if hour < 12:
            hour += 12
    elif is_pm is False:
        if hour == 12:
            hour = 0
    else:
        # am/pm இல்லன்னா — smart guess
        if 1 <= hour <= 6:
            hour += 12   # 1-6 → pm assume
        elif hour == 12:
            pass

    hour   = hour % 24
    minute = minute % 60

    now           = datetime.datetime.now()
    reminder_time = now.replace(
        hour=hour, minute=minute, second=0, microsecond=0
    )

    # Already passed today → tomorrow
    if reminder_time <= now:
        reminder_time += datetime.timedelta(days=1)

    print(f"[TimeParser] '{original}' → {reminder_time.strftime('%d %b %Y %I:%M %p')}")
    return reminder_time


# ─────────────────────────────────────────────────────────────
#  REMINDER — NO POPUP, DIRECT VOICE
# ─────────────────────────────────────────────────────────────
def set_reminder(reminder_text, time_str, speak_fn=None):
    """
    Time ஆனா உடனே — no popup, no click — directly voice-ல் சொல்லும்.
    3 times repeat ஆகும்.
    """
    reminder_time = _parse_time(time_str)

    if reminder_time is None:
        return (
            "Sorry, I could not understand the time. "
            "Please say something like 5 pm or 5:30 pm."
        )

    formatted = reminder_time.strftime("%I:%M %p")
    now       = datetime.datetime.now()
    delay_sec = (reminder_time - now).total_seconds()
    mins      = int(delay_sec // 60)
    secs      = int(delay_sec % 60)

    print(f"[Reminder] Scheduled: '{reminder_text}' at {formatted} "
          f"(in {mins}m {secs}s)")

    def _reminder_thread():
        # Exact time வரும்வரை wait — every 5 seconds check
        while True:
            remaining = (reminder_time - datetime.datetime.now()).total_seconds()
            if remaining <= 0:
                break
            time.sleep(min(5, remaining))

        current_time = datetime.datetime.now().strftime("%I:%M %p")
        print(f"\n[Reminder] FIRING: {reminder_text} at {current_time}")

        # Time + reminder text சேர்த்து சொல்லும்
        alert = f"Reminder! It is {current_time}. {reminder_text}"

        # ── 3 times voice — NO POPUP ──────────────────────────
        for i in range(3):
            _speak_in_thread(alert)
            if i < 2:
                time.sleep(1.5)

        # Auto complete task
        tasks = _load_tasks()
        for t in tasks:
            if reminder_text.lower() in t["text"].lower() and not t["done"]:
                t["done"]      = True
                t["completed"] = datetime.datetime.now().strftime("%d %b %Y %I:%M %p")
                _save_tasks(tasks)
                print(f"[Reminder] Auto-completed: {t['text']}")
                break

    # daemon=False → window close ஆனாலும் reminder fire ஆகும்
    t = threading.Thread(
        target=_reminder_thread,
        daemon=False,
        name=f"REM_{formatted}"
    )
    t.start()

    # Task-ஆவும் save பண்ணு
    add_task(f"[Reminder {formatted}] {reminder_text}")

    if mins > 0:
        time_left = f"in {mins} minute{'s' if mins>1 else ''}"
    else:
        time_left = f"in {secs} seconds"

    return (
        f"Reminder set for {formatted}, {time_left}. "
        f"I will tell you: {reminder_text}"
    )


# ─────────────────────────────────────────────────────────────
#  COMMAND HANDLER
# ─────────────────────────────────────────────────────────────
def handle_task_command(command, listen_fn, speak_fn):
    command = command.lower().strip()

    # ── ADD TASK ──────────────────────────────────────────────
    if any(w in command for w in [
        "add task", "new task", "create task", "add a task"
    ]):
        speak_fn("What is the task?")
        task_text = listen_fn()
        if task_text and task_text != "none":
            return add_task(task_text)
        return "No task heard. Please try again."

    # ── PENDING TASKS ─────────────────────────────────────────
    elif any(w in command for w in [
        "my tasks", "show tasks", "list tasks",
        "what are my tasks", "pending tasks",
        "what tasks", "show my tasks"
    ]):
        return get_pending_tasks()

    # ── ALL TASKS ─────────────────────────────────────────────
    elif any(w in command for w in ["all tasks", "show all tasks"]):
        return get_all_tasks()

    # ── COMPLETE TASK ─────────────────────────────────────────
    elif any(w in command for w in [
        "complete task", "done task",
        "mark task", "finish task", "task done"
    ]):
        speak_fn("Which task number is done?")
        task_id = listen_fn()
        if task_id and task_id != "none":
            return complete_task(task_id)
        return "No task number heard."

    # ── DELETE ONE TASK ───────────────────────────────────────
    elif any(w in command for w in [
        "delete task", "remove task", "cancel task"
    ]):
        speak_fn("Which task number to delete?")
        task_id = listen_fn()
        if task_id and task_id != "none":
            return delete_task(task_id)
        return "No task number heard."

    # ── CLEAR COMPLETED ───────────────────────────────────────
    elif any(w in command for w in [
        "clear completed", "clear done tasks", "remove completed"
    ]):
        return clear_completed()

    # ── DELETE ALL ────────────────────────────────────────────
    elif any(w in command for w in [
        "clear all tasks", "delete all tasks",
        "remove all tasks", "reset tasks",
        "clear all", "delete all"
    ]):
        return clear_all_tasks()

    # ── SET REMINDER ──────────────────────────────────────────
    elif any(w in command for w in [
        "remind me", "set reminder",
        "reminder at", "remind at", "alert me"
    ]):
        # "remind me at 5 pm" → time extract
        time_str = None
        for kw in ["at ", "for ", "by "]:
            if kw in command:
                time_str = command.split(kw, 1)[-1].strip()
                break

        if not time_str:
            speak_fn("At what time should I remind you?")
            time_str = listen_fn()

        if not time_str or time_str == "none":
            return "No time heard. Please try again."

        speak_fn("What should I remind you about?")
        reminder_text = listen_fn()
        # Not heard → retry once
        if not reminder_text or reminder_text == "none":
            speak_fn("Sorry, I did not catch that. What should I remind you about?")
            reminder_text = listen_fn()
        # Still not heard → use default
        if not reminder_text or reminder_text == "none":
            reminder_text = "your reminder"

        return set_reminder(reminder_text, time_str, speak_fn=speak_fn)

    return None


# ─────────────────────────────────────────────────────────────
#  TEST
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=== TIME PARSE TEST ===")
    tests = [
        "5 pm", "5:00 pm", "5:23 pm", "5:30 pm",
        "6 pm", "7:30 pm", "10 am", "10:30 am", "17:30"
    ]
    now = datetime.datetime.now()
    for t in tests:
        r = _parse_time(t)
        if r:
            diff = int((r - now).total_seconds() // 60)
            print(f"  '{t}' → {r.strftime('%I:%M %p')} (in {diff} min)")
        else:
            print(f"  '{t}' → FAILED")

    print("\n=== 15-SEC REMINDER TEST ===")
    future = datetime.datetime.now() + datetime.timedelta(seconds=15)
    t_str  = future.strftime("%I:%M %p")
    print(f"Setting reminder at {t_str}...")
    result = set_reminder("take medicine", t_str, speak_fn=None)
    print(f"Result: {result}")
    print("\nWaiting 25 seconds (window close பண்ணாதீங்க!)...")
    for i in range(25):
        print(f"\r  {25-i}s remaining...", end="", flush=True)
        time.sleep(1)
    print("\nTest done!")