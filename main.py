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
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    with microphone as source:
        print("Checking for ambient noises wait for 2s" )
        recognizer.adjust_for_ambient_noise(source, duration=2)

        try:
         audio = recognizer.listen(source, timeout=5)  # to recognize audio
         print("Recognizing...")
         text = recognizer.recognize_google(audio)   # audio is converted into text form
         print(f"You said: {text}")
         return text
        except sr.WaitTimeoutError:
         print("NO speech detected")
         return None
        except sr.RequestError:
         print("API was unreachable or unresponsive.")
         return None
        except Exception as e:
         print("some exception has occured from eight")
         return None
def say(text):
    engine = pyttsx3.init() # Initialize pyttsx3 engine
    engine.say(text)         # prepares text to be spoken
    engine.runAndWait()      # wait until text is spoken

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
    print("=" * 60 + "\n")

    while True:
        recognise_text = recognised_speech_from_microphone()
        if recognise_text:  # if recognised text is not empty and none
            text_lower = recognise_text.lower()

            # Stop command
            if text_lower in ["stop", "exit", "quit", "goodbye"]:
                say("Goodbye! Have a great day!")
                break

            # Calculator - Check FIRST to avoid conflict with "time" keyword
            elif (any(word in text_lower for word in ["calculate", "solve", "plus", "minus", "times", "multiply", "divide", "add", "subtract"])
                  or re.match(r'^[\d\s+\-*/().]+$', recognise_text.strip())
                  or (any(op in recognise_text for op in ['+', '-', '*', '/']) and any(c.isdigit() for c in recognise_text))):
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
            print("Eight: No speech detected. Listening again...")
            # Continue listening instead of breaking