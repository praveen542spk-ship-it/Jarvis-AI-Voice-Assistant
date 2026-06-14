import win32com.client
import pythoncom

# Chat display callback — jarvis_ui.py இதை set பண்ணும்
_chat_callback = None

def set_chat_callback(fn):
    global _chat_callback
    _chat_callback = fn

def speak(text):
    """
    1. Chat panel-ல் display பண்ணு (callback வழியா)
    2. Voice-ல் பேசு (SAPI.SpVoice மூலமாக 100% COM-STA த்ரெட் சேஃப்)
    """
    # Chat-ல் display
    if _chat_callback:
        try:
            _chat_callback("jarvis", str(text))
        except Exception as e:
            print(f"[Chat callback error] {e}")

    # Native SAPI Speech (Thread-safe on-demand COM initialization)
    try:
        # Initialize COM for the current calling thread (STA safe!)
        pythoncom.CoInitialize()
        try:
            speaker = win32com.client.Dispatch("SAPI.SpVoice")
            voices = speaker.GetVoices()
            if voices.Count > 1:
                # Set female voice (index 1 is Zira, index 0 is David)
                speaker.Voice = voices.Item(1)
            speaker.Rate = 1       # Slightly faster, snappy speaking rate
            speaker.Volume = 100   # Max volume
            
            # Speak synchronously (0) so it blocks the command thread until speaking finishes,
            # which perfectly prevents microphone feedback loop!
            speaker.Speak(str(text), 0)
        finally:
            # Uninitialize COM for this thread
            pythoncom.CoUninitialize()
    except Exception as e:
        print(f"[Speak Error] {e}")