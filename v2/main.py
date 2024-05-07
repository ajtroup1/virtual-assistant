import datetime
import speech_recognition as sr
import pyttsx3
import webbrowser
import wikipedia
import wolframalpha
import re
import requests
import os

os.system('cls')

activation_word = 'sam'
name = 'adam'

# tts engine
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id) # 0=male, 1=female voice

def speak(text, rate=175):
    print(text)
    engine.setProperty('rate', rate)
    engine.say(text)
    engine.runAndWait()

def search_wiki(search=''): # wikipedia library sucks :(
    print(search)
    searchResults = wikipedia.search(search)
    if not searchResults:
        return 'No result received'
    try: 
        wikiPage = wikipedia.page(searchResults[0]) 
    except wikipedia.DisambiguationError as error:
        wikiPage = wikipedia.page(error.options[0])
    
    speak(f'pulling up the wiki for {wikiPage.title}')
    wikiSummary = str(wikiPage.summary)
    print(wikiSummary)

def display_help_file(file_path):
    try:
        with open(file_path, 'r') as file:
            file_contents = file.read()
            print(file_contents)
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")

def parse_command():
    listener = sr.Recognizer()
    print('Currently listening to everything you are saying!')

    with sr.Microphone() as source:
        listener.pause_threshold = 1.25
        input_speech = listener.listen(source=source)

    try:
        print('...')
        query = listener.recognize_google(input_speech, language='en_us')
        print(f'input: {query.lower()}')
    except Exception as e:
        # err = f'You are bad at giving me directions, look at this: {e}'
        # speak(err)
        return 'None'
    
    return query.lower()

def route_sam_function(query=None):
    print("Joined query:", ''.join(query))
    if query[0] == 'exit':
        speak('Goodbye')
        exit()

    # sam voice request
    if query[0] == 'say': 
        if 'hello' in query:
            speak('Hello!')
        else:
            query.pop(0)
            speech = ' '.join(query)
            speak(f'sure {name}, {speech}')

    # clear terminal
    elif query[0] == 'clear': 
        speak("yes sir, or ma'am")
        os.system('cls')
    
    # spotify api current song request
    elif ''.join(query) == 'whatsongisthis':
        response = requests.get("http://127.0.0.1:8000/spotify/current-song")
        if response.status_code == 200:
            song_data = response.json()
            title = song_data.get('title')
            artist = song_data.get('artist')
            if title and artist:
                speak(f"Currently listening to {title} by {artist}")
            else:
                speak("Title or artist not found in song data.")
        else:
            speak("Couldn't find the song")

    # spotify api volume up (the fun way)
    elif ''.join(query) == 'turnitup':
        response = requests.get("http://127.0.0.1:8000/spotify/get-device")
        if response.status_code == 200:
            song_data = response.json()
            vol = song_data.get('volume_percent')
            if vol > 75:
                vol = 100
            else:
                vol += 25
            response = requests.put(f"http://127.0.0.1:8000/spotify/set-volume/{vol}")
            if response.status_code == 204:
                speak("oh yeah, turning it up")
            else:
                speak("Failed to turn it up")
        else:
            speak("Couldn't find the song")

    # spotify api volume down (the fun way)
    elif ''.join(query) == 'turnitdown':
        response = requests.get("http://127.0.0.1:8000/spotify/get-device")
        if response.status_code == 200:
            song_data = response.json()
            vol = song_data.get('volume_percent')
            if vol < 25:
                vol = 0
            else:
                vol -= 25
            response = requests.put(f"http://127.0.0.1:8000/spotify/set-volume/{vol}")
            if response.status_code == 204:
                speak("shhhhh")
            else:
                speak("Failed to turn down")
        else:
            speak("Couldn't find the song")

    elif query[0] == 'help':
        speak('Displaying help text...')
        os.system('cls')
        display_help_file('help.txt')

    elif len(query) >= 3:
        # navigation request
        if query[0] == 'navigate' or query[0] == 'go' and query[1] == 'to': 
            query.pop(0)
            query.pop(0)
            print(query)
            if len(query) > 1:
                if query[1] == 'and' and query[2] == 'search': # google and search billboard top 100
                    query.pop(1)
                    query.pop(1)
                    if(query[1] == 'for'):
                        query.pop(1)
                    # google billboard top 100
                    site = query[0]
                    # billboard top 100
                    query.pop(0)
                    search = '+'.join(query)
                    # https://www.google.com/search?q=top+100+billboard&
                    url = f'https://www.{site}.com/search?q={search}'
                    print(url)
                    webbrowser.open(url)
            else:
                speech = ' '.join(query)
                url = 'https://' + ''.join(query) + '.com'
                webbrowser.open(url)
                speak(f"ok, here's {speech}")

        # wikipedia query
        elif query[0] == 'search' and query[1] == 'wikipedia':
            query.pop(0) # search
            query.pop(0) # wikipedia
            query.pop(0) # for
            search = ' '.join(query[0:])
            search_wiki(search=search)

    elif query[0] == 'spotify':
        query.pop(0)
    
        if query[0] == 'play':
            response = requests.put("http://127.0.0.1:8000/spotify/play")
            if response.status_code == 204:
                print("Playback started successfully.")
            else:
                print("Failed to start playback.")
        elif query[0] == 'pause':
            response = requests.put("http://127.0.0.1:8000/spotify/pause")
            if response.status_code == 204:
                print("Playback paused successfully.")
            else:
                print("Failed to pause playback.")
        elif query[0] == 'skip':
            response = requests.post("http://127.0.0.1:8000/spotify/skip")
            if response.status_code == 204:
                print("Playback skipped successfully.")
            else:
                print("Failed to pause playback.")

    # default handling
    else:
        speak("I heard you say my name, but didn't hear a keyword after. To refer to the SAM documentation say, help!")

# user loop
if __name__ == '__main__':
    # engine.say('Welcome, I am SAM, your virtual assistant. Just say, sam, to signify a query for me')
    # engine.runAndWait()

    while True:
        # message structure: "computer (act word), go to google.com (request) (2 sec silence stops)"
        query = parse_command().lower().split()
    
        if query[0] == activation_word:
            query.pop(0)
        else:
            continue
        
        route_sam_function(query=query)