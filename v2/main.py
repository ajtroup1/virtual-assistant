import datetime
import speech_recognition as sr
import pyttsx3
import webbrowser
import wikipedia
import wolframalpha
import re

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

def parse_command():
    listener = sr.Recognizer()
    print('Currently listening to everything you are saying!')

    with sr.Microphone() as source:
        listener.pause_threshold = 2
        input_speech = listener.listen(source=source)

    try:
        print('...')
        query = listener.recognize_google(input_speech, language='en_us')
        print(f'input: {query}')
    except Exception as e:
        # err = f'You are bad at giving me directions, look at this: {e}'
        # speak(err)
        return 'None'
    
    return query.lower()

def route_sam_function(query=None):
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

    if len(query) >= 3:
        # navigation request
        if query[0] == 'navigate' and query[1] == 'to': 
            query.pop(0)
            query.pop(0)
            print(query)
            if query[1] == 'and' and query[2] == 'search': # google and search billboard top 100
                query.pop(1)
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