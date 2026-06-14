import datetime
import os
import subprocess
import wikipedia
import pyautogui
import time

from speak import speak
from listen import take_command
from news_weather import speak_news, get_weather
from tasks import handle_task_command
from developer import handle_dev_command

# ─────────────────────────────────────────────────────────────
#  SETTINGS
# ─────────────────────────────────────────────────────────────
pyautogui.FAILSAFE = False
pyautogui.PAUSE    = 0.3

# ── Desktop Shortcut Paths ────────────────────────────────────
SHORTCUTS = {
    "youtube":         r"C:\Users\prave\OneDrive\Desktop\YouTube.lnk",
    "whatsapp":        r"C:\Users\prave\OneDrive\Desktop\WhatsApp.lnk",
    "instagram":       r"C:\Users\prave\OneDrive\Desktop\instagram.lnk",
    "vscode":          r"C:\Users\prave\OneDrive\Desktop\Visual Studio Code.lnk",
    "claude":          r"C:\Users\prave\OneDrive\Desktop\Claude (2).lnk",
    "chatgpt":         r"C:\Users\prave\OneDrive\Desktop\ChatGPT.lnk",
    "spotify":         r"C:\Users\prave\OneDrive\Desktop\Spotify.lnk",
    "antigravity":     r"C:\Users\prave\OneDrive\Desktop\Antigravity.lnk",
    "brave":           r"C:\Users\prave\OneDrive\Desktop\Brave.lnk",
    "firefox":         r"C:\Users\prave\OneDrive\Desktop\Firefox.lnk",
    "chrome_college":  r"C:\Users\prave\OneDrive\Desktop\PRAVEEN KUMAR S - Chrome.lnk",
    "chrome_personal": r"C:\Users\Public\Desktop\Google Chrome.lnk",
    "codetantra":      r"C:\Users\prave\OneDrive\Desktop\CodeTantra SEA.lnk",
    "github_desktop":  r"C:\Users\prave\OneDrive\Desktop\GitHub.lnk",
    "telegram":        r"C:\Users\prave\OneDrive\Desktop\Telegram.lnk",
    "myasus":          r"C:\Users\prave\OneDrive\Desktop\MyASUS.lnk",
    # ── New apps added from user screenshot ─────────────────────
    "edge":            r"C:\Users\prave\OneDrive\Desktop\Personal - Edge.lnk",
    "vlc":             r"C:\Users\prave\OneDrive\Desktop\VLC media player.lnk",
    "virtualbox":      r"C:\Users\prave\OneDrive\Desktop\Oracle VirtualBox.lnk",
    "chess":           r"C:\Users\prave\OneDrive\Desktop\Chess - Play & Learn.lnk",
    "idle":            r"C:\Users\prave\OneDrive\Desktop\IDLE (Python 3.14 64-bit).lnk",
    "settings":        r"C:\Users\prave\OneDrive\Desktop\Settings.lnk",
    "notepad":         r"C:\Users\prave\OneDrive\Desktop\Notepad.lnk",
}

# ── Web Browser Fallback URLs ─────────────────────────────────
URL_FALLBACKS = {
    "youtube":        "https://www.youtube.com",
    "whatsapp":       "https://web.whatsapp.com",
    "instagram":      "https://www.instagram.com",
    "claude":         "https://claude.ai",
    "chatgpt":        "https://chatgpt.com",
    "spotify":        "https://open.spotify.com",
    "brave":          "https://search.brave.com",
    "firefox":        "https://google.com",
    "chrome_college": "https://google.com",
    "chrome_personal":"https://google.com",
    "codetantra":     "https://codetantra.com",
    "telegram":       "https://web.telegram.org",
    "myasus":         "https://www.asus.com",
    "edge":           "https://google.com",
    "chess":          "https://www.chess.com",
}

# ── Browser exe paths ─────────────────────────────────────────
CHROME_PATH  = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
FIREFOX_PATH = r"C:\Program Files\Mozilla Firefox\firefox.exe"
BRAVE_PATH   = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"

# ─────────────────────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────────────────────
def _open_shortcut(key):
    path = SHORTCUTS.get(key, "")
    if path and os.path.exists(path):
        try:
            os.startfile(path)
            return True
        except Exception as e:
            print(f"[Shortcut error] {path}: {e}")
            
    # Web URL fallback
    url = URL_FALLBACKS.get(key)
    if url:
        print(f"[Shortcut not found or failed] {path} - Falling back to URL: {url}")
        _open_browser("chrome", url)
        return True
        
    print(f"[Shortcut fallback not found] {path}")
    return False


def _open_telegram():
    path = SHORTCUTS.get("telegram", "")
    if os.path.exists(path):
        try:
            os.startfile(path)
            return True
        except Exception:
            pass
            
    # AppData local installation check
    appdata_path = os.path.expandvars(r"%APPDATA%\Telegram Desktop\Telegram.exe")
    if os.path.exists(appdata_path):
        try:
            subprocess.Popen([appdata_path])
            return True
        except Exception:
            pass
            
    # Web fallback
    print("[Telegram app not found or failed] - Falling back to Web")
    _open_browser("chrome", "https://web.telegram.org")
    return True


def _open_browser(browser, url):
    try:
        import webbrowser
        webbrowser.open_new_tab(url)
    except Exception:
        exe_map = {
            "chrome":  CHROME_PATH,
            "firefox": FIREFOX_PATH,
            "brave":   BRAVE_PATH,
        }
        exe = exe_map.get(browser, CHROME_PATH)
        if os.path.exists(exe):
            subprocess.Popen([exe, url])
        else:
            os.system(f'start chrome "{url}"')


def _open_chrome_profile(profile_dir):
    """Launch Chrome directly with the target profile, bypassing the profile chooser."""
    if os.path.exists(CHROME_PATH):
        subprocess.Popen([CHROME_PATH, f"--profile-directory={profile_dir}"])
    else:
        os.system(f'start chrome --profile-directory="{profile_dir}"')


def _search_in_chrome_profile(profile_dir, query):
    """Launch Chrome directly with target profile and open a Google search query in a new tab."""
    url = f"https://www.google.com/search?q={_encode(query)}"
    if os.path.exists(CHROME_PATH):
        subprocess.Popen([CHROME_PATH, f"--profile-directory={profile_dir}", url])
    else:
        os.system(f'start chrome --profile-directory="{profile_dir}" "{url}"')


def _encode(text):
    return text.strip().replace(" ", "+")


def _listen_with_retry(prompt, retries=2):
    for attempt in range(retries):
        speak(prompt)
        result = take_command()
        if result and result != "none":
            return result
        if attempt < retries - 1:
            speak("Sorry, I did not catch that. Please say it again.")
    return "none"


def _run_cmd(cmd):
    try:
        import subprocess
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except Exception as e:
        return "", str(e), 1


def _set_brightness(level):
    try:
        import wmi
        c = wmi.WMI(namespace="wmi")
        c.WmiMonitorBrightnessMethods()[0].WmiSetBrightness(level, 0)
        return True
    except Exception:
        try:
            script = f"(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1,{level})"
            subprocess.run(["powershell", "-Command", script], capture_output=True)
            return True
        except Exception as e:
            print(f"[Brightness Error] {e}")
            return False


def _get_brightness():
    try:
        import wmi
        c = wmi.WMI(namespace="wmi")
        return c.WmiMonitorBrightness()[0].CurrentBrightness
    except Exception:
        try:
            result = subprocess.run(
                ["powershell", "-Command",
                 "(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightness).CurrentBrightness"],
                capture_output=True, text=True)
            return int(result.stdout.strip())
        except Exception:
            return 50


def _close_existing_app_windows(keyword, force=False):
    """Scan and close any active visible window that contains the keyword in its title."""
    try:
        import win32gui
        import time
        
        def win_cb(hwnd, extra):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd).lower()
                
                # Safety checks to prevent closing development IDEs, terminals, browsers, or Jarvis itself
                protected = ["visual studio code", "vscode", "jarvis", "antigravity", "cmd.exe", "powershell", "terminal", "program manager"]
                if not force and any(p in title for p in protected):
                    return True
                    
                if keyword.lower() in title:
                    print(f"[Cleanup] Closing existing window matching '{keyword}': {win32gui.GetWindowText(hwnd)}")
                    # Send WM_CLOSE (0x0010) signal to close the window gracefully (like clicking X)
                    win32gui.PostMessage(hwnd, 0x0010, 0, 0)
            return True
            
        win32gui.EnumWindows(win_cb, None)
        time.sleep(0.3)  # Short delay to allow graceful close
    except Exception as e:
        print(f"[Cleanup Error] {e}")


def _find_whatsapp_window():
    """Scan all visible windows to find the WhatsApp window, even if it has an unread badge like '(3) WhatsApp'."""
    import win32gui
    hwnds = []
    
    def win_cb(hwnd, extra):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if "WhatsApp" in title:
                hwnds.append(hwnd)
        return True
        
    win32gui.EnumWindows(win_cb, None)
    return hwnds[0] if hwnds else None


def _send_whatsapp_message(contact, message=None):
    """Automate focusing/launching WhatsApp, searching for the contact, opening their chat, and optionally sending a message."""
    import win32gui
    import win32con
    import win32com.client
    import pyautogui
    import time
    
    speak(f"Opening WhatsApp chat for {contact}")
    
    # 1. Open/Focus WhatsApp
    hwnd = _find_whatsapp_window()
    if not hwnd:
        # Try launching it via shortcut
        _open_shortcut("whatsapp")
        time.sleep(3.5)  # Wait for launch
        hwnd = _find_whatsapp_window()
        
    if hwnd:
        try:
            # Restore window if minimized
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            time.sleep(0.2)
            
            # WScript.Shell Alt-key trick to bypass Windows focus restrictions and force window to foreground
            shell = win32com.client.Dispatch("WScript.Shell")
            shell.SendKeys('%')  # Send Alt key
            time.sleep(0.1)
            
            win32gui.SetForegroundWindow(hwnd)
        except Exception as e:
            print(f"[Focus Error] {e}")
            try:
                win32gui.SetForegroundWindow(hwnd)
            except Exception:
                pass
        time.sleep(0.8)
    else:
        speak("Sorry, WhatsApp is not running and I could not launch it.")
        return False

    # 2. Focus and activate search
    # Press Ctrl + F to search (standard keyboard method)
    pyautogui.hotkey('ctrl', 'f')
    time.sleep(0.3)
    
    # Backup mouse click on the search input box (about 180px from left, 135px from top of WhatsApp window)
    try:
        rect = win32gui.GetWindowRect(hwnd)
        left, top, right, bottom = rect
        click_x = left + 180
        click_y = top + 135
        pyautogui.click(click_x, click_y)
        time.sleep(0.2)
    except Exception as e:
        print(f"[WhatsApp Search Focus Error] {e}")
    
    # Clear any previous text
    pyautogui.press('backspace', presses=25, interval=0.01)
    
    # Type contact name
    pyautogui.write(contact, interval=0.04)
    time.sleep(1.2)  # Wait for search filter to populate
    
    # Select first contact and enter chat
    pyautogui.press('enter')
    time.sleep(0.8)
    
    # Click message input box to focus cursor inside WhatsApp Desktop (UWP)
    try:
        rect = win32gui.GetWindowRect(hwnd)
        left, top, right, bottom = rect
        width = right - left
        
        # Click position: ~60% window width, 45 pixels above the window bottom
        click_x = left + int(width * 0.6)
        click_y = bottom - 45
        
        pyautogui.click(click_x, click_y)
        time.sleep(0.3)
    except Exception as e:
        print(f"[WhatsApp Message Focus Error] {e}")
    
    # 3. Type and send message if provided
    if message:
        speak(f"Sending message to {contact}")
        pyautogui.write(message, interval=0.04)
        time.sleep(0.2)
        pyautogui.press('enter')
        speak(f"Message successfully sent to {contact} on WhatsApp!")
    else:
        speak(f"WhatsApp chat for {contact} is now open and ready.")
        
    return True


# ── Pomodoro Focus Mode & Distraction Blocker ──────────────────
focus_active = False
focus_thread = None

def _focus_blocker_loop(duration_mins):
    global focus_active
    start_time = time.time()
    duration_secs = duration_mins * 60
    distractions = ["whatsapp", "instagram", "telegram", "discord", "netflix", "facebook"]
    
    # Initial block
    for d in distractions:
        _close_existing_app_windows(d)
        
    while focus_active and (time.time() - start_time < duration_secs):
        elapsed = time.time() - start_time
        remaining_mins = max(1, int((duration_secs - elapsed) / 60))
        
        # Safe UI status update
        try:
            from jarvis_ui import set_status
            set_status("THINKING", f"FOCUS MODE — {remaining_mins} mins left")
        except Exception:
            pass
            
        # Periodic block scan (every 15 seconds)
        for d in distractions:
            _close_existing_app_windows(d)
            
        # Check every 1 second to react quickly to cancel
        for _ in range(15):
            if not focus_active:
                break
            time.sleep(1)
            
    if focus_active:
        focus_active = False
        speak("Praveen, your focus session is complete! Outstanding job! Take a well-deserved 5-minute break now.")
        try:
            from jarvis_ui import set_status
            set_status("IDLE", "Focus session complete!")
        except Exception:
            pass


# ─────────────────────────────────────────────────────────────
#  EXECUTE COMMAND
# ─────────────────────────────────────────────────────────────
def execute_command(command):
    command = command.lower().strip()

    # Smart Phonetic Mishearing Corrections for common voice recognizer slips
    corrections = {
        "open 4g": "open chatgpt",
        "open 4 g": "open chatgpt",
        "open four g": "open chatgpt",
        "open chat 4g": "open chatgpt",
        "open chat 4 g": "open chatgpt",
        "open chat four g": "open chatgpt",
        "chat 4g": "open chatgpt",
        "chat 4 g": "open chatgpt",
        "chat four g": "open chatgpt",
        "four g": "chatgpt",
        "4 g": "chatgpt",
        "4g": "chatgpt",
        "class room": "classroom",
        "google class room": "google classroom",
        "code tantra": "codetantra",
    }
    for misheard, correct in corrections.items():
        if misheard in command:
            command = command.replace(misheard, correct)


    # ══════════════════════════════════════════════════════════
    #  CHROME — COLLEGE ACCOUNT
    #  Keywords: "college chrome" | "college account" | "open college"
    # ══════════════════════════════════════════════════════════
    if any(w in command for w in [
        "college chrome", "college account", "college browser",
        "open college", "praveen kumar chrome", "rmd chrome",
        "my college", "college profile"
    ]):
        # Extract search query if present
        query = ""
        for prefix in ["search ", "open ", "find ", "look up "]:
            if command.startswith(prefix):
                query = command.replace(prefix, "")
                break
        
        # Clean query by removing college chrome keywords
        for keyword in ["in college chrome", "on college chrome", "college chrome", "college profile", "rmd chrome"]:
            query = query.replace(keyword, "")
        query = query.strip()
        
        if query:
            speak(f"Searching {query} on College Chrome")
            _search_in_chrome_profile("Default", query)
        else:
            _open_chrome_profile("Default")
            speak("Opening college Chrome account")

    # ══════════════════════════════════════════════════════════
    #  CHROME — PERSONAL ACCOUNT
    #  Keywords: "personal chrome" | "personal account" | "my chrome"
    # ══════════════════════════════════════════════════════════
    elif any(w in command for w in [
        "personal chrome", "personal account", "personal browser",
        "my chrome", "my account", "open personal",
        "google chrome personal", "personal profile"
    ]):
        # Extract search query if present
        query = ""
        for prefix in ["search ", "open ", "find ", "look up "]:
            if command.startswith(prefix):
                query = command.replace(prefix, "")
                break
                
        # Clean query by removing personal chrome keywords
        for keyword in ["in personal chrome", "on personal chrome", "personal chrome", "personal profile", "my chrome", "personal browser"]:
            query = query.replace(keyword, "")
        query = query.strip()
        
        if query:
            speak(f"Searching {query} on Personal Chrome")
            _search_in_chrome_profile("Profile 5", query)
        else:
            _open_chrome_profile("Profile 5")
            speak("Opening personal Chrome account")

    # ══════════════════════════════════════════════════════════
    #  CHROME — Generic (personal account default)
    # ══════════════════════════════════════════════════════════
    elif "chrome" in command:
        speak("Which account? Say college or personal.")
        choice = take_command()
        if choice and "college" in choice:
            _open_chrome_profile("Default")
            speak("Opening college Chrome account")
        else:
            _open_chrome_profile("Profile 5")
            speak("Opening personal Chrome account")

    # ══════════════════════════════════════════════════════════
    #  YOUTUBE (Instant Search & Smart Match)
    # ══════════════════════════════════════════════════════════
    elif "youtube" in command:
        query = ""
        for prefix in ["search ", "play ", "open ", "find "]:
            if command.startswith(prefix):
                query = command.replace(prefix, "")
                break
        if "on youtube" in query:
            query = query.replace("on youtube", "")
        elif "in youtube" in query:
            query = query.replace("in youtube", "")
        
        if not query.strip() or query.strip() == "youtube":
            temp = command.replace("youtube", "").strip()
            if temp:
                query = temp
                
        query = query.strip()
        
        # Open in stand-alone app window (Brave/Chrome App/PWA mode) so it looks like a desktop app!
        if query:
            speak(f"Searching {query} on YouTube")
            url = f"https://www.youtube.com/results?search_query={_encode(query)}"
            _close_existing_app_windows("youtube")  # Close any previously open YouTube standalone app windows
            if os.path.exists(BRAVE_PATH):
                subprocess.Popen([BRAVE_PATH, f"--app={url}"])
            elif os.path.exists(CHROME_PATH):
                subprocess.Popen([CHROME_PATH, f"--app={url}"])
            else:
                _open_browser("chrome", url)
        else:
            _open_shortcut("youtube")
            speak("Opening YouTube desktop app")

    # ══════════════════════════════════════════════════════════
    #  WHATSAPP (Message Automation & Contact Search)
    # ══════════════════════════════════════════════════════════
    elif any(w in command for w in ["whatsapp message", "send message to", "send whatsapp", "message on whatsapp", "message to"]):
        # Extract contact and message
        # Example: "send message to praveen on whatsapp"
        contact = ""
        msg = ""
        
        # Parse contact
        words = command.split()
        try:
            if "to" in words:
                idx = words.index("to")
                if idx + 1 < len(words):
                    contact = words[idx + 1]
            elif "message" in words:
                idx = words.index("message")
                if idx + 1 < len(words) and words[idx+1] != "on" and words[idx+1] != "to":
                    contact = words[idx + 1]
        except Exception:
            pass
            
        # Clean contact name
        contact = contact.replace("on", "").replace("whatsapp", "").strip().title()
        
        if not contact:
            # Ask for contact
            contact = _listen_with_retry("Who should I message on WhatsApp?")
            contact = contact.strip().title()
            
        if contact and contact != "None":
            # Ask for the message content
            msg = _listen_with_retry(f"What is the message for {contact}?")
            if msg and msg != "none":
                _send_whatsapp_message(contact, msg)
            else:
                speak("Message cancelled.")
        else:
            speak("Contact name not understood.")

    elif "whatsapp" in command:
        # Check if they want to chat with a specific contact
        # Example: "whatsapp praveen" or "open whatsapp chat for mom"
        query = command.replace("open whatsapp chat for", "").replace("open whatsapp chat to", "").replace("whatsapp", "").strip()
        query = query.replace("chat for", "").replace("chat to", "").strip().title()
        
        if query:
            _send_whatsapp_message(query)
        else:
            _open_shortcut("whatsapp")
            speak("Opening WhatsApp")

    # ══════════════════════════════════════════════════════════
    #  SPOTIFY (Instant Play & Smart Match)
    # ══════════════════════════════════════════════════════════
    elif "spotify" in command:
        query = ""
        for prefix in ["search ", "play ", "open ", "listen to "]:
            if command.startswith(prefix):
                query = command.replace(prefix, "")
                break
        if "on spotify" in query:
            query = query.replace("on spotify", "")
        elif "in spotify" in query:
            query = query.replace("in spotify", "")
            
        if not query.strip() or query.strip() == "spotify":
            temp = command.replace("spotify", "").strip()
            if temp:
                query = temp
                
        query = query.strip()
        
        if query:
            speak(f"Searching {query} on Spotify")
            url = f"https://open.spotify.com/search/{_encode(query)}"
            _close_existing_app_windows("spotify")  # Close any previously open Spotify standalone app windows
            if os.path.exists(BRAVE_PATH):
                subprocess.Popen([BRAVE_PATH, f"--app={url}"])
            elif os.path.exists(CHROME_PATH):
                subprocess.Popen([CHROME_PATH, f"--app={url}"])
            else:
                _open_browser("chrome", url)
        else:
            _open_shortcut("spotify")
            speak("Opening Spotify")

    # ══════════════════════════════════════════════════════════
    #  INSTAGRAM
    # ══════════════════════════════════════════════════════════
    elif "instagram" in command:
        _open_shortcut("instagram")
        speak("Opening Instagram from desktop")

    # ══════════════════════════════════════════════════════════
    #  CLAUDE AI
    # ══════════════════════════════════════════════════════════
    elif "claude" in command:
        _open_shortcut("claude")
        speak("Opening Claude AI from desktop")

    # ══════════════════════════════════════════════════════════
    #  CHATGPT (Fixes "chat gpt" space matching)
    # ══════════════════════════════════════════════════════════
    elif any(w in command for w in ["chatgpt", "chat gpt", "gpt"]):
        _open_shortcut("chatgpt")
        speak("Opening ChatGPT")

    # ══════════════════════════════════════════════════════════
    #  VS CODE
    # ══════════════════════════════════════════════════════════
    elif any(w in command for w in ["vs code", "vscode", "visual studio"]):
        _open_shortcut("vscode")
        speak("Opening VS Code from desktop")

    # ══════════════════════════════════════════════════════════
    #  CODETANTRA
    # ══════════════════════════════════════════════════════════
    elif any(w in command for w in ["codetantra", "code tantra", "sea", "coding platform"]):
        _open_shortcut("codetantra")
        speak("Opening CodeTantra SEA from desktop")

    # ══════════════════════════════════════════════════════════
    #  GITHUB DESKTOP (Fixed path to 'GitHub.lnk')
    # ══════════════════════════════════════════════════════════
    elif any(w in command for w in ["github desktop", "github", "git hub", "git desktop"]):
        _open_shortcut("github_desktop")
        speak("Opening GitHub from desktop")

    # ══════════════════════════════════════════════════════════
    #  TELEGRAM (Added smart Local/Web fallback)
    # ══════════════════════════════════════════════════════════
    elif "telegram" in command:
        speak("Opening Telegram")
        _open_telegram()

    # ══════════════════════════════════════════════════════════
    #  MYASUS
    # ══════════════════════════════════════════════════════════
    elif any(w in command for w in ["myasus", "my asus", "asus app", "asus settings", "asus"]):
        _open_shortcut("myasus")
        speak("Opening MyASUS from desktop")

    # ══════════════════════════════════════════════════════════
    #  CAMERA
    # ══════════════════════════════════════════════════════════
    elif "camera" in command:
        os.system("start microsoft.windows.camera:")
        speak("Opening Camera")

    # ══════════════════════════════════════════════════════════
    #  ANTIGRAVITY
    # ══════════════════════════════════════════════════════════
    elif "antigravity" in command or "anti gravity" in command:
        _open_shortcut("antigravity")
        speak("Launching AntiGravity from desktop")

    # ══════════════════════════════════════════════════════════
    #  FIREFOX (Updated path to OneDrive Desktop)
    # ══════════════════════════════════════════════════════════
    elif "firefox" in command:
        _open_shortcut("firefox")
        speak("Opening Firefox from desktop")

    # ══════════════════════════════════════════════════════════
    #  BRAVE (Updated path to OneDrive Desktop)
    # ══════════════════════════════════════════════════════════
    elif "brave" in command:
        _open_shortcut("brave")
        speak("Opening Brave from desktop")

    # ══════════════════════════════════════════════════════════
    #  MICROSOFT EDGE (Updated path)
    # ══════════════════════════════════════════════════════════
    elif "edge" in command or "microsoft edge" in command:
        _open_shortcut("edge")
        speak("Opening Microsoft Edge from desktop")

    # ══════════════════════════════════════════════════════════
    #  NEW APPS FROM USER SCREENSHOT
    # ══════════════════════════════════════════════════════════
    elif "vlc" in command or "media player" in command:
        _open_shortcut("vlc")
        speak("Opening VLC media player")

    elif "virtualbox" in command or "virtual box" in command:
        _open_shortcut("virtualbox")
        speak("Opening Oracle VirtualBox")

    elif "chess" in command:
        _open_shortcut("chess")
        speak("Opening Chess Play and Learn")

    elif "idle" in command or "python idle" in command:
        _open_shortcut("idle")
        speak("Opening Python IDLE")

    # ══════════════════════════════════════════════════════════
    #  UNIVERSAL APP CLOSER
    # ══════════════════════════════════════════════════════════
    elif command.startswith("close ") or command.startswith("close the "):
        app_name = command.replace("close the ", "").replace("close ", "").replace("app", "").replace("window", "").strip()
        
        # Smart mappings
        mapping = {
            "vscode": "visual studio code",
            "vs code": "visual studio code",
            "chrome college": "chrome",
            "chrome personal": "chrome",
            "college chrome": "chrome",
            "personal chrome": "chrome",
        }
        keyword = mapping.get(app_name, app_name)
        
        if keyword:
            speak(f"Closing {app_name}")
            # If the user explicitly asks to close VS Code/Jarvis/Antigravity, we pass force=True to bypass safety guard!
            _close_existing_app_windows(keyword, force=True)

    # ══════════════════════════════════════════════════════════
    #  GLOBAL VOICE MEDIA CONTROLS
    # ══════════════════════════════════════════════════════════
    elif command.strip() in ["pause", "pause the video", "pause the song", "pause music", "stop music", "stop video"]:
        pyautogui.press("playpause")
        speak("Paused")
        
    elif command.strip() in ["play", "continue", "carry on", "unpause", "go on", "resume", "play the video", "play the song", "resume music", "continue music"]:
        pyautogui.press("playpause")
        speak("Playing")

    # ══════════════════════════════════════════════════════════
    #  POMODORO FOCUS MODE & DISTRACTION BLOCKER
    # ══════════════════════════════════════════════════════════
    elif any(w in command for w in ["stop focus", "cancel focus", "cancel study", "stop study"]):
        global focus_active
        if focus_active:
            focus_active = False
            speak("Focus mode cancelled. Normal mode restored.")
        else:
            speak("Focus mode is not currently running.")
            
    elif any(w in command for w in ["focus mode", "study mode", "pomodoro", "start focus", "start study"]):
        import threading
        if focus_active:
            speak("Focus mode is already running.")
        else:
            speak("Focus mode activated for 25 minutes. All distractions are blocked. Let's focus, Praveen!")
            focus_active = True
            focus_thread = threading.Thread(target=_focus_blocker_loop, args=(25,), daemon=True)
            focus_thread.start()

    # ══════════════════════════════════════════════════════════
    #  VOICE NOTE MAKER & AUTO-OPENER
    # ══════════════════════════════════════════════════════════
    elif any(w in command for w in ["take a note", "create a note", "write note"]):
        topic = ""
        for prefix in ["take a note about ", "create a note about ", "write note about "]:
            if prefix in command:
                topic = command.split(prefix)[-1].strip().title()
                break
                
        content = _listen_with_retry("What is the content of the note?")
        if content and content != "none":
            try:
                # Create notes folder in Jarvis directory
                notes_dir = os.path.join(r"C:\Users\prave\OneDrive\Desktop\Jarvis", "notes")
                os.makedirs(notes_dir, exist_ok=True)
                
                # File name with date and time
                now = datetime.datetime.now()
                filename = f"note_{now.strftime('%Y%m%d_%H%M%S')}.md"
                note_path = os.path.join(notes_dir, filename)
                
                # Write formatted Markdown
                with open(note_path, "w", encoding="utf-8") as f:
                    f.write("# Jarvis Voice Note\n")
                    f.write(f"- **Date**: {now.strftime('%A, %d %B %Y, %I:%M %p')}\n")
                    if topic:
                        f.write(f"- **Topic**: {topic}\n")
                    f.write(f"- **Content**: {content}\n")
                    
                speak("Saving note and opening it.")
                os.startfile(note_path)
            except Exception as e:
                print(f"[Note Error] {e}")
                speak("Sorry, I had trouble saving the note.")
        else:
            speak("Note cancelled.")

    # ══════════════════════════════════════════════════════════
    #  GOOGLE SEARCH
    # ══════════════════════════════════════════════════════════
    elif "search" in command or "google" in command:
        query = _listen_with_retry("What should I search on Google?")
        if query != "none":
            _open_browser("chrome",
                f"https://www.google.com/search?q={_encode(query)}")
            speak(f"Searching {query} on Google")

    # ══════════════════════════════════════════════════════════
    #  TYPE MESSAGE
    # ══════════════════════════════════════════════════════════
    elif any(command.startswith(prefix) for prefix in ["type ", "write ", "send "]):
        # Extract what to type
        text_to_type = ""
        for prefix in ["type ", "write ", "send "]:
            if command.startswith(prefix):
                text_to_type = command[len(prefix):].strip()
                break
        
        # Clean up trailing 'and send' or 'send' if spoken at the end
        if text_to_type.endswith(" and send"):
            text_to_type = text_to_type[:-9].strip()
        elif text_to_type.endswith(" send"):
            text_to_type = text_to_type[:-5].strip()
            
        if text_to_type:
            speak(f"Typing {text_to_type}")
            pyautogui.write(text_to_type, interval=0.04)
            pyautogui.press("enter")
            speak("Done, sent!")
        else:
            msg = _listen_with_retry("Tell me what to type")
            if msg != "none":
                pyautogui.write(msg, interval=0.06)
                pyautogui.press("enter")
                speak("Done, message typed")

    elif command.strip() in ["type", "write", "send", "type message", "send message"]:
        msg = _listen_with_retry("Tell me what to type")
        if msg != "none":
            pyautogui.write(msg, interval=0.06)
            pyautogui.press("enter")
            speak("Done, message typed")

    # ══════════════════════════════════════════════════════════
    #  TIME
    # ══════════════════════════════════════════════════════════
    elif any(w in command for w in ["time", "current time", "what time"]):
        t = datetime.datetime.now().strftime("%I:%M %p")
        speak(f"The current time is {t}")

    # ══════════════════════════════════════════════════════════
    #  DATE
    # ══════════════════════════════════════════════════════════
    elif any(w in command for w in ["date", "today's date", "what date", "today"]):
        d = datetime.datetime.now().strftime("%A, %d %B %Y")
        speak(f"Today is {d}")

    # ══════════════════════════════════════════════════════════
    #  WIKIPEDIA
    # ══════════════════════════════════════════════════════════
    elif "who is" in command or "what is" in command:
        try:
            q = command.replace("who is", "").replace("what is", "").strip()
            result = wikipedia.summary(q, sentences=2)
            speak(result)
        except wikipedia.exceptions.DisambiguationError:
            speak("There are multiple results. Please be more specific.")
        except wikipedia.exceptions.PageError:
            speak("Sorry, I could not find that on Wikipedia.")
        except Exception as e:
            print(f"[Wiki Error] {e}")
            speak("Sorry, I had trouble with Wikipedia.")

    # ══════════════════════════════════════════════════════════
    #  BRIGHTNESS UP
    # ══════════════════════════════════════════════════════════
    elif "brightness up" in command or "increase brightness" in command:
        current = _get_brightness()
        new_level = min(100, current + 20)
        if _set_brightness(new_level):
            speak(f"Brightness increased to {new_level} percent")
        else:
            speak("Sorry, I could not change the brightness")

    # ══════════════════════════════════════════════════════════
    #  BRIGHTNESS DOWN
    # ══════════════════════════════════════════════════════════
    elif "brightness down" in command or "decrease brightness" in command or "reduce brightness" in command:
        current = _get_brightness()
        new_level = max(0, current - 20)
        if _set_brightness(new_level):
            speak(f"Brightness decreased to {new_level} percent")
        else:
            speak("Sorry, I could not change the brightness")

    # ══════════════════════════════════════════════════════════
    #  SET BRIGHTNESS TO VALUE
    # ══════════════════════════════════════════════════════════
    elif "set brightness" in command:
        words = command.split()
        number = next((int(w) for w in words if w.isdigit()), None)
        if number is not None:
            level = max(0, min(100, number))
            if _set_brightness(level):
                speak(f"Brightness set to {level} percent")
            else:
                speak("Sorry, I could not set the brightness")
        else:
            speak("Please say a number. For example, set brightness to 50")

    # ══════════════════════════════════════════════════════════
    #  WINDOWS START MENU
    # ══════════════════════════════════════════════════════════
    elif "start menu" in command or "win key" in command:
        pyautogui.press("win")
        speak("Opening Windows Start menu")

    # ══════════════════════════════════════════════════════════
    #  CONTROL PANEL
    # ══════════════════════════════════════════════════════════
    elif "control panel" in command:
        os.system("control")
        speak("Opening Control Panel")

    # ══════════════════════════════════════════════════════════
    #  WINDOWS SETTINGS
    # ══════════════════════════════════════════════════════════
    elif "settings" in command or "windows settings" in command:
        os.system("start ms-settings:")
        speak("Opening Windows Settings")

    # ══════════════════════════════════════════════════════════
    #  MICROSOFT STORE
    # ══════════════════════════════════════════════════════════
    elif "microsoft store" in command or "ms store" in command or "store" in command:
        os.system("start ms-windows-store:")
        speak("Opening Microsoft Store")

    # ══════════════════════════════════════════════════════════
    #  POWERPOINT
    # ══════════════════════════════════════════════════════════
    elif "powerpoint" in command or "power point" in command or "presentation" in command:
        os.system("start powerpnt")
        speak("Opening Microsoft PowerPoint")

    # ══════════════════════════════════════════════════════════
    #  OTHER DESKTOP APPS
    # ══════════════════════════════════════════════════════════
    elif "notepad" in command:
        os.system("notepad")
        speak("Opening Notepad")

    elif "calculator" in command:
        os.system("calc")
        speak("Opening Calculator")

    elif "file explorer" in command or "explorer" in command:
        os.system("explorer")
        speak("Opening File Explorer")

    elif "task manager" in command:
        os.system("taskmgr")
        speak("Opening Task Manager")

    elif "paint" in command:
        os.system("mspaint")
        speak("Opening Paint")

    elif "word" in command:
        os.system("start winword")
        speak("Opening Microsoft Word")

    elif "excel" in command:
        os.system("start excel")
        speak("Opening Microsoft Excel")

    # ══════════════════════════════════════════════════════════
    #  FOLDERS
    # ══════════════════════════════════════════════════════════
    elif "open desktop" in command:
        os.startfile(r"C:\Users\prave\OneDrive\Desktop")
        speak("Opening Desktop folder")

    elif "open downloads" in command:
        os.startfile(r"C:\Users\prave\OneDrive\Downloads")
        speak("Opening Downloads folder")

    elif "open jarvis" in command:
        os.startfile(r"C:\Users\prave\OneDrive\Desktop\Jarvis")
        speak("Opening Jarvis folder")

    # ══════════════════════════════════════════════════════════
    #  VOLUME
    # ══════════════════════════════════════════════════════════
    elif "volume up" in command:
        for _ in range(5): pyautogui.press("volumeup")
        speak("Volume increased")

    elif "volume down" in command:
        for _ in range(5): pyautogui.press("volumedown")
        speak("Volume decreased")

    elif "unmute" in command:
        pyautogui.press("volumemute")
        speak("Unmuted")

    elif "mute" in command:
        pyautogui.press("volumemute")
        speak("Muted")

    # ══════════════════════════════════════════════════════════
    #  SCREENSHOT
    # ══════════════════════════════════════════════════════════
    elif "screenshot" in command:
        img  = pyautogui.screenshot()
        ts   = datetime.datetime.now().strftime("%H%M%S")
        path = rf"C:\Users\prave\OneDrive\Desktop\screenshot_{ts}.png"
        img.save(path)
        speak("Screenshot saved to desktop")

    # ══════════════════════════════════════════════════════════
    #  SYSTEM POWER
    # ══════════════════════════════════════════════════════════
    elif "shutdown" in command:
        speak("Shutting down in 5 seconds. Goodbye!")
        time.sleep(5)
        os.system("shutdown /s /t 1")

    elif "restart" in command:
        speak("Restarting in 5 seconds!")
        time.sleep(5)
        os.system("shutdown /r /t 1")

    elif "sleep" in command or "hibernate" in command:
        speak("Putting the computer to sleep")
        os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")

    elif "lock" in command:
        speak("Locking the computer")
        os.system("rundll32.exe user32.dll,LockWorkStation")

    # ══════════════════════════════════════════════════════════
    #  EXIT
    # ══════════════════════════════════════════════════════════
    elif command.strip() in [
        "exit", "stop", "quit", "bye", "goodbye", "bye bye", "see you",
        "stop jarvis", "exit jarvis", "quit jarvis", "close jarvis",
        "go to sleep jarvis", "shutdown jarvis", "turn off jarvis", "bye jarvis"
    ]:
        speak("Goodbye Praveen! Have a great day.")
        return "exit"

    # ══════════════════════════════════════════════════════════
    #  NEWS
    # ══════════════════════════════════════════════════════════
    elif any(w in command for w in ["news", "headlines", "what's happening", "latest news"]):
        # Category detect பண்ணு
        if "tech" in command or "technology" in command:
            category = "technology"
        elif "sport" in command or "cricket" in command or "football" in command:
            category = "sports"
        elif "business" in command or "economy" in command or "market" in command:
            category = "business"
        elif "health" in command or "medical" in command:
            category = "health"
        elif "science" in command:
            category = "science"
        else:
            category = "general"

        speak("Fetching the latest news, please wait.")
        try:
            news_text = speak_news(category=category)
            speak(news_text)
        except Exception as e:
            print(f"[News Error] {e}")
            speak("Sorry, I could not fetch news right now.")

    # ══════════════════════════════════════════════════════════
    #  WEATHER
    # ══════════════════════════════════════════════════════════
    elif any(w in command for w in ["weather", "temperature", "how hot", "how cold", "climate"]):
        # City name detect பண்ணு — "weather in Mumbai" மாதிரி
        city = None
        if " in " in command:
            city = command.split(" in ")[-1].strip().title()
        elif " at " in command:
            city = command.split(" at ")[-1].strip().title()
        elif " for " in command:
            city = command.split(" for ")[-1].strip().title()

        speak("Checking the weather, please wait.")
        try:
            weather_text = get_weather(city)
            speak(weather_text)
        except Exception as e:
            print(f"[Weather Error] {e}")
            speak("Sorry, I could not fetch weather right now.")

    # ══════════════════════════════════════════════════════════
    #  TASK MANAGER + REMINDERS
    # ══════════════════════════════════════════════════════════
    elif any(w in command for w in [
        "add task", "new task", "create task", "add a task",
        "my tasks", "show tasks", "list tasks", "what are my tasks",
        "pending tasks", "all tasks", "show my tasks",
        "complete task", "done task", "finish task", "task done",
        "delete task", "remove task", "cancel task",
        "clear completed", "clear done",
        "delete all tasks", "clear all tasks", "remove all tasks",
        "reset tasks", "clear all", "delete all",
        "remind me", "set reminder", "reminder at", "remind at", "alert me"
    ]):
        response = handle_task_command(command, take_command, speak)
        if response:
            speak(response)
        else:
            speak("Sorry, I could not process that task command.")

    # ══════════════════════════════════════════════════════════
    #  DEVELOPER MODE
    # ══════════════════════════════════════════════════════════
    elif any(w in command for w in [
        # File operations
        "create file", "new file", "make file",
        "create python", "new python", "create html",
        "create javascript", "create css",
        # AI Code Generator
        "generate code", "create code", "write code",
        "generate python", "generate html", "build a",
        "code for", "make a program", "create a program",
        "write a program", "create a function",
        # Run code
        "run code", "run file", "run python",
        "execute file", "execute code",
        # Explain + Fix
        "explain code", "explain file", "fix bugs",
        "fix code", "fix errors", "debug code",
        # Terminal
        "open terminal", "open cmd", "run command",
        "terminal command", "python version", "pip version",
        "list packages", "installed packages", "create venv",
        "run tests", "git log", "ip address", "system info",
        # Project
        "open project", "open vs code", "open vscode",
        "list files", "show files", "what files",
        # Install
        "install package", "install library", "pip install",
        # Git
        "git status", "git commit", "git push", "git pull",
        "commit code", "push code", "push to github", "commit changes"
    ]):
        response = handle_dev_command(command, take_command, speak)
        if response:
            speak(response)
        else:
            speak("Sorry, I could not process that developer command.")

    # ══════════════════════════════════════════════════════════
    #  ADVANCED FEATURES
    # ══════════════════════════════════════════════════════════

    # ── 1. SCREEN VISION 🖥️
    elif any(w in command for w in ["look at my screen", "explain my screen", "analyze my screen", "what is on my screen", "explain screen", "look at screen"]):
        speak("Taking a screenshot and analyzing it, please wait.")
        try:
            import pyautogui
            from chatgpt import ask_chatgpt_vision
            
            # Save screenshot
            temp_dir = os.path.join(os.path.dirname(__file__), "scratch")
            os.makedirs(temp_dir, exist_ok=True)
            screenshot_path = os.path.join(temp_dir, "vision_temp.png")
            
            img = pyautogui.screenshot()
            img.save(screenshot_path)
            
            # Call vision API
            analysis = ask_chatgpt_vision(screenshot_path, "Analyze this screenshot. What is currently on the screen? Give a very concise summary in 2-3 sentences. No markdown.")
            speak(analysis)
        except Exception as e:
            print(f"[Vision Error] {e}")
            speak("Sorry, I could not analyze the screen right now.")

    # ── 2. DEV WORKSPACE AUTOMATION 🚀
    elif any(w in command for w in ["prepare coding environment", "developer setup", "developer workspace", "dev workspace", "dev setup"]):
        speak("Preparing your developer workspace now, Praveen.")
        try:
            # 1. Open VS Code
            _open_shortcut("vscode")
            
            # 2. Create and open play file
            play_file = os.path.join(r"C:\Users\prave\OneDrive\Desktop\Jarvis", "dev_playground.py")
            if not os.path.exists(play_file):
                with open(play_file, "w", encoding="utf-8") as f:
                    f.write("# Developer playground created by Jarvis\nprint('Hello Praveen, let\\'s code!')\n")
            
            # 3. Open College Chrome Profile
            _open_shortcut("chrome_college")
            
            speak("Your developer workspace is ready.")
        except Exception as e:
            print(f"[Workspace Error] {e}")
            speak("Sorry, I had some trouble setting up the workspace.")

    # ── 3. SYSTEM HEALTH DASHBOARD 📊
    elif any(w in command for w in ["system health", "how is my computer", "system dashboard", "system status", "computer status"]):
        speak("Checking system health, please wait.")
        try:
            # CPU Load
            cpu_cmd = "wmic cpu get loadpercentage"
            cpu_out, _, _ = _run_cmd(cpu_cmd)
            cpu_val = "unknown"
            for line in cpu_out.split('\n'):
                line = line.strip()
                if line.isdigit():
                    cpu_val = f"{line}%"
                    break
            
            # RAM Load
            ram_cmd = "wmic OS get FreePhysicalMemory,TotalVisibleMemorySize"
            ram_out, _, _ = _run_cmd(ram_cmd)
            ram_lines = [line.strip() for line in ram_out.split('\n') if line.strip()]
            ram_val = "unknown"
            if len(ram_lines) > 1:
                parts = ram_lines[1].split()
                if len(parts) >= 2:
                    free_mem = int(parts[0])
                    total_mem = int(parts[1])
                    used_mem_gb = (total_mem - free_mem) / (1024 * 1024)
                    total_mem_gb = total_mem / (1024 * 1024)
                    ram_percent = int(((total_mem - free_mem) / total_mem) * 100)
                    ram_val = f"{ram_percent}% (using {used_mem_gb:.1f} GB of {total_mem_gb:.1f} GB)"
            
            # Battery status
            bat_cmd = "powershell -Command \"Get-CimInstance -ClassName Win32_Battery | Select-Object -Property EstimatedChargeRemaining, BatteryStatus\""
            bat_out, _, _ = _run_cmd(bat_cmd)
            bat_lines = [line.strip() for line in bat_out.split('\n') if line.strip()]
            charge = "unknown"
            status_desc = "discharging"
            if len(bat_lines) > 2:
                parts = bat_lines[2].split()
                if len(parts) >= 1 and parts[0].isdigit():
                    charge = f"{parts[0]}%"
                if len(parts) >= 2:
                    status_code = parts[1]
                    if status_code == "2":
                        status_desc = "charging"
                    elif status_code == "1":
                        status_desc = "discharging"
                    elif status_code == "3":
                        status_desc = "fully charged"
            
            # Disk Space
            disk_cmd = "wmic logicaldisk where DeviceID='C:' get FreeSpace,Size"
            disk_out, _, _ = _run_cmd(disk_cmd)
            disk_lines = [line.strip() for line in disk_out.split('\n') if line.strip()]
            disk_val = "unknown"
            if len(disk_lines) > 1:
                parts = disk_lines[1].split()
                if len(parts) >= 2:
                    free_b = int(parts[0])
                    size_b = int(parts[1])
                    free_gb = free_b / (1024 * 1024 * 1024)
                    size_gb = size_b / (1024 * 1024 * 1024)
                    disk_val = f"{free_gb:.1f} GB free of {size_gb:.1f} GB"

            report = f"Praveen, here is your system health report. CPU load is currently {cpu_val}. RAM utilization is {ram_val}."
            if charge != "unknown":
                report += f" Battery is at {charge} and is currently {status_desc}."
            if disk_val != "unknown":
                report += f" Your C drive has {disk_val}."
            speak(report)
        except Exception as e:
            print(f"[System Health Error] {e}")
            speak("Sorry, I had trouble reading system status.")

    # ── 5. REAL-TIME TRANSLATOR 🗣️
    elif any(w in command for w in ["translate", "translator"]):
        target_lang = "English"
        if "to tamil" in command or ("tamil" in command and "to english" not in command):
            target_lang = "Tamil"
            speak("Starting translator to Tamil. Say whatever you want to translate.")
        else:
            speak("Starting translator to English. Speak now.")
            
        phrase = take_command()
        if phrase and phrase != "none":
            speak("Translating...")
            try:
                from chatgpt import translate_text
                translation = translate_text(phrase, target_lang)
                speak(f"Translation: {translation}")
            except Exception as e:
                print(f"[Translator Error] {e}")
                speak("Sorry, I could not complete the translation.")
        else:
            speak("No speech detected. Exiting translator.")

    # ══════════════════════════════════════════════════════════
    #  AI FALLBACK & INTELLIGENT INTENT ROUTER
    # ══════════════════════════════════════════════════════════
    else:
        try:
            from chatgpt import route_intent_with_llm
            response = route_intent_with_llm(command)
            
            if response.startswith("[ACTION:"):
                # Parse LLM generated action
                action_part = response.split("]")[0]
                action_type = action_part.replace("[ACTION:", "").strip()
                parameter = response.replace(action_part + "]", "").strip()
                
                print(f"[LLM Intent Router] Triggered Action: {action_type} with parameter: {parameter}")
                
                if action_type == "open_url":
                    speak("Opening website")
                    _open_browser("chrome", parameter)
                elif action_type == "open_shortcut":
                    speak(f"Opening {parameter}")
                    _open_shortcut(parameter)
                elif action_type == "search_google":
                    speak(f"Searching Google for {parameter}")
                    _open_browser("chrome", f"https://www.google.com/search?q={_encode(parameter)}")
                elif action_type == "play_youtube":
                    speak(f"Searching YouTube for {parameter}")
                    url = f"https://www.youtube.com/results?search_query={_encode(parameter)}"
                    _close_existing_app_windows("youtube")  # Close any previously open YouTube standalone app windows
                    if os.path.exists(BRAVE_PATH):
                        subprocess.Popen([BRAVE_PATH, f"--app={url}"])
                    elif os.path.exists(CHROME_PATH):
                        subprocess.Popen([CHROME_PATH, f"--app={url}"])
                    else:
                        _open_browser("chrome", url)
                elif action_type == "play_spotify":
                    speak(f"Searching Spotify for {parameter}")
                    url = f"https://open.spotify.com/search/{_encode(parameter)}"
                    _close_existing_app_windows("spotify")  # Close any previously open Spotify standalone app windows
                    if os.path.exists(BRAVE_PATH):
                        subprocess.Popen([BRAVE_PATH, f"--app={url}"])
                    elif os.path.exists(CHROME_PATH):
                        subprocess.Popen([CHROME_PATH, f"--app={url}"])
                    else:
                        _open_browser("chrome", url)
                elif action_type == "system_health":
                    execute_command("system health")
                elif action_type == "screen_vision":
                    execute_command("look at my screen")
                elif action_type == "translate":
                    execute_command(f"translate {parameter}")
                elif action_type == "volume":
                    if "up" in parameter.lower():
                        for _ in range(5): pyautogui.press("volumeup")
                        speak("Volume increased")
                    elif "down" in parameter.lower():
                        for _ in range(5): pyautogui.press("volumedown")
                        speak("Volume decreased")
                    elif "mute" in parameter.lower():
                        pyautogui.press("volumemute")
                        speak("Muted")
                    elif "unmute" in parameter.lower():
                        pyautogui.press("volumemute")
                        speak("Unmuted")
                elif action_type == "brightness":
                    words = parameter.split()
                    number = next((int(w) for w in words if w.isdigit()), 50)
                    _set_brightness(number)
                    speak(f"Brightness set to {number} percent")
                elif action_type == "shutdown":
                    execute_command("shutdown")
                elif action_type == "restart":
                    execute_command("restart")
                elif action_type == "sleep":
                    execute_command("sleep")
                elif action_type == "type_text":
                    pyautogui.write(parameter, interval=0.06)
                    pyautogui.press("enter")
                    speak("Done typing")
                elif action_type == "whatsapp_message":
                    parts = parameter.split("|")
                    contact = parts[0].strip()
                    msg = parts[1].strip() if len(parts) > 1 else None
                    _send_whatsapp_message(contact, msg)
                elif action_type == "close_app":
                    execute_command(f"close {parameter}")
                elif action_type == "media_control":
                    if "pause" in parameter.lower():
                        execute_command("pause")
                    elif "play" in parameter.lower():
                        execute_command("play")
                elif action_type == "focus_mode":
                    if "stop" in parameter.lower() or "cancel" in parameter.lower():
                        execute_command("stop focus")
                    else:
                        execute_command("focus mode")
                elif action_type == "take_note":
                    execute_command("take a note")
                else:
                    speak("Action not supported.")
            else:
                print(f"Jarvis: {response}")
                speak(response)
                
        except Exception as e:
            print(f"[AI Error] {e}")
            speak("I am having trouble connecting to AI right now")

    return None