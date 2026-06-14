import speech_recognition as sr
import threading
import math

# GUI reads this to animate waveform (0.0 - 1.0)
mic_volume = 0.0
_vol_lock  = threading.Lock()

# Persistent, low-latency recognizer instance initialized globally
_recognizer = sr.Recognizer()
_recognizer.energy_threshold         = 120   # Highly sensitive threshold (hears whispers)
_recognizer.dynamic_energy_threshold = False # Fixed threshold to prevent sensitivity drift
_recognizer.pause_threshold          = 0.8

def get_volume():
    with _vol_lock:
        return mic_volume

def _set_volume(v):
    global mic_volume
    with _vol_lock:
        mic_volume = float(v)

def take_command(volume_callback=None):
    """
    Highly optimized, low-latency voice capture.
    No recurring 500ms ambient noise calibration delay, starting instant capturing.
    """
    try:
        with sr.Microphone() as source:
            print("Listening...")

            # Animate GUI instantly
            if volume_callback:
                for i in range(8):
                    volume_callback(math.sin(i * 0.4) * 0.3 + 0.15)

            # Instantly listen - no 0.5s calibration delay
            audio = _recognizer.listen(source, timeout=6, phrase_time_limit=7)

            if volume_callback:
                volume_callback(0.8)   # "processing" pulse

        print("Recognizing...")
        command = _recognizer.recognize_google(audio)
        print("You said:", command)

        if volume_callback:
            volume_callback(0.0)
        return command.lower()

    except sr.WaitTimeoutError:
        print("Timeout — nothing heard")
        if volume_callback:
            volume_callback(0.0)
        return "none"

    except sr.UnknownValueError:
        print("Could not understand audio")
        if volume_callback:
            volume_callback(0.0)
        return "none"

    except sr.RequestError as e:
        print(f"Google API error: {e}")
        if volume_callback:
            volume_callback(0.0)
        return "none"

    except Exception as e:
        print(f"[Listen Error] {e}")
        if volume_callback:
            volume_callback(0.0)
        return "none"