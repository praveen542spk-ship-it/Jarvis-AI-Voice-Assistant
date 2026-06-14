import os
import sys

# Ensure correct working directory and sys.path for background execution
project_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(project_dir)
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

class DummyWriter:
    def write(self, x):
        pass
    def flush(self):
        pass

# Redirect stdout and stderr to a log file for debugging background execution
try:
    log_file = os.path.join(project_dir, "jarvis_debug.log")
    sys.stdout = open(log_file, "a", encoding="utf-8", buffering=1)
    sys.stderr = sys.stdout
    import time
    print(f"\n--- JARVIS LOG START: {time.strftime('%Y-%m-%d %H:%M:%S')} ---")
except Exception:
    # Fallback to dummy writer so prints never crash under pythonw.exe or hidden console
    sys.stdout = DummyWriter()
    sys.stderr = sys.stdout

import tkinter as tk
from tkinter import scrolledtext
from threading import Thread
import math, random, time

import speak as speak_module
from speak import speak
from listen import take_command
from commands import execute_command
from chatgpt import clear_memory, get_memory_count

# ── Global State ──────────────────────────────────────────────
jarvis_running = False
current_status = "IDLE"
mic_volume     = 0.0

# ── Colours ───────────────────────────────────────────────────
BG        = "#050a0e"
CYAN      = "#00f5ff"
CYAN_DIM  = "#007a80"
CYAN_DARK = "#003035"
AMBER     = "#ffb300"
RED       = "#ff3b3b"
GREEN     = "#00ff99"
GRAY      = "#0d1a22"
GRAY2     = "#1a2530"
WHITE     = "#e8f4f8"

# ── Root Window ───────────────────────────────────────────────
root = tk.Tk()
root.title("J.A.R.V.I.S")
root.geometry("1100x820")
root.configure(bg=BG)
root.resizable(False, False)

# ── Left canvas (animation) ───────────────────────────────────
canvas = tk.Canvas(root, width=720, height=820, bg=BG, highlightthickness=0)
canvas.place(x=0, y=0)

# ── Right panel (chat) ────────────────────────────────────────
right = tk.Frame(root, bg=GRAY, width=380, height=820)
right.place(x=720, y=0)
right.pack_propagate(False)

# Header
chat_header = tk.Frame(right, bg=CYAN_DARK, height=44)
chat_header.pack(fill="x")
chat_header.pack_propagate(False)

tk.Label(chat_header, text="CONVERSATION",
         font=("Courier New", 11, "bold"),
         bg=CYAN_DARK, fg=CYAN).pack(side="left", padx=12, pady=10)

mem_label = tk.Label(chat_header, text="MEM: 0",
                     font=("Courier New", 9), bg=CYAN_DARK, fg=CYAN_DIM)
mem_label.pack(side="right", padx=8, pady=10)

tk.Button(chat_header, text="CLR",
          font=("Courier New", 9, "bold"),
          bg=GRAY2, fg=RED,
          activebackground=GRAY, activeforeground=RED,
          relief="flat", bd=0, cursor="hand2",
          command=lambda: (clear_memory(), chat_clear())).pack(side="right", padx=4, pady=8)

tk.Frame(right, bg=CYAN_DARK, height=1).pack(fill="x")

# Scrollable chat area
chat_area = scrolledtext.ScrolledText(
    right, bg=GRAY, fg=WHITE,
    font=("Courier New", 10),
    wrap=tk.WORD, bd=0, padx=10, pady=8,
    state="disabled",
    insertbackground=CYAN,
    selectbackground=CYAN_DARK,
)
chat_area.pack(fill="both", expand=True)

chat_area.tag_config("you_name",    foreground=CYAN,      font=("Courier New", 9,  "bold"))
chat_area.tag_config("you_text",    foreground=WHITE,     font=("Courier New", 10))
chat_area.tag_config("jarvis_name", foreground=AMBER,     font=("Courier New", 9,  "bold"))
chat_area.tag_config("jarvis_text", foreground="#b0e8ef", font=("Courier New", 10))
chat_area.tag_config("sys_text",    foreground=CYAN_DIM,  font=("Courier New", 9,  "italic"))
chat_area.tag_config("sep",         foreground=CYAN_DARK, font=("Courier New", 8))

# Input bar
tk.Frame(right, bg=CYAN_DARK, height=1).pack(fill="x")
input_frame = tk.Frame(right, bg=GRAY2, height=46)
input_frame.pack(fill="x")
input_frame.pack_propagate(False)

chat_entry = tk.Entry(input_frame, bg=GRAY2, fg=WHITE,
                      font=("Courier New", 10),
                      insertbackground=CYAN,
                      relief="flat", bd=0, highlightthickness=0)
chat_entry.pack(side="left", fill="both", expand=True, padx=10, pady=12)

def send_typed(event=None):
    text = chat_entry.get().strip()
    if text:
        chat_entry.delete(0, "end")
        Thread(target=handle_text_input, args=(text,), daemon=True).start()

chat_entry.bind("<Return>", send_typed)
tk.Button(input_frame, text="SEND",
          font=("Courier New", 9, "bold"),
          bg=CYAN_DARK, fg=CYAN,
          activebackground=GRAY, activeforeground=CYAN,
          relief="flat", bd=0, cursor="hand2",
          command=send_typed).pack(side="right", padx=6, pady=8)

# ─────────────────────────────────────────────────────────────
#  CHAT HELPERS
#  IMPORTANT: background thread-லிருந்து safe-ஆ call ஆக
#             நேரடியா widget update பண்றோம் (root.after தேவையில்ல)
#             — tkinter ScrolledText is safe when called via
#               root.after(0, ...) which marshals to main thread.
# ─────────────────────────────────────────────────────────────
def _insert_msg(role, text):
    """Must run on main thread."""
    chat_area.config(state="normal")
    ts = time.strftime("%H:%M")
    if role == "you":
        chat_area.insert("end", f"\n  YOU  [{ts}]\n", "you_name")
        chat_area.insert("end", f"  {text}\n", "you_text")
    elif role == "jarvis":
        chat_area.insert("end", f"\n  JARVIS  [{ts}]\n", "jarvis_name")
        chat_area.insert("end", f"  {text}\n", "jarvis_text")
    elif role == "system":
        chat_area.insert("end", f"\n  ⬡ {text}\n", "sys_text")
    chat_area.insert("end", "  " + "─"*42 + "\n", "sep")
    chat_area.config(state="disabled")
    chat_area.see("end")
    mem_label.config(text=f"MEM: {get_memory_count()}")

def chat_add(role, text):
    """Thread-safe: schedules insert on main tkinter thread."""
    root.after(0, _insert_msg, role, str(text))

def chat_clear():
    def _do():
        chat_area.config(state="normal")
        chat_area.delete("1.0", "end")
        chat_area.config(state="disabled")
        _insert_msg("system", "Memory cleared — new conversation started")
    root.after(0, _do)

# ── Register speak → chat callback ───────────────────────────
# speak() எங்கிருந்து call ஆனாலும் chat_add("jarvis",...) trigger ஆகும்
speak_module.set_chat_callback(chat_add)

# ── Handle typed input ────────────────────────────────────────
def handle_text_input(text):
    chat_add("you", text)
    set_status("THINKING", text[:46] + "...")
    result = execute_command(text)   # commands.py → speak() → chat_add auto ✅
    if result == "exit":
        set_status("IDLE", "Stopped")
    else:
        set_status("IDLE", "Done — ready")

# ─────────────────────────────────────────────────────────────
#  CANVAS — HEADER
# ─────────────────────────────────────────────────────────────
canvas.create_text(360, 36, text="J.A.R.V.I.S",
                   fill=CYAN, font=("Courier New", 26, "bold"), anchor="center")
canvas.create_text(360, 60, text="Just A Rather Very Intelligent System",
                   fill=CYAN_DIM, font=("Courier New", 10), anchor="center")
canvas.create_line(50, 74, 670, 74, fill=CYAN_DARK, width=1)

# ─────────────────────────────────────────────────────────────
#  HOLOGRAPHIC TECH GRID BACKGROUND
# ─────────────────────────────────────────────────────────────
def _draw_tech_grid():
    grid_gap = 50
    # Draw horizontal and vertical tech points
    for x in range(0, 720, grid_gap):
        for y in range(80, 520, grid_gap):
            canvas.create_oval(x-1, y-1, x+1, y+1, fill="#001a22", outline="")
            
    # Technical HUD brackets at the corners
    canvas.create_line(40, 100, 40, 82, 58, 82, fill=CYAN_DARK, width=1)
    canvas.create_line(680, 100, 680, 82, 662, 82, fill=CYAN_DARK, width=1)
    canvas.create_line(40, 500, 40, 518, 58, 518, fill=CYAN_DARK, width=1)
    canvas.create_line(680, 500, 680, 518, 662, 518, fill=CYAN_DARK, width=1)

_draw_tech_grid()

# ─────────────────────────────────────────────────────────────
#  CORE HUD & GYROSCOPIC RINGS
# ─────────────────────────────────────────────────────────────
CX, CY = 360, 295
rings = []

# Gyroscopic Segmented Arcs
# Ring 1: Outer segmented tech scale (dash pattern)
r1_id = canvas.create_oval(CX-165, CY-165, CX+165, CY+165, outline="#002b36", width=1, dash=(2, 8))
rings.append({"id": r1_id, "type": "static_dash", "base_r": 165, "phase": 0.0})

# Ring 2: Primary Clockwise Slotted Ring
r2_id = canvas.create_arc(CX-140, CY-140, CX+140, CY+140, start=0, extent=130, style="arc", outline=CYAN_DARK, width=2)
rings.append({"id": r2_id, "type": "arc", "base_r": 140, "dir": 1.0, "speed": 1.5, "phase": 0.0})

# Ring 3: Counter-Clockwise Double Slotted Ring
r3_id = canvas.create_arc(CX-118, CY-118, CX+118, CY+118, start=180, extent=110, style="arc", outline=CYAN_DIM, width=2)
rings.append({"id": r3_id, "type": "arc", "base_r": 118, "dir": -1.3, "speed": 2.2, "phase": 1.5})

# Ring 4: Innermost glowing technical circle
r4_id = canvas.create_oval(CX-85, CY-85, CX+85, CY+85, outline="#003544", width=1, dash=(6, 12))
rings.append({"id": r4_id, "type": "static_dash", "base_r": 85, "phase": 3.0})

# Core elements
core_outer = canvas.create_oval(CX-65, CY-65, CX+65, CY+65, fill="#01121a", outline=CYAN, width=1)
canvas.create_oval(CX-42, CY-42, CX+42, CY+42, fill="#001c24", outline=CYAN_DIM, width=1)
canvas.create_oval(CX-7, CY-7, CX+7, CY+7, fill=CYAN, outline="")

core_label = canvas.create_text(CX, CY, text="READY", fill=CYAN, font=("Courier New", 18, "bold"))
scan_line  = canvas.create_line(CX, CY, CX+125, CY, fill="#002e3b", width=1)

# HUD technical brackets & crosshairs
for xa, xb in [(CX-72, CX-52), (CX+52, CX+72)]:
    canvas.create_line(xa, CY, xb, CY, fill=CYAN_DARK, width=1)
for ya, yb in [(CY-72, CY-52), (CY+52, CY+72)]:
    canvas.create_line(CX, ya, CX, yb, fill=CYAN_DARK, width=1)

# Degree HUD Labels
canvas.create_text(CX, CY-178, text="N  00°", fill=CYAN_DARK, font=("Courier New", 7))
canvas.create_text(CX+178, CY, text="E  90°", fill=CYAN_DARK, font=("Courier New", 7))
canvas.create_text(CX, CY+178, text="S 180°", fill=CYAN_DARK, font=("Courier New", 7))
canvas.create_text(CX-178, CY, text="W 270°", fill=CYAN_DARK, font=("Courier New", 7))

# Orbit dots
orbit_items = []
for i in range(8):
    dot = canvas.create_oval(0, 0, 6, 6, fill=CYAN, outline="")
    orbit_items.append({"id": dot, "phase": (2*math.pi/8)*i})

# Waveform Lines (Double-layered symmetrical neon oscilloscope waves)
WAVE_Y = 530
wave_cyan = canvas.create_line(100, WAVE_Y, 620, WAVE_Y, fill=CYAN, width=2, smooth=True)
wave_dim  = canvas.create_line(100, WAVE_Y, 620, WAVE_Y, fill=CYAN_DIM, width=1, smooth=True)

# Swirling Vortex Particles
MAX_PARTICLES = 35
def make_particle():
    a = random.uniform(0, 2*math.pi)
    r = random.uniform(15, 60)
    s = random.uniform(1.2, 3.2)
    sz = random.choice([2, 3])
    lf = random.randint(50, 130)
    return {
        "angle": a,
        "r": r,
        "speed": s,
        "size": sz,
        "life": lf,
        "max_life": lf,
        "id": canvas.create_oval(0, 0, sz, sz, fill=CYAN_DIM, outline="")
    }

particles = [make_particle() for _ in range(MAX_PARTICLES)]

# ─────────────────────────────────────────────────────────────
#  STATUS BOX
# ─────────────────────────────────────────────────────────────
canvas.create_rectangle(50, 540, 670, 586, fill=GRAY2, outline=CYAN_DARK, width=1)
status_id = canvas.create_text(360, 563,
    text="● IDLE — Press START to activate",
    fill=CYAN, font=("Courier New", 12, "bold"), anchor="center")

# ─────────────────────────────────────────────────────────────
#  COMMAND LOG
# ─────────────────────────────────────────────────────────────
canvas.create_rectangle(50, 596, 670, 726, fill=GRAY2, outline=CYAN_DARK, width=1)
canvas.create_text(62, 608, text="RECENT COMMANDS",
                   fill=CYAN_DIM, font=("Courier New", 9), anchor="w")
canvas.create_line(50, 618, 670, 618, fill=CYAN_DARK, width=1)
log_ids     = []
cmd_history = []
for i in range(4):
    log_ids.append(canvas.create_text(66, 632+i*22, text="",
                   fill=CYAN_DIM, font=("Courier New", 9), anchor="w"))

def log_command(text):
    cmd_history.append(text)
    if len(cmd_history) > 4:
        cmd_history.pop(0)
    for i, lid in enumerate(log_ids):
        if i < len(cmd_history):
            canvas.itemconfig(lid, text=f"› {cmd_history[len(cmd_history)-1-i][:52]}")
        else:
            canvas.itemconfig(lid, text="")

# ─────────────────────────────────────────────────────────────
#  BUTTONS
# ─────────────────────────────────────────────────────────────
def make_btn(x, y, w, h, label, color, cmd):
    btn = tk.Button(root, text=label, font=("Courier New", 10, "bold"),
                    bg=GRAY2, fg=color,
                    activebackground=CYAN_DARK, activeforeground=CYAN,
                    relief="flat", bd=0, cursor="hand2", command=cmd)
    canvas.create_window(x, y, anchor="nw", window=btn, width=w, height=h)

# START button — face login pass ஆனாலே enable ஆகும்
start_btn = tk.Button(root, text="▶  START",
    font=("Courier New", 10, "bold"),
    bg=GRAY2, fg=CYAN_DIM,          # Dimmed initially = disabled look
    activebackground=CYAN_DARK, activeforeground=CYAN,
    relief="flat", bd=0, cursor="hand2",
    state="disabled",               # Face login முன்னே disabled
    command=lambda: toggle_jarvis(True))
canvas.create_window(80, 740, anchor="nw", window=start_btn, width=170, height=38)

make_btn(270, 740, 170, 38, "■  STOP",  AMBER, lambda: toggle_jarvis(False))
make_btn(460, 740, 160, 38, "✕  EXIT",  RED,   root.quit)

def enable_start_btn():
    """Face login success → START button enable பண்ணு."""
    start_btn.config(state="normal", fg=CYAN)

def disable_start_btn():
    """Face login fail → START button disabled வை."""
    start_btn.config(state="disabled", fg=CYAN_DIM)

canvas.create_line(50, 738, 670, 738, fill=CYAN_DARK, width=1)
canvas.create_text(60,  790, text="v4.0 — Chat + Memory Edition",
                   fill=CYAN_DARK, font=("Courier New", 9), anchor="w")
canvas.create_text(660, 790, text="Praveen × OpenAI",
                   fill=CYAN_DARK, font=("Courier New", 9), anchor="e")

def corner(x1, y1, x2, y2, o):
    ln = 16
    if o=="tl": canvas.create_line(x1,y1+ln,x1,y1,x1+ln,y1, fill=CYAN, width=1)
    if o=="tr": canvas.create_line(x2,y1+ln,x2,y1,x2-ln,y1, fill=CYAN, width=1)
    if o=="bl": canvas.create_line(x1,y2-ln,x1,y2,x1+ln,y2, fill=CYAN, width=1)
    if o=="br": canvas.create_line(x2,y2-ln,x2,y2,x2-ln,y2, fill=CYAN, width=1)
for o in ["tl","tr","bl","br"]:
    corner(18, 18, 702, 802, o)

# ─────────────────────────────────────────────────────────────
#  STATUS HELPER
# ─────────────────────────────────────────────────────────────
def set_status(state, text):
    global current_status
    current_status = state
    colours = {"IDLE": CYAN_DIM, "LISTENING": CYAN, "THINKING": AMBER, "SPEAKING": GREEN}
    icons   = {"IDLE": "●", "LISTENING": "◉", "THINKING": "◈", "SPEAKING": "▶"}
    col  = colours.get(state, CYAN_DIM)
    icon = icons.get(state, "●")
    root.after(0, lambda: canvas.itemconfig(status_id,
               text=f"{icon} {state} — {text[:46]}", fill=col))

# ─────────────────────────────────────────────────────────────
#  JARVIS VOICE THREAD
# ─────────────────────────────────────────────────────────────
def volume_cb(vol):
    global mic_volume
    mic_volume = vol

def run_jarvis():
    global jarvis_running, mic_volume
    greeting = "Hello Praveen! Jarvis is ready. How can I help you?"
    set_status("SPEAKING", "Hello Praveen!")
    chat_add("system", "Jarvis activated — voice mode ON")
    speak(greeting)   # speak() → callback → chat_add("jarvis", greeting) ✅

    while jarvis_running:
        set_status("LISTENING", "Waiting for your voice...")
        command = take_command(volume_callback=volume_cb)
        mic_volume = 0.0

        if not jarvis_running:
            break
        if command == "none":
            set_status("IDLE", "Nothing heard — try again")
            time.sleep(0.3)
            continue

        chat_add("you", command)
        log_command(command)
        set_status("THINKING", command[:46] + "...")

        # execute_command → internally calls speak(response)
        # speak() → _chat_callback → chat_add("jarvis", response) ✅
        result = execute_command(command)

        if result == "exit":
            set_status("IDLE", "Goodbye!")
            jarvis_running = False
            root.after(2000, root.withdraw)
            break

        set_status("IDLE", "Done — listening again...")
        time.sleep(0.3)

def toggle_jarvis(start):
    global jarvis_running
    if start and not jarvis_running:
        jarvis_running = True
        Thread(target=run_jarvis, daemon=True).start()
    elif not start and jarvis_running:
        jarvis_running = False
        set_status("IDLE", "Stopped by user")
        chat_add("system", "Jarvis stopped")
        speak("Stopping. Goodbye!")
        root.after(2000, root.withdraw)

# ─────────────────────────────────────────────────────────────
#  ANIMATION LOOP
# ─────────────────────────────────────────────────────────────
anim_tick = 0

def animate():
    global anim_tick
    anim_tick += 1
    t   = anim_tick
    spd = {"IDLE":1.0,"LISTENING":2.2,"THINKING":3.8,"SPEAKING":1.8}.get(current_status,1.0)
    lbl = {"IDLE":CYAN_DARK,"LISTENING":CYAN,"THINKING":AMBER,"SPEAKING":GREEN}.get(current_status,CYAN)
    lbl_text = {"IDLE":CYAN,"LISTENING":CYAN,"THINKING":AMBER,"SPEAKING":GREEN}.get(current_status,CYAN)
    
    # 1. Update Core Label Text dynamically based on status
    state_label = {"IDLE": "READY", "LISTENING": "LISTEN", "THINKING": "THINK", "SPEAKING": "JARVIS"}.get(current_status, "READY")
    canvas.itemconfig(core_label, text=state_label, fill=lbl_text)

    # 2. Tech Rings Animation (Concentric segmented arcs counter-rotating)
    for rd in rings:
        pulse = math.sin(t*0.04*spd + rd["phase"]) * 6
        r = rd["base_r"] + pulse + (mic_volume*28 if current_status=="LISTENING" else 0)
        canvas.coords(rd["id"], CX-r, CY-r, CX+r, CY+r)
        
        # If it is an arc, update its starting rotation angle
        if rd.get("type") == "arc":
            canvas.itemconfig(rd["id"], start=(t * rd["speed"] * rd["dir"]) % 360, outline=lbl)
        else:
            canvas.itemconfig(rd["id"], outline=lbl if current_status!="IDLE" else "#002530")

    # 3. Concentric Core scale pulse
    cr = 65 + math.sin(t*0.07)*4 + (mic_volume*18 if current_status=="LISTENING" else 0)
    canvas.coords(core_outer, CX-cr, CY-cr, CX+cr, CY+cr)
    canvas.itemconfig(core_outer, outline=lbl_text)

    # 4. Tech Orbit dots
    orb_r = 103 + math.sin(t*0.03)*8 + (mic_volume*22 if current_status=="LISTENING" else 0)
    for od in orbit_items:
        od["phase"] += 0.015 * spd
        ox = CX + math.cos(od["phase"])*orb_r - 3
        oy = CY + math.sin(od["phase"])*orb_r - 3
        canvas.coords(od["id"], ox, oy, ox+6, oy+6)
        canvas.itemconfig(od["id"], fill=lbl_text)

    # 5. Glowing Radial scan line (speeds up when thinking)
    sa  = (t * (2.0 if current_status!="THINKING" else 5)) % 360
    rad = math.radians(sa)
    canvas.coords(scan_line, CX, CY, CX+math.cos(rad)*125, CY+math.sin(rad)*125)
    canvas.itemconfig(scan_line, fill=lbl if current_status!="IDLE" else "#002530")

    # 6. Symmetrical Neon Oscilloscope Waveform (Double-layered sine waves)
    amplitude = 12 + mic_volume * 45 if current_status == "LISTENING" else (16 if current_status == "SPEAKING" else 4)
    if current_status == "IDLE":
        amplitude = 2 # low calm ripple
        
    freq_mult = 2.5 if current_status == "THINKING" else (1.5 if current_status == "SPEAKING" else 1.0)
    
    pts_cyan = []
    pts_dim  = []
    x_start, x_end = 100, 620
    
    for x in range(x_start, x_end + 1, 10):
        norm_x = (x - x_start) / (x_end - x_start) # 0.0 to 1.0
        envelope = math.sin(norm_x * math.pi) # Symmetrical envelope (starts and ends at 0)
        
        # Primary Wave
        y_cyan = WAVE_Y + envelope * amplitude * math.sin(norm_x * 12 * freq_mult - t * 0.18)
        pts_cyan.extend([x, y_cyan])
        
        # Secondary Wave (out of phase, slightly smaller)
        y_dim = WAVE_Y + envelope * (amplitude * 0.6) * math.sin(norm_x * 10 * freq_mult + t * 0.12 + 1.5)
        pts_dim.extend([x, y_dim])
        
    canvas.coords(wave_cyan, *pts_cyan)
    canvas.itemconfig(wave_cyan, fill=lbl_text if current_status!="IDLE" else CYAN_DIM)
    
    canvas.coords(wave_dim, *pts_dim)
    canvas.itemconfig(wave_dim, fill=lbl if current_status!="IDLE" else CYAN_DARK)

    # 7. Spiral Vortex Swirling Particles
    for _ in range(2 if current_status=="IDLE" else 4):
        if len(particles) < MAX_PARTICLES:
            particles.append(make_particle())
            
    dead = []
    for p in particles:
        p["life"] -= 1
        if p["life"] <= 0:
            canvas.delete(p["id"])
            dead.append(p)
            continue
            
        # Spiral/Vortex math (Inward spiral for THINKING state)
        if current_status == "THINKING":
            p["r"] -= p["speed"] * 1.5
            p["angle"] -= 0.08
            if p["r"] < 10: # died by core absorption
                canvas.delete(p["id"])
                dead.append(p)
                continue
        else:
            p["r"] += p["speed"]
            p["angle"] += 0.04
            
        x = CX + math.cos(p["angle"]) * p["r"]
        y = CY + math.sin(p["angle"]) * p["r"]
        
        a_fade = p["life"] / p["max_life"]
        g = int(min(255, a_fade * 255))
        b = int(min(255, a_fade * 255))
        
        try:
            canvas.coords(p["id"], x, y, x + p["size"], y + p["size"])
            # Set glowing color based on status
            if current_status == "LISTENING":
                canvas.itemconfig(p["id"], fill=f"#00{g:02x}ff")
            elif current_status == "THINKING":
                canvas.itemconfig(p["id"], fill=f"#ff{g:02x}00")
            elif current_status == "SPEAKING":
                canvas.itemconfig(p["id"], fill=f"#00ff{g:02x}")
            else:
                canvas.itemconfig(p["id"], fill=f"#00{g:02x}{b:02x}")
        except Exception:
            dead.append(p)
            
    for p in dead:
        if p in particles:
            particles.remove(p)

    root.after(35, animate)

# ─────────────────────────────────────────────────────────────
#  FACE LOGIN — Camera feed on canvas (DEPRECATED - REMOVED)
# ─────────────────────────────────────────────────────────────


def run_wake_word_loop():
    root.after(0, enable_start_btn)
    # Hide window on startup
    root.after(0, root.withdraw)
    
    chat_add("system", "Wake Word Active — Jarvis is running silently in the background!")
    
    while True:
        if not jarvis_running:
            set_status("IDLE", "Say 'Hey Jarvis' to wake me")
            command = take_command()
            
            if command != "none":
                command_clean = command.lower().strip()
                print(f"[Wake Word Check] Heard: {command_clean}")
                
                # Check for wake words
                if any(w in command_clean for w in ["hey jarvis", "hello jarvis", "wake up jarvis", "hi jarvis", "jarvis"]):
                    chat_add("system", "Wake word detected!")
                    # Show and focus window
                    root.after(0, root.deiconify)
                    root.after(0, lambda: root.state("normal"))
                    root.after(0, root.focus_force)
                    
                    toggle_jarvis(True)
                    
        time.sleep(0.4)


def on_closing():
    if jarvis_running:
        toggle_jarvis(False)
    else:
        root.withdraw()


root.protocol("WM_DELETE_WINDOW", on_closing)


# ─────────────────────────────────────────────────────────────
#  STARTUP
# ─────────────────────────────────────────────────────────────
Thread(target=run_wake_word_loop, daemon=True).start()
animate()
root.mainloop()