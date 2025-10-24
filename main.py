import pyttsx3
import speech_recognition as sr
import webbrowser
import datetime
import subprocess
import os
import json
import threading
import time
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from openai import OpenAI
from config import apikey


# Global variables for reminders
reminders = []
notes_folder = "eight_notes"

# Speech recognition settings
RECOGNITION_TIMEOUT = 5  # seconds to wait for speech to start
PHRASE_TIME_LIMIT = 10   # max seconds for a single phrase
MAX_FAILED_ATTEMPTS = 3  # stop after this many consecutive failures
AMBIENT_NOISE_DURATION = 1  # seconds to adjust for ambient noise

# Voice settings
VOICE_RATE = 150        # Speed of speech (default: 200, lower = slower)
VOICE_VOLUME = 1.0      # Volume (0.0 to 1.0)
VOICE_PITCH = 50        # Pitch/tone (0-100, lower = deeper/heavier)

# Ensure notes folder exists
if not os.path.exists(notes_folder):
    os.makedirs(notes_folder)

def ai(prompt):
    client = OpenAI(api_key=apikey)

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo-16k",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=1,
            max_tokens=256,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        result = response.choices[0].message.content
        print(result)
        return result
    except Exception as e:
        print("Error with AI request:", e)
        return None

# Reminder/Alarm System
def set_reminder(reminder_text, minutes):
    """Set a reminder that will alert after specified minutes"""
    def reminder_thread():
        time.sleep(minutes * 60)
        say(f"Reminder: {reminder_text}")
        print(f"REMINDER: {reminder_text}")

    thread = threading.Thread(target=reminder_thread)
    thread.daemon = True
    thread.start()
    reminders.append({"text": reminder_text, "minutes": minutes, "time": datetime.datetime.now()})

def parse_reminder_command(text):
    """Parse reminder command from text"""
    # Patterns: "remind me to [task] in [X] minutes"
    # "set reminder [task] in [X] minutes"
    pattern = r"(?:remind me to|reminder|set reminder)(.*?)(?:in|after)\s*(\d+)\s*(?:minute|minutes|min)"
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        task = match.group(1).strip()
        minutes = int(match.group(2))
        return task, minutes
    return None, None

# Note-taking System
def take_note(note_content):
    """Save a note to a text file"""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(notes_folder, f"note_{timestamp}.txt")

    with open(filename, 'w') as f:
        f.write(f"Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Note: {note_content}\n")

    return filename

def list_notes():
    """List all saved notes"""
    if os.path.exists(notes_folder):
        notes = os.listdir(notes_folder)
        return notes
    return []

# Email System
def send_email(to_email, subject, body, from_email=None, password=None):
    """Send an email using SMTP"""
    try:
        # You'll need to configure these in config.py
        if from_email is None or password is None:
            print("Email credentials not configured. Please set EMAIL and PASSWORD in config.py")
            return False

        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        # Using Gmail SMTP
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(from_email, password)
        server.send_message(msg)
        server.quit()

        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

# Calculator System
def calculate(expression):
    """Safely evaluate mathematical expressions"""
    try:
        # Remove any non-mathematical characters
        safe_expr = re.sub(r'[^0-9+\-*/().\s]', '', expression)
        result = eval(safe_expr)
        return result
    except Exception as e:
        print(f"Calculation error: {e}")
        return None

def parse_calculation(text):
    """Extract calculation from voice command"""
    text_original = text
    text_lower = text.lower()

    # Convert spoken words to symbols FIRST
    text_converted = text_lower
    text_converted = text_converted.replace("plus", "+")
    text_converted = text_converted.replace("add", "+")
    text_converted = text_converted.replace("minus", "-")
    text_converted = text_converted.replace("subtract", "-")
    text_converted = text_converted.replace("times", "*")
    text_converted = text_converted.replace("multiplied by", "*")
    text_converted = text_converted.replace("multiply", "*")
    text_converted = text_converted.replace("divided by", "/")
    text_converted = text_converted.replace("divide", "/")
    # Handle 'x' as multiplication (like "5 x 3")
    text_converted = re.sub(r'\b(\d+)\s*x\s*(\d+)\b', r'\1 * \2', text_converted)

    # Patterns: "calculate [expression]", "what is [expression]"
    patterns = [
        r"calculate\s+(.*)",
        r"what is\s+(.*)",
        r"solve\s+(.*)"
    ]

    for pattern in patterns:
        match = re.search(pattern, text_converted, re.IGNORECASE)
        if match:
            expr = match.group(1).strip()
            return expr

    # Check if the converted text is a math expression
    if re.match(r'^[\d\s+\-*/().]+$', text_converted.strip()):
        return text_converted.strip()

    # Check if original text is already a math expression (like "5 + 5")
    if re.match(r'^[\d\s+\-*/().]+$', text_original.strip()):
        return text_original.strip()

    return None

# File Operations
def create_file(filename, content=""):
    """Create a new file"""
    try:
        with open(filename, 'w') as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"Error creating file: {e}")
        return False

def delete_file(filename):
    """Delete a file"""
    try:
        if os.path.exists(filename):
            os.remove(filename)
            return True
        else:
            print(f"File {filename} does not exist")
            return False
    except Exception as e:
        print(f"Error deleting file: {e}")
        return False

def search_files(directory, pattern):
    """Search for files matching a pattern"""
    try:
        matches = []
        for root, dirs, files in os.walk(directory):
            for filename in files:
                if pattern.lower() in filename.lower():
                    matches.append(os.path.join(root, filename))
        return matches
    except Exception as e:
        print(f"Error searching files: {e}")
        return []

def list_files(directory="."):
    """List files in a directory"""
    try:
        return os.listdir(directory)
    except Exception as e:
        print(f"Error listing files: {e}")
        return []
def recognised_speech_from_microphone():
    """
    Improved speech recognition with configurable timeout and phrase limits
    Returns: tuple (text, error_type) where error_type is None on success
    """
    recognizer = sr.Recognizer()

    # Adjust recognizer settings for better performance
    recognizer.energy_threshold = 4000  # Adjust based on ambient noise
    recognizer.dynamic_energy_threshold = True
    recognizer.pause_threshold = 0.8  # seconds of silence to consider phrase complete

    try:
        microphone = sr.Microphone()
    except Exception as e:
        print(f"ERROR: Could not access microphone - {e}")
        return None, "microphone_error"

    with microphone as source:
        print("Listening... (speak now)")
        recognizer.adjust_for_ambient_noise(source, duration=AMBIENT_NOISE_DURATION)

        try:
            # Listen with timeout and phrase time limit
            audio = recognizer.listen(
                source,
                timeout=RECOGNITION_TIMEOUT,
                phrase_time_limit=PHRASE_TIME_LIMIT
            )
            print("Processing speech...")

            # Convert audio to text using Google Speech Recognition
            text = recognizer.recognize_google(audio)
            print(f"✓ You said: {text}")
            return text, None

        except sr.WaitTimeoutError:
            print("⏱ No speech detected (timeout)")
            return None, "timeout"

        except sr.UnknownValueError:
            print("❌ Could not understand audio")
            return None, "unknown"

        except sr.RequestError as e:
            print(f"❌ Speech recognition service error: {e}")
            return None, "service_error"

        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return None, "error"
def say(text):
    """Text-to-speech with customizable voice settings"""
    engine = pyttsx3.init()

    # Set voice properties for heavier/deeper voice
    engine.setProperty('rate', VOICE_RATE)      # Speed of speech
    engine.setProperty('volume', VOICE_VOLUME)  # Volume level

    # Try to set a male/deeper voice if available
    voices = engine.getProperty('voices')

    # Priority order for deeper male voices
    preferred_voices = ['david', 'mark', 'george']  # David is deepest on Windows

    male_voice_found = False
    for preferred in preferred_voices:
        for voice in voices:
            if preferred in voice.name.lower():
                engine.setProperty('voice', voice.id)
                male_voice_found = True
                break
        if male_voice_found:
            break

    # If no preferred voice found, use the first available (usually male on Windows)
    if not male_voice_found and len(voices) > 0:
        engine.setProperty('voice', voices[0].id)

    engine.say(text)
    engine.runAndWait()

if __name__ == "__main__":
    print("=" * 60)
    print("Hello I am Eight - Your Intelligent Productivity Assistant")
    print("=" * 60)

    # Check API key
    if not apikey or apikey.startswith("sk-HduWd") or len(apikey) < 20:
        print("\n⚠️  WARNING: Invalid or default API key detected!")
        print("AI features will not work. Please update your API key in config.py")
        print("Get your API key from: https://platform.openai.com/api-keys\n")

    say("Hello I am Eight, your intelligent productivity assistant")

    sites=[["youtube","https://www.youtube.com/"],["netflix","https://www.netflix.com/browse"],["google","https://www.google.co.in/"]]

    print("\nAvailable Commands:")
    print("- Open websites: 'open youtube', 'open google', etc.")
    print("- Time: 'what time is it'")
    print("- Reminders: 'remind me to [task] in [X] minutes'")
    print("- Notes: 'take a note [content]', 'list notes'")
    print("- Calculator: 'calculate [expression]' or 'what is [expression]'")
    print("- Files: 'list files', 'search file [name]', 'create file [name]'")
    print("- AI: Ask any question naturally")
    print("- Stop: 'stop' or 'exit'")
    print("=" * 60)
    print(f"\nSettings: Timeout={RECOGNITION_TIMEOUT}s, Max fails before auto-stop={MAX_FAILED_ATTEMPTS}")
    print("=" * 60 + "\n")

    failed_attempts = 0

    while True:
        recognise_text, error_type = recognised_speech_from_microphone()

        if recognise_text:  # Successfully recognized speech
            failed_attempts = 0  # Reset counter on success
            text_lower = recognise_text.lower()

            # Stop command
            if text_lower in ["stop", "exit", "quit", "goodbye"]:
                say("Goodbye! Have a great day!")
                break

            # Calculator - Check FIRST to avoid conflict with "time" keyword
            elif (any(word in text_lower for word in ["calculate", "solve", "plus", "minus", "times", "multiply", "divide", "add", "subtract"])
                  or re.match(r'^[\d\s+\-*/().]+$', recognise_text.strip())
                  or (any(op in recognise_text for op in ['+', '-', '*', '/']) and any(c.isdigit() for c in recognise_text))
                  or re.search(r'\d+\s*x\s*\d+', text_lower)):
                expr = parse_calculation(recognise_text)
                if expr:
                    result = calculate(expr)
                    if result is not None:
                        say(f"The answer is {result}")
                        print(f"Calculation: {expr} = {result}")
                    else:
                        say("I couldn't calculate that")
                else:
                    # If parse failed and it has "what is", pass to AI
                    if "what is" in text_lower and not any(op in text_lower for op in ["plus", "minus", "times", "multiply", "divide", "+", "-", "*", "/"]):
                        print(f"AI Query: {recognise_text}")
                        response = ai(prompt=recognise_text)
                        if response:
                            say(response)
                        else:
                            say("I'm having trouble connecting to AI services. Please check the API key in config.py")
                    else:
                        say("Please provide a calculation")

            # Open websites
            elif "open" in text_lower:
                for site in sites:
                    if f"open {site[0]}" in text_lower:
                        say(f"opening {site[0]}")
                        webbrowser.open(site[1])
                        break

            # Time - more specific check to avoid conflict with "times"
            elif ("what" in text_lower and "time" in text_lower) or "current time" in text_lower or text_lower.strip() == "time":
                hour = datetime.datetime.now().strftime("%H")
                minutes = datetime.datetime.now().strftime("%M")
                say(f"the time is {hour} hours and {minutes} minutes")
                print(f"Time: {hour}:{minutes}")

            # Date
            elif "date" in text_lower or "today" in text_lower:
                date = datetime.datetime.now().strftime("%B %d, %Y")
                say(f"Today is {date}")
                print(f"Date: {date}")

            # Reminders
            elif "remind" in text_lower or "reminder" in text_lower:
                task, minutes = parse_reminder_command(recognise_text)
                if task and minutes:
                    set_reminder(task, minutes)
                    say(f"Reminder set for {task} in {minutes} minutes")
                    print(f"✓ Reminder set: {task} in {minutes} minutes")
                else:
                    say("I couldn't understand the reminder. Please say 'remind me to [task] in [X] minutes'")

            # Notes
            elif "take a note" in text_lower or "make a note" in text_lower or "note this" in text_lower:
                # Extract note content
                patterns = [
                    r"take a note\s+(.*)",
                    r"make a note\s+(.*)",
                    r"note this\s+(.*)"
                ]
                note_content = None
                for pattern in patterns:
                    match = re.search(pattern, text_lower)
                    if match:
                        note_content = match.group(1).strip()
                        break

                if note_content:
                    filename = take_note(note_content)
                    say("Note saved successfully")
                    print(f"✓ Note saved: {filename}")
                else:
                    say("What would you like me to note?")

            elif "list notes" in text_lower or "show notes" in text_lower:
                notes = list_notes()
                if notes:
                    say(f"You have {len(notes)} notes")
                    print(f"\nYour notes ({len(notes)}):")
                    for note in notes[:5]:  # Show first 5
                        print(f"  - {note}")
                else:
                    say("You have no saved notes")
                    print("No notes found")

            # File Operations
            elif "list files" in text_lower:
                files = list_files(".")
                say(f"Found {len(files)} files in current directory")
                print(f"\nFiles in current directory ({len(files)}):")
                for f in files[:10]:  # Show first 10
                    print(f"  - {f}")

            elif "search file" in text_lower or "find file" in text_lower:
                pattern_match = re.search(r"(?:search|find) file\s+(.*)", text_lower)
                if pattern_match:
                    pattern = pattern_match.group(1).strip()
                    results = search_files(".", pattern)
                    if results:
                        say(f"Found {len(results)} matching files")
                        print(f"\nMatching files ({len(results)}):")
                        for r in results[:10]:
                            print(f"  - {r}")
                    else:
                        say("No matching files found")
                        print("No files found")

            elif "create file" in text_lower:
                match = re.search(r"create file\s+([\w\.]+)", text_lower)
                if match:
                    filename = match.group(1)
                    if create_file(filename):
                        say(f"File {filename} created successfully")
                        print(f"✓ Created: {filename}")
                    else:
                        say("Failed to create file")

            # PowerPoint
            elif "powerpoint" in text_lower:
                say("opening powerpoint")
                subprocess.Popen(r"C:\Program Files\Microsoft Office\root\Office16\POWERPNT.EXE")

            # Word
            elif "word" in text_lower and "open" in text_lower:
                say("opening microsoft word")
                subprocess.Popen(r"C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE")

            # Excel
            elif "excel" in text_lower and "open" in text_lower:
                say("opening microsoft excel")
                subprocess.Popen(r"C:\Program Files\Microsoft Office\root\Office16\EXCEL.EXE")

            # AI for everything else (general questions)
            else:
                print(f"AI Query: {recognise_text}")
                response = ai(prompt=recognise_text)
                if response:
                    say(response)
                else:
                    say("I'm having trouble connecting to AI services. Please check the API key in config.py")

        else:
            # Handle recognition failures
            failed_attempts += 1

            if error_type == "timeout":
                print(f"⚠️  Attempt {failed_attempts}/{MAX_FAILED_ATTEMPTS}: Waiting for speech...")
            elif error_type == "unknown":
                print(f"⚠️  Attempt {failed_attempts}/{MAX_FAILED_ATTEMPTS}: Could not understand")
            elif error_type == "service_error":
                print(f"⚠️  Attempt {failed_attempts}/{MAX_FAILED_ATTEMPTS}: Service connection issue")
                failed_attempts += 1  # Count service errors double
            elif error_type == "microphone_error":
                print("❌ Critical: Cannot access microphone!")
                say("Cannot access microphone. Exiting.")
                break

            # Check if we should stop
            if failed_attempts >= MAX_FAILED_ATTEMPTS:
                print(f"\n❌ Too many failed attempts ({failed_attempts}). Stopping Eight.")
                print("Tips:")
                print("  - Speak clearly and closer to the microphone")
                print("  - Check your internet connection (required for speech recognition)")
                print("  - Reduce background noise")
                say("Too many failed attempts. Goodbye!")
                break

            # Brief pause before next attempt
            time.sleep(0.5)