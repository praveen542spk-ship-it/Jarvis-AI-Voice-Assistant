import os
from groq import Groq

# ─────────────────────────────────────────────────────────────
#  GROQ API — Loaded dynamically from local untracked file
# ─────────────────────────────────────────────────────────────
GROQ_API_KEY = ""
GROQ_KEY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "groq_key.txt")
if os.path.exists(GROQ_KEY_FILE):
    try:
        with open(GROQ_KEY_FILE, "r", encoding="utf-8") as f:
            GROQ_API_KEY = f.read().strip()
    except Exception as e:
        print(f"[Groq Key Load Error] {e}")

if not GROQ_API_KEY:
    # Fallback to default placeholder if file is empty or missing
    GROQ_API_KEY = "gsk_PLACEHOLDER_KEY"

client = Groq(api_key=GROQ_API_KEY)

# ─────────────────────────────────────────────────────────────
#  CONVERSATION MEMORY
# ─────────────────────────────────────────────────────────────
conversation_memory = []
MAX_MEMORY          = 20

SYSTEM_PROMPT = {
    "role": "system",
    "content": (
        "You are Jarvis, a smart, friendly and knowledgeable AI assistant created for Praveen. "
        "You can answer ANY question on ANY topic — science, math, history, coding, "
        "general knowledge, sports, movies, cooking, health, current events, jokes, "
        "advice, calculations, definitions, translations — everything. "
        "Always give helpful, accurate answers. "
        "Keep answers short (2-4 sentences) and clear for voice speech. "
        "No markdown formatting, no bullet points, no asterisks, no special symbols. "
        "Speak naturally like a helpful friend. "
        "You remember the full conversation context and refer back when needed. "
        "If you don't know something, say so honestly."
    )
}


def ask_chatgpt(question):
    """Send question with full memory. Returns answer string."""
    global conversation_memory

    conversation_memory.append({"role": "user", "content": question})

    if len(conversation_memory) > MAX_MEMORY:
        conversation_memory = conversation_memory[-MAX_MEMORY:]

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",   # Latest free model
            messages=[SYSTEM_PROMPT] + conversation_memory,
            max_tokens=200,
            temperature=0.7,
        )
        answer = response.choices[0].message.content.strip()
        conversation_memory.append({"role": "assistant", "content": answer})
        return answer

    except Exception as e:
        err = str(e)
        print(f"[Groq Error] {e}")
        if conversation_memory and conversation_memory[-1]["role"] == "user":
            conversation_memory.pop()
        if "401" in err or "invalid_api_key" in err.lower():
            return "Invalid API key. Please check your Groq key."
        if "429" in err or "rate_limit" in err.lower():
            return "Too many requests. Please wait a moment."
        return "Sorry, I could not reach the AI right now."


def ask_chatgpt_vision(image_path, prompt):
    """Scan active open window titles and use Llama-3.3 to provide a smart summary of what's on the screen."""
    try:
        import win32gui
        
        # 1. Get all visible window titles
        def win_cb(hwnd, lst):
            if win32gui.IsWindowVisible(hwnd):
                t = win32gui.GetWindowText(hwnd)
                if t.strip() and t not in lst:
                    # Filter non-printable unicode to prevent any string issues
                    clean_t = "".join(c for c in t if c.isprintable())
                    if clean_t.strip():
                        lst.append(clean_t.strip())
            return True
            
        windows = []
        win32gui.EnumWindows(win_cb, windows)
        
        # Keep only the top 15 visible windows to prevent context bloat
        windows_str = "\n".join([f"- {w}" for w in windows[:15]])
        
        print(f"[Screen Analysis] Found open windows:\n{windows_str}")
        
        # 2. Call Llama 3.3 Text model with this list to write a beautiful screen report
        prompt_with_context = (
            f"The user asked: '{prompt}'\n\n"
            f"Here is the list of active open windows currently visible on their Windows PC screen:\n"
            f"{windows_str}\n\n"
            f"Based on this list of open programs and window titles, write a natural-sounding response to their request. "
            f"Describe what is currently open on their screen (e.g. VS Code, browser, Notepad) and what they seem to be working on. "
            f"Keep your summary very concise, natural, and friendly (2-3 sentences max). Do not use any markdown formatting or bullet points."
        )
        
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "You are Jarvis, a smart AI assistant. You can see the user's active window titles and explain what is on their screen."
                },
                {"role": "user", "content": prompt_with_context}
            ],
            max_tokens=150,
            temperature=0.5,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"[Vision Fallback Error] {e}")
        return "Sorry, I had trouble analyzing the screen right now."


def translate_text(text, target_language):
    """Translates text to target language using Groq."""
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": f"You are a professional translator. Translate the given text to {target_language}. Return ONLY the raw translation, without any quotes, explanations, notes or extra text. Keep the translation natural and idiomatic."
                },
                {"role": "user", "content": text}
            ],
            max_tokens=200,
            temperature=0.3,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"[Groq Translation Error] {e}")
        return "Translation failed."


def route_intent_with_llm(command):
    """Uses Groq to analyze the user's voice command and decide whether to trigger a system action or respond conversationally."""
    system_instruction = (
        "You are Jarvis, a smart AI assistant on Praveen's Windows PC. "
        "The user said a command. You must determine if they want to perform an action on the computer. "
        "If they want to perform an action, respond ONLY with one of the following structured action codes: "
        "1. [ACTION: open_url] URL (to open a website like youtube, google, instagram, etc.) "
        "2. [ACTION: open_shortcut] shortcut_name (e.g. chatgpt, vscode, spotify, telegram, vlc, virtualbox, notepad, settings, edge, chess, idle) "
        "3. [ACTION: search_google] search_query (to search something on google) "
        "4. [ACTION: play_youtube] search_query (to search or play a video on youtube) "
        "5. [ACTION: play_spotify] search_query (to search or play a song on spotify) "
        "6. [ACTION: system_health] (to check CPU, RAM, battery, disk space) "
        "7. [ACTION: screen_vision] (to take a screenshot and analyze/look at the screen) "
        "8. [ACTION: translate] target_language (to start translation mode) "
        "9. [ACTION: volume] up|down|mute|unmute "
        "10. [ACTION: brightness] level (0 to 100) "
        "11. [ACTION: shutdown|restart|sleep] "
        "12. [ACTION: type_text] message (to type text into the active window) "
        "13. [ACTION: whatsapp_message] contact_name | message (to search a contact and send them a message on WhatsApp. If no message is specified, just pass contact_name) "
        "14. [ACTION: close_app] app_name (to close a specific open application or window like youtube, whatsapp, chrome, spotify, notepad, vscode, etc.) "
        "15. [ACTION: media_control] pause|play (to pause or resume any playing video or music globally) "
        "16. [ACTION: focus_mode] start|stop (to start or stop Pomodoro study mode and block distraction apps) "
        "17. [ACTION: take_note] (to capture a voice note and open it in Notepad) "
        "\n"
        "If they are NOT asking to perform a computer task, just answer their question or continue the conversation normally and friendly. "
        "Remember: Output ONLY the raw action code starting with '[ACTION:' and parameters, OR a friendly conversational answer. No markdown."
    )
    
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": command}
            ],
            max_tokens=150,
            temperature=0.3,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"[Groq Intent Router Error] {e}")
        # Fallback to standard chatgpt answer
        return ask_chatgpt(command)


def clear_memory():
    """Reset conversation history."""
    global conversation_memory
    conversation_memory = []
    print("[Memory] Cleared.")


def get_memory_count():
    """Returns number of stored messages."""
    return len(conversation_memory)


# ─────────────────────────────────────────────────────────────
#  TEST
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=== GROQ API TEST ===\n")

    print("Q: What is Python?")
    print("A:", ask_chatgpt("What is Python?"))

    print("\nQ: Give me an example")
    print("A:", ask_chatgpt("Give me an example"))

    print(f"\nMemory: {get_memory_count()} messages stored")