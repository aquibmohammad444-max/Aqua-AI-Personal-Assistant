import tkinter as tk
import speech_recognition as sr
import pyttsx3
import datetime
import webbrowser
import wikipedia
import requests
import urllib.parse
import threading
import subprocess
import os
import re
import math
import psutil
import shutil
import platform
import time


# ============================================================
# AQUA 3.0
# ADVANCED AI PERSONAL ASSISTANT
# ============================================================

APP_NAME = "AQUA"
NOTES_FILE = "aqua_notes.txt"

# ---------------- THEME ----------------

BG = "#030712"
TEXT = "#F5FAFF"
MUTED = "#71839A"
CYAN = "#00E5FF"
PURPLE = "#8B5CF6"
GREEN = "#22E6A7"
RED = "#FF5577"


# ============================================================
# VOICE ENGINE
# ============================================================

engine = pyttsx3.init()

engine.setProperty("rate", 175)
engine.setProperty("volume", 1.0)

try:
    voices = engine.getProperty("voices")

    if voices:
        engine.setProperty("voice", voices[0].id)

except Exception:
    pass


# ============================================================
# WINDOW
# ============================================================

root = tk.Tk()

root.title("AQUA")
root.geometry("900x650")
root.minsize(700, 550)
root.configure(bg=BG)


# ============================================================
# VARIABLES
# ============================================================

status_var = tk.StringVar(value="READY")
response_var = tk.StringVar(
    value="I'm ready."
)

orb_phase = 0
is_listening = False


# ============================================================
# SAFE UI UPDATE
# ============================================================

def ui_status(status):

    def update():
        status_var.set(status)

        if status == "LISTENING":
            status_label.config(fg=CYAN)

        elif status == "THINKING":
            status_label.config(fg=PURPLE)

        elif status == "SPEAKING":
            status_label.config(fg=GREEN)

        else:
            status_label.config(fg=MUTED)

    root.after(0, update)


def ui_response(text):

    root.after(
        0,
        lambda: response_var.set(text)
    )


# ============================================================
# SPEAK
# ============================================================

def speak(text):

    def voice():

        try:

            ui_status("SPEAKING")

            engine.say(text)
            engine.runAndWait()

        except Exception:
            pass

        ui_status("READY")

    threading.Thread(
        target=voice,
        daemon=True
    ).start()


def aqua_reply(text):

    ui_response(text)
    speak(text)


# ============================================================
# ORB ANIMATION
# ============================================================

def animate_orb():

    global orb_phase

    orb_phase += 1

    canvas.delete("orb")

    pulse = int(
        6 + 5 * math.sin(
            orb_phase / 8
        )
    )

    x = 450
    y = 295

    # Outer rings
    for i in range(5):

        size = 85 + pulse + i * 17

        canvas.create_oval(
            x - size,
            y - size,
            x + size,
            y + size,
            outline=(
                "#0B2639"
                if i > 1
                else "#10425A"
            ),
            width=2,
            tags="orb"
        )

    # Main orb
    size = 62 + pulse

    canvas.create_oval(
        x - size,
        y - size,
        x + size,
        y + size,
        fill="#071C2C",
        outline=CYAN,
        width=3,
        tags="orb"
    )

    # Core
    inner = 27 + int(
        pulse / 2
    )

    canvas.create_oval(
        x - inner,
        y - inner,
        x + inner,
        y + inner,
        fill=CYAN,
        outline="",
        tags="orb"
    )

    canvas.create_text(
        x,
        y,
        text="A",
        fill=BG,
        font=("Segoe UI", 25, "bold"),
        tags="orb"
    )

    root.after(
        40,
        animate_orb
    )


# ============================================================
# LISTEN
# ============================================================

def start_listening():

    global is_listening

    if is_listening:
        return

    threading.Thread(
        target=listen,
        daemon=True
    ).start()


def listen():

    global is_listening

    is_listening = True

    recognizer = sr.Recognizer()

    try:

        ui_status("LISTENING")
        ui_response("Listening...")

        with sr.Microphone() as source:

            recognizer.adjust_for_ambient_noise(
                source,
                duration=0.5
            )

            audio = recognizer.listen(
                source,
                timeout=7,
                phrase_time_limit=12
            )

        ui_status("THINKING")
        ui_response("Understanding...")

        command = recognizer.recognize_google(
            audio,
            language="en-IN"
        )

        process_command(
            command.lower().strip()
        )

    except sr.WaitTimeoutError:

        aqua_reply(
            "I didn't hear anything."
        )

    except sr.UnknownValueError:

        aqua_reply(
            "I couldn't understand that."
        )

    except sr.RequestError:

        aqua_reply(
            "Speech recognition is unavailable."
        )

    except Exception as error:

        print("VOICE ERROR:", error)

        aqua_reply(
            "Something went wrong."
        )

    finally:

        is_listening = False


# ============================================================
# OPEN WEBSITE
# ============================================================

def open_website(command):

    websites = {

        "youtube": "https://www.youtube.com",

        "google": "https://www.google.com",

        "gmail": "https://mail.google.com",

        "github": "https://github.com",

        "instagram": "https://www.instagram.com",

        "facebook": "https://www.facebook.com",

        "whatsapp": "https://web.whatsapp.com",

        "chatgpt": "https://chatgpt.com",

        "linkedin": "https://www.linkedin.com",

        "amazon": "https://www.amazon.in"
    }

    for name, url in websites.items():

        if (
            f"open {name}" in command
            or command == name
        ):

            webbrowser.open(url)

            aqua_reply(
                f"Opening {name}."
            )

            return True

    return False


# ============================================================
# SEARCH WEB
# ============================================================

def search_google(command):

    patterns = [
        "search google for",
        "search google",
        "google search for",
        "google search",
        "search for",
        "search"
    ]

    query = command

    for pattern in patterns:

        if query.startswith(pattern):

            query = query[
                len(pattern):
            ].strip()

            break

    if not query:

        aqua_reply(
            "What should I search for?"
        )

        return True

    url = (
        "https://www.google.com/search?q="
        + urllib.parse.quote_plus(query)
    )

    webbrowser.open(url)

    aqua_reply(
        f"Searching Google for {query}."
    )

    return True


# ============================================================
# YOUTUBE
# ============================================================

def youtube_command(command):

    if command == "open youtube":

        webbrowser.open(
            "https://www.youtube.com"
        )

        aqua_reply(
            "Opening YouTube."
        )

        return True

    patterns = [
        "search youtube for",
        "youtube search for",
        "youtube search",
        "search youtube",
        "play on youtube",
        "play"
    ]

    query = command

    for pattern in patterns:

        if pattern in query:

            query = query.replace(
                pattern,
                ""
            )

    query = query.strip()

    if query:

        url = (
            "https://www.youtube.com/results?search_query="
            + urllib.parse.quote_plus(query)
        )

        webbrowser.open(url)

        aqua_reply(
            f"Searching YouTube for {query}."
        )

    else:

        webbrowser.open(
            "https://www.youtube.com"
        )

        aqua_reply(
            "Opening YouTube."
        )

    return True


# ============================================================
# WINDOWS APPLICATIONS
# ============================================================

def open_application(command):

    applications = {

        "notepad": "notepad.exe",

        "calculator": "calc.exe",

        "file explorer": "explorer.exe",

        "explorer": "explorer.exe"
    }

    # Chrome
    if (
        "chrome" in command
        or "google chrome" in command
    ):

        chrome_paths = [

            r"C:\Program Files\Google\Chrome\Application\chrome.exe",

            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
        ]

        for path in chrome_paths:

            if os.path.exists(path):

                subprocess.Popen(path)

                aqua_reply(
                    "Opening Chrome."
                )

                return True

        webbrowser.open(
            "https://www.google.com"
        )

        aqua_reply(
            "I couldn't find Chrome, so I opened Google."
        )

        return True

    for name, executable in applications.items():

        if name in command:

            try:

                subprocess.Popen(
                    executable
                )

                aqua_reply(
                    f"Opening {name}."
                )

                return True

            except Exception:

                aqua_reply(
                    f"I couldn't open {name}."
                )

                return True

    return False


# ============================================================
# OPEN FOLDERS
# ============================================================

def open_folder(command):

    home = os.path.expanduser("~")

    folders = {

        "downloads": "Downloads",

        "download folder": "Downloads",

        "desktop": "Desktop",

        "desktop folder": "Desktop",

        "documents": "Documents",

        "document folder": "Documents",

        "pictures": "Pictures",

        "music": "Music",

        "videos": "Videos"
    }

    for name, folder in folders.items():

        if name in command:

            path = os.path.join(
                home,
                folder
            )

            if os.path.exists(path):

                os.startfile(path)

                aqua_reply(
                    f"Opening your {folder} folder."
                )

            else:

                aqua_reply(
                    f"I couldn't find your {folder} folder."
                )

            return True

    return False


# ============================================================
# WEATHER
# ============================================================

def weather(command):

    city = None

    patterns = [
        "weather in",
        "weather at",
        "temperature in",
        "temperature at"
    ]

    for pattern in patterns:

        if pattern in command:

            city = command.split(
                pattern,
                1
            )[1].strip()

            break

    if not city:
        city = "Amravati"

    try:

        url = (
            "https://wttr.in/"
            + urllib.parse.quote(city)
            + "?format=j1"
        )

        response = requests.get(
            url,
            timeout=8
        )

        data = response.json()

        current = data[
            "current_condition"
        ][0]

        temp = current["temp_C"]
        feels = current["FeelsLikeC"]
        humidity = current["humidity"]

        condition = current[
            "weatherDesc"
        ][0]["value"]

        answer = (
            f"In {city}, it is {temp} degrees "
            f"Celsius with {condition}. "
            f"It feels like {feels} degrees "
            f"and humidity is {humidity} percent."
        )

        aqua_reply(answer)

    except Exception:

        aqua_reply(
            "I couldn't get the weather right now."
        )


# ============================================================
# CALCULATOR
# ============================================================

def calculate(command):

    expression = command

    replacements = {

        "multiplied by": "*",

        "divided by": "/",

        "plus": "+",

        "minus": "-",

        "times": "*",

        "multiply": "*",

        "divide": "/",

        "modulo": "%",

        "mod": "%"
    }

    for word, symbol in replacements.items():

        expression = expression.replace(
            word,
            symbol
        )

    expression = expression.replace(
        "calculate",
        ""
    )

    expression = expression.replace(
        "what is",
        ""
    )

    expression = re.sub(
        r"[^0-9+\-*/().% ]",
        "",
        expression
    )

    try:

        result = eval(
            expression,
            {
                "__builtins__": None
            }
        )

        aqua_reply(
            f"The answer is {result}."
        )

    except Exception:

        aqua_reply(
            "I couldn't calculate that."
        )


# ============================================================
# NOTES
# ============================================================

def note_command(command):

    patterns = [

        "create a note",

        "make a note",

        "save a note",

        "take a note",

        "remember this",

        "write a note"
    ]

    for pattern in patterns:

        if pattern in command:

            note = command.split(
                pattern,
                1
            )[1].strip()

            if not note:

                aqua_reply(
                    "What should I write?"
                )

                return True

            try:

                with open(
                    NOTES_FILE,
                    "a",
                    encoding="utf-8"
                ) as file:

                    timestamp = datetime.datetime.now().strftime(
                        "%d-%m-%Y %I:%M %p"
                    )

                    file.write(
                        f"[{timestamp}] {note}\n"
                    )

                aqua_reply(
                    "Your note has been saved."
                )

            except Exception:

                aqua_reply(
                    "I couldn't save the note."
                )

            return True

    if (
        "read my notes" in command
        or "show my notes" in command
    ):

        try:

            if not os.path.exists(
                NOTES_FILE
            ):

                aqua_reply(
                    "You don't have any notes yet."
                )

                return True

            with open(
                NOTES_FILE,
                "r",
                encoding="utf-8"
            ) as file:

                notes = file.read().strip()

            if notes:

                # Read last few notes
                lines = notes.splitlines()
                recent = lines[-5:]

                text = "Here are your recent notes. "

                for line in recent:
                    text += line + " "

                aqua_reply(text)

            else:

                aqua_reply(
                    "You don't have any notes yet."
                )

        except Exception:

            aqua_reply(
                "I couldn't read your notes."
            )

        return True

    return False


# ============================================================
# INFORMATION
# ============================================================

def information(command):

    patterns = [

        "who is",

        "what is",

        "tell me about",

        "explain"
    ]

    query = command

    for pattern in patterns:

        if query.startswith(pattern):

            query = query[
                len(pattern):
            ].strip()

            break

    if not query:

        aqua_reply(
            "What would you like to know?"
        )

        return

    try:

        wikipedia.set_lang("en")

        result = wikipedia.summary(
            query,
            sentences=2
        )

        aqua_reply(
            result
        )

    except Exception:

        # If Wikipedia fails, Google it
        url = (
            "https://www.google.com/search?q="
            + urllib.parse.quote_plus(query)
        )

        webbrowser.open(url)

        aqua_reply(
            f"I couldn't get a direct answer, so I searched Google for {query}."
        )


# ============================================================
# SYSTEM INFORMATION
# ============================================================

def system_information(command):

    if (
        "battery" in command
        or "battery level" in command
    ):

        battery = psutil.sensors_battery()

        if battery:

            percent = battery.percent

            if battery.power_plugged:
                state = "and it is charging."
            else:
                state = "and it is not charging."

            aqua_reply(
                f"Your battery is at {percent} percent {state}"
            )

        else:

            aqua_reply(
                "I couldn't read the battery information."
            )

        return True

    if (
        "ram" in command
        or "memory usage" in command
        or "memory" in command
    ):

        memory = psutil.virtual_memory()

        used = round(
            memory.percent,
            1
        )

        aqua_reply(
            f"Your memory usage is {used} percent."
        )

        return True

    if (
        "cpu" in command
        or "processor" in command
    ):

        cpu = psutil.cpu_percent(
            interval=1
        )

        aqua_reply(
            f"Current CPU usage is {cpu} percent."
        )

        return True

    if (
        "system information" in command
        or "computer information" in command
        or "my pc information" in command
    ):

        system = platform.system()
        version = platform.version()
        machine = platform.machine()

        aqua_reply(
            f"You are using {system}. "
            f"System version is {version}. "
            f"Architecture is {machine}."
        )

        return True

    return False


# ============================================================
# FILE SEARCH
# ============================================================

def search_files(command):

    patterns = [
        "find file",
        "search file",
        "find folder",
        "search folder"
    ]

    query = None

    for pattern in patterns:

        if pattern in command:

            query = command.split(
                pattern,
                1
            )[1].strip()

            break

    if not query:
        return False

    locations = [

        os.path.expanduser(
            "~/Desktop"
        ),

        os.path.expanduser(
            "~/Documents"
        ),

        os.path.expanduser(
            "~/Downloads"
        )
    ]

    found = []

    for location in locations:

        if not os.path.exists(location):
            continue

        try:

            for root_dir, dirs, files in os.walk(
                location
            ):

                for filename in files:

                    if query.lower() in filename.lower():

                        found.append(
                            os.path.join(
                                root_dir,
                                filename
                            )
                        )

                        if len(found) >= 5:
                            break

                if len(found) >= 5:
                    break

        except Exception:
            continue

        if len(found) >= 5:
            break

    if found:

        first = found[0]

        aqua_reply(
            f"I found {len(found)} matching files. "
            f"The first one is {os.path.basename(first)}."
        )

    else:

        aqua_reply(
            f"I couldn't find a file named {query}."
        )

    return True


# ============================================================
# SYSTEM COMMANDS
# ============================================================

def system_command(command):

    # Shutdown
    if (
        "shutdown computer" in command
        or "shut down computer" in command
        or "turn off computer" in command
    ):

        aqua_reply(
            "Shutdown is a sensitive action. "
            "Please confirm by saying confirm shutdown."
        )

        pending_action["type"] = "shutdown"

        return True

    # Restart
    if (
        "restart computer" in command
        or "restart pc" in command
    ):

        aqua_reply(
            "Restart is a sensitive action. "
            "Please confirm by saying confirm restart."
        )

        pending_action["type"] = "restart"

        return True

    # Confirm shutdown
    if "confirm shutdown" in command:

        if pending_action.get("type") == "shutdown":

            aqua_reply(
                "Shutting down the computer."
            )

            time.sleep(2)

            os.system(
                "shutdown /s /t 5"
            )

            pending_action["type"] = None

            return True

    # Confirm restart
    if "confirm restart" in command:

        if pending_action.get("type") == "restart":

            aqua_reply(
                "Restarting the computer."
            )

            time.sleep(2)

            os.system(
                "shutdown /r /t 5"
            )

            pending_action["type"] = None

            return True

    return False


pending_action = {
    "type": None
}


# ============================================================
# COMMAND PROCESSOR
# ============================================================

def process_command(command):

    print(
        "COMMAND:",
        command
    )

    if not command:
        return

    # ---------------- EXIT ----------------

    if any(
        word in command
        for word in [
            "close aqua",
            "exit aqua",
            "quit aqua",
            "stop aqua",
            "goodbye"
        ]
    ):

        aqua_reply(
            "Goodbye. See you soon."
        )

        root.after(
            1800,
            root.destroy
        )

        return

    # ---------------- SYSTEM ----------------

    if system_command(command):
        return

    # ---------------- GREETING ----------------

    if command in [
        "hi",
        "hello",
        "hey",
        "hey aqua"
    ]:

        aqua_reply(
            "Hello. I'm Aqua. How can I help you?"
        )

        return

    if "how are you" in command:

        aqua_reply(
            "I'm doing great and ready to help."
        )

        return

    if "your name" in command:

        aqua_reply(
            "My name is Aqua, your AI personal assistant."
        )

        return

    if "who are you" in command:

        aqua_reply(
            "I'm Aqua, your AI personal assistant."
        )

        return

    if (
        "thank you" in command
        or "thanks" in command
    ):

        aqua_reply(
            "You're welcome."
        )

        return

    # ---------------- TIME ----------------

    if (
        "what time" in command
        or "current time" in command
        or command == "time"
    ):

        now = datetime.datetime.now()

        aqua_reply(
            "The current time is "
            + now.strftime("%I:%M %p")
            + "."
        )

        return

    # ---------------- DATE ----------------

    if (
        "what date" in command
        or "today's date" in command
        or command == "date"
        or "what day is it" in command
    ):

        now = datetime.datetime.now()

        aqua_reply(
            "Today is "
            + now.strftime("%A, %d %B %Y")
            + "."
        )

        return

    # ---------------- WEBSITE ----------------

    if open_website(command):
        return

    # ---------------- YOUTUBE ----------------

    if "youtube" in command:

        youtube_command(command)

        return

    # ---------------- WEATHER ----------------

    if (
        "weather" in command
        or "temperature in" in command
        or "temperature at" in command
    ):

        weather(command)

        return

    # ---------------- NOTES ----------------

    if note_command(command):
        return

    # ---------------- CALCULATOR ----------------

    if (
        command.startswith("calculate")
        or "divided by" in command
        or "multiplied by" in command
        or "plus" in command
        or "minus" in command
        or "times" in command
    ):

        calculate(command)

        return

    # ---------------- SYSTEM INFO ----------------

    if system_information(command):
        return

    # ---------------- FILE SEARCH ----------------

    if search_files(command):
        return

    # ---------------- FOLDERS ----------------

    if (
        "open downloads" in command
        or "open desktop" in command
        or "open documents" in command
        or "open pictures" in command
        or "open music" in command
        or "open videos" in command
    ):

        if open_folder(command):
            return

    # ---------------- APPS ----------------

    if (
        "open chrome" in command
        or "open google chrome" in command
        or "open notepad" in command
        or "open calculator" in command
        or "open file explorer" in command
        or "open explorer" in command
    ):

        if open_application(command):
            return

    # ---------------- GOOGLE SEARCH ----------------

    if (
        command.startswith("search")
        or "google search" in command
        or "search google" in command
    ):

        search_google(command)

        return

    # ---------------- KNOWLEDGE ----------------

    if (
        command.startswith("who is")
        or command.startswith("what is")
        or command.startswith("tell me about")
        or command.startswith("explain")
    ):

        information(command)

        return

    # ---------------- UNKNOWN ----------------

    aqua_reply(
        "I don't have that action yet. "
        "You can ask me to open apps, search the web, "
        "use YouTube, manage notes, check weather, "
        "calculate, find files, or control basic system functions."
    )


# ============================================================
# GUI
# ============================================================

canvas = tk.Canvas(
    root,
    bg=BG,
    highlightthickness=0
)

canvas.pack(
    fill="both",
    expand=True
)


# ============================================================
# BRAND
# ============================================================

canvas.create_text(
    450,
    55,
    text="A Q U A",
    fill=TEXT,
    font=("Segoe UI", 28, "bold")
)

canvas.create_text(
    450,
    88,
    text="AI PERSONAL ASSISTANT",
    fill=MUTED,
    font=("Segoe UI", 9, "bold")
)


# ============================================================
# STATUS
# ============================================================

status_label = tk.Label(
    root,
    textvariable=status_var,
    font=("Segoe UI", 10, "bold"),
    fg=MUTED,
    bg=BG
)

status_label.place(
    relx=0.5,
    rely=0.72,
    anchor="center"
)


# ============================================================
# RESPONSE
# ============================================================

response_label = tk.Label(
    root,
    textvariable=response_var,
    font=("Segoe UI", 11),
    fg=TEXT,
    bg=BG,
    wraplength=650,
    justify="center"
)

response_label.place(
    relx=0.5,
    rely=0.77,
    anchor="center"
)


# ============================================================
# HINT
# ============================================================

hint_label = tk.Label(
    root,
    text="Click anywhere or press SPACE to talk",
    font=("Segoe UI", 9),
    fg=MUTED,
    bg=BG
)

hint_label.place(
    relx=0.5,
    rely=0.90,
    anchor="center"
)


# ============================================================
# CLICK TO TALK
# ============================================================

root.bind(
    "<Button-1>",
    lambda event: start_listening()
)


# ============================================================
# SPACE TO TALK
# ============================================================

root.bind(
    "<space>",
    lambda event: start_listening()
)


# ============================================================
# START ANIMATION
# ============================================================

animate_orb()


# ============================================================
# START AQUA
# ============================================================

root.mainloop()