import pyttsx3
import speech_recognition as sr
import webbrowser
import datetime
import subprocess
import openai
from config import apikey


def ai(prompt):
    openai.api_key = apikey

    try:
        response = openai.ChatCompletion.create(
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
        print(response.choices[0].message["content"])
    except Exception as e:
        print("Error with AI request:", e)
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
    print("Hello I am Eight")
    say("Hello I am Eight")
    sites=[["youtube","https://www.youtube.com/"],["netflix","https://www.netflix.com/browse"],["google","https://www.google.co.in/"]]
    while True:
        recognise_text = recognised_speech_from_microphone()
        if recognise_text:  # if recognised text is not empty and none
            if recognise_text.lower()=="stop":
                say("command to stop has been initiated")
                break
            elif "open".lower() in recognise_text.lower():  # for checking which site to open
                for site in sites:
                 if f"open {site[0]}".lower() in recognise_text.lower():
                  say(f"opening {site[0]}")
                  webbrowser.open(site[1])
            elif "time".lower() in recognise_text.lower():
                 hour=datetime.datetime.now().strftime("%H")
                 minutes = datetime.datetime.now().strftime("%M")
                 say(f"the time is {hour} hours and {minutes} minutes")
                 print(f"the time is {hour} and {minutes} minutes")
            elif "powerpoint".lower() in recognise_text.lower():
                 say("opening powerpoint")
                 subprocess.call(r"C:\Program Files\Microsoft Office\root\Office16\POWERPNT.EXE")
            elif "using artificial intelligence".lower() in recognise_text.lower():
                  ai(prompt=recognise_text)
            else:
                print(f"{recognise_text}")
                say(recognise_text)
        else:
            print("Eight : no meaningfull text recognised")
            break