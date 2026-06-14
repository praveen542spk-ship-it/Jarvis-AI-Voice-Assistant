# 🪐 J.A.R.V.I.S — Just A Rather Very Intelligent System

[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Windows OS](https://img.shields.io/badge/OS-Windows-0078D6.svg)](https://www.microsoft.com/windows)

J.A.R.V.I.S is a highly advanced, premium personal AI voice assistant built specifically for Windows. Featuring a stunning **Cybernetic Holographic HUD (Heads-Up Display)** interface, silent background wake-word detection, direct native Windows Speech API (SAPI) feedback, and a state-of-the-art LLM (Large Language Model) router powered by Groq Llama, Jarvis brings the experience of having a sci-fi desktop assistant to life.

---

## 🌟 Key Features & Capabilities

### 1. 🕸️ Cybernetic Holographic HUD User Interface
Jarvis features a futuristic, responsive Tkinter-based HUD designed with clean, movie-accurate aesthetics:
- **Tech Grid Background**: A subtle, glowing HSL holographic hexagonal grid pattern providing visual depth.
- **Gyroscopic Tech Rings**: Symmetrical, counter-rotating segmented arcs and rings that change rotation speed, scale, and color based on Jarvis's state (Idle, Listening, Thinking, Speaking).
- **Vortex Particle System**: Cybernetic particles that float outwards during idle states and collapse inwards to the core during AI processing, simulating data ingestion.
- **Oscilloscope Waveform**: Symmetrical neon-glowing wave visualizations responding dynamically to real-time microphone input volume.

### 2. 🗣️ Wake Word Detection ("Hey Jarvis")
- Runs in a low-latency, background loop.
- Monitors microphone input using a **drift-free, fixed sensitivity threshold (120)** to capture whispering and soft speech.
- Instantly activates, launches the GUI, and greets the user when you say `"Hey Jarvis"`, `"Hello Jarvis"`, `"Wake up Jarvis"`, or `"Jarvis"`.
- Goes back to background sleep mode when you say `"bye"`, `"stop"`, or `"exit"`.

### 3. 💬 Advanced UWP WhatsApp Desktop Automation
- **Dynamic Window Title Scanner**: Automatically locates the active WhatsApp window handle, even if title titles contain dynamic badges like unread counts (e.g. `(3) WhatsApp`).
- **Foreground Forcing Lock-Bypass**: Uses an Alt-key trigger sequence via WScript Shell to bypass Windows foreground activation restrictions, ensuring WhatsApp is brought to the absolute front.
- **Dual-Method Search Focus**: Activates the search bar using a combination of keyboard shortcuts (`Ctrl + F`) and fallback physical window coordinates (`left + 180, top + 120`).
- **Precise Input Field Focus**: Calculates the exact relative location of the text field (`60%` width, `45px` up from bottom) to click and focus before executing typing.
- **Voice Typing & Sending**: Extract messages from natural speech and type them in directly, then automatically send them.

### 4. 🍅 Pomodoro Study Mode & Active Distraction Blocker
- Say *"focus mode"*, *"study mode"*, or *"pomodoro"* to activate.
- Starts a 25-minute study block with a remaining time indicator displayed on the HUD status bar.
- **Active Enforcer**: A background daemon thread scans active windows every 15 seconds and instantly force-closes distraction apps (**WhatsApp, Instagram, Telegram, Discord, Netflix, Facebook**) if you try to open them.
- Alerts you when focus time is complete and encourages a break.

### 5. 🖥️ Screen Vision & Active Window Analysis
- Say *"look at my screen"*, *"explain my screen"*, or *"what is on my screen"*.
- Instantly captures active window titles and maps the workspace.
- Feeds the snapshot text to the LLM to give you a contextual, spoken summary of what you are working on.

### 6. 📝 Voice Note Maker & Notepad Opener
- Say *"take a note"*, *"create a note"*, or *"write a note about [topic]"*.
- Jarvis records your dictation, formats it into a clean Markdown document, saves it to a dated note in a `notes/` directory, and automatically opens it in Windows **Notepad** for immediate review.

### 7. 🗣️ Real-time Voice Translator
- Say *"translate"* or *"translator"*.
- Initiates an interactive bidirectional voice translation interface (Tamil ➔ English, English ➔ Tamil) utilizing Llama API formatting.

### 8. 📊 Live System Health Dashboard
- Say *"system health"*, *"system status"*, or *"how is my computer"*.
- Queries Windows Management Instrumentation (WMIC) for real-time CPU usage, RAM utilization, laptop battery percentage, and remaining C: drive space, reading out a voice report.

### 9. 🎵 Global Media Controls
- Say *"pause"*, *"pause music"*, or *"pause video"* to pause media globally.
- Say *"continue"*, *"play"*, *"carry on"*, `"unpause"`, or *"go on"* to resume.

---

## 🗣️ Voice Command Reference Guide

| Category | Voice Commands | Description |
| :--- | :--- | :--- |
| **Wake / Sleep** | `"Hey Jarvis"`, `"Hello Jarvis"`, `"Wake up"` / `"bye"`, `"stop"`, `"go to sleep"` | Wake up the GUI / Put Jarvis back to silent tray monitor mode. |
| **System Info** | `"system health"`, `"system status"`, `"how is my computer"` | Speaks CPU, RAM, Battery, and Disk Space usage. |
| **Chrome Launching** | `"open college chrome"`, `"open personal chrome"`, `"open chrome"` | Launches Chrome bypassing profile selection screen. |
| **Chrome Searches** | `"search [query] in college chrome"`, `"search [query] in personal chrome"` | Automatically searches target queries in selected user profiles. |
| **Universal Closer** | `"close [app name]"` (e.g. `"close chrome"`, `"close whatsapp"`, `"close vscode"`) | Closes application. VS Code requires confirmation unless forced. |
| **Media Playback** | `"pause"`, `"play"`, `"continue"`, `"carry on"`, `"unpause"`, `"go on"` | Media play/pause global keyboard emulation. |
| **WhatsApp Chat** | `"open whatsapp chat for [contact]"`, `"go to [contact] on whatsapp"` | Launches WhatsApp, searches, and opens contact chat window. |
| **WhatsApp Type** | `"type [message] and send"`, `"send [message] [text]"`, `"type"` | Voice-guided typing or direct message sending into focused chat. |
| **Pomodoro Focus** | `"focus mode"`, `"study mode"`, `"pomodoro"` / `"stop focus"`, `"cancel focus"` | Activates 25-minute distraction blocker / Cancels Pomodoro mode. |
| **Screen Analysis** | `"look at my screen"`, `"explain my screen"`, `"what's on my screen"` | Analyzes open applications and summarizes them. |
| **Notes** | `"take a note"`, `"create a note about [topic]"` | Records dictation, saves to MD note, and opens in Notepad. |
| **Translation** | `"translate"`, `"translator"` | Launches Tamil/English bidirectional translator loop. |
| **News / Weather** | `"weather"`, `"news"`, `"latest news"` | Reads out local weather and top news headlines. |
| **Tasks / Reminders** | `"add task [name]"`, `"show tasks"`, `"what are my tasks"`, `"clear tasks"` | Adds, lists, or clears voice-logged reminders. |

---

## 🏗️ Architectural Workflow

Below is the execution flow of how Jarvis processes user requests:

```
[Silent Tray Monitor Mode]
          │
          ▼ (Microphone Audio Input)
[Voice Wake Word Detection]
          │
          ├─► Match: "Hey Jarvis" ──► [Restore GUI & Wake Up]
          │                                      │
                                                 ▼ (Listen Active Command)
                                    [Speech Recognition Parser]
                                                 │
                                                 ▼ (Match Rules / Else Router)
                                          {Intent Router}
                                                 │
                  ┌──────────────────────────────┴──────────────────────────────┐
                  ▼ (Predefined Rule Match)                                     ▼ (Natural Language Fallback)
    [Direct Win32/Keyboard Execution]                             [Groq Llama-3.3 LLM Routing]
                  │                                                             │
                  │                                                             ▼ (Output Structured Actions)
                  └──────────────────────────────┬──────────────────────────────┘
                                                 ▼
                                     [Execute Command Action]
                                                 │
                                                 ▼
                                      [SAPI TTS Response]
                                                 │
                                                 ▼ (Return to Idle)
                                    [Restore Active Listening]
```

---

## 🛠️ Installation & Setup

### 1. Prerequisites
- **Python 3.11 or higher** installed on Windows.
- Git installed.
- A **Groq API Key** (Get one at [console.groq.com](https://console.groq.com)).

### 2. Clone the Repository & Install Dependencies
Open PowerShell or CMD in your working folder and run:
```bash
git clone https://github.com/praveen542spk-ship-it/Jarvis-AI-Voice-Assistant.git
cd Jarvis-AI-Voice-Assistant
pip install -r requirements.txt
```

### 3. Add your Groq API Key
Create a file named `groq_key.txt` in the root of the project directory and paste your API key inside:
```
gsk_xxxx...
```
> [!IMPORTANT]
> Do not rename this file. `groq_key.txt` is already added to `.gitignore` to prevent you from accidentally pushing your private API key to GitHub.

### 4. Enable Windows Startup Launcher (Optional)
To have Jarvis load silently in the background automatically when you boot up your computer:
```bash
python setup_startup.py
```
This installs `jarvis_startup.vbs` inside your Windows Startup folder.

---

## 🚀 How to Run

1. Simply double-click **`run_jarvis.bat`** or execute:
   ```bash
   python jarvis_ui.py
   ```
2. Jarvis will start up minimized and run silently in your background.
3. Say **"Hey Jarvis"** to wake it up!
4. The Tkinter GUI contains three control buttons:
   - **START**: Toggles/resumes active voice listening.
   - **STOP**: Pauses active voice listening (useful when you are watching movies or talking to others).
   - **EXIT**: Fully shuts down the Jarvis background process.

---

## 📂 Project Structure

- `jarvis_ui.py` — Core Tkinter GUI, gyroscopic animation engine, and wake-word listener loop.
- `commands.py` — Voice command execution logic, WhatsApp automation, and media keyboard emulation.
- `listen.py` — Low-latency, fixed-threshold microphone speech capture.
- `speak.py` — Direct Windows Native SAPI SpVoice engine with multi-threading COM guards.
- `chatgpt.py` — Groq Llama LLM intent router, memory buffer, and screen vision parser.
- `news_weather.py` — Weather geolocation and top news scraper.
- `tasks.py` — Voice reminder list manager.
- `developer.py` — Voice playground code runner.
- `setup_startup.py` — Startup launcher setup utility.
- `run_jarvis.bat` — One-click CMD redirection launcher.

---

## ⚙️ Customization & Tweaks

### Changing Chrome Profiles
If your browser profiles differ, open `commands.py` and update the paths inside `open_chrome_profile`:
- Modify the shortcut names or profile parameters (e.g. `--profile-directory="Default"` or `--profile-directory="Profile 5"`) to map to your custom Chrome users.

### Modifying Voice Thresholds
If Jarvis triggers too easily or doesn't hear you:
- Open `listen.py` and tweak `self.energy_threshold = 120`. Increase it (e.g., to `180`) if your room is noisy, or decrease it if you want it to hear extremely soft whispers.

---

## 🩺 Troubleshooting

### 1. Jarvis UI does not start up
- Verify that your Groq API key is placed inside `groq_key.txt` in the root folder.
- Run `pip install -r requirements.txt` again to ensure all packages are fully installed.

### 2. Multi-Process Lock (Jarvis is unresponsive or speech is frozen)
- If you ran Jarvis multiple times, there may be orphaned processes in the background competing for your microphone.
- Open PowerShell and run:
  ```powershell
  python scratch/kill_all_python_jarvis.py
  ```
  This will clean terminate all stuck background python instances.

### 3. Speech API COM Error / Threading Hangs
- If your SAPI SpVoice throws COM initialization errors, Jarvis has already solved this by calling `pythoncom.CoInitialize()` before SAPI invocation. Make sure you do not launch `speak.py` from raw sub-threads without proper COM initialization.
