import datetime
import speech_recognition as sr
import pyttsx3
import webbrowser
import wikipedia
import sys
import time
# import wolframalpha
import re
import requests
import os
import random
import json
import pickle
import numpy as np
import nltk
import asyncio
from nltk import WordNetLemmatizer
from tensorflow.keras.models import load_model

async def main():
    # AI importation and function
    lemmatizer = WordNetLemmatizer()
    intents = json.loads(open('./aitools/intents.json').read())

    words = pickle.load(open('./aitools/words.pkl', 'rb'))
    classes = pickle.load(open('./aitools/classes.pkl', 'rb'))
    model = load_model('./aitools/sam_modelv2.keras')

    def clean_up_sentence(sentence):
        sentence_words = nltk.word_tokenize(sentence)
        sentence_words = [lemmatizer.lemmatize(word) for word in sentence_words]

        return sentence_words

    def bag_of_words(sentence):
        sentence_words = clean_up_sentence(sentence=sentence)
        bag = [0] * len(words)

        for w in sentence_words:
            for i, word in enumerate(words):
                if word == w:
                    bag[i] = 1

        return np.array(bag)

    def predict_class(sentence):
        bag = bag_of_words(sentence=sentence)
        result = model.predict(np.array([bag]))[0]
        ERROR_THRESHOLD = 0.25
        results = [[i, r] for i, r, in enumerate(result) if r > ERROR_THRESHOLD]

        results.sort(key=lambda x: x[1], reverse=True)
        return_list = []

        for r in results:
            return_list.append({'intent': classes[r[0]], 'probability': str(r[1])})

        # print(return_list)
        
        return return_list

    def get_response(intents_list, intents_json):
        tag = intents_list[0]['intent']
        list_of_intents = intents_json['intents']
        for i in list_of_intents:
            if i['tag'] == tag:
                result = random.choice(i['responses'])
                break
        return result

    # SAM code start
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

        with sr.Microphone() as source:
            listener.pause_threshold = 1.25
            input_speech = listener.listen(source=source)

        try:
            query = listener.recognize_google(input_speech, language='en_us')
            if 'sam' not in query.lower():
                parse_command()
            print(f'You said: {query.lower()}\n')
        except Exception as e:
            # err = f'You are bad at giving me directions, look at this: {e}'
            # speak(err)
            return 'None'
        
        return query.lower()
    
    async def set_timer():
        speak('How long should I set the timer for? ')
        print('Ex. "sam 15 minutes", or "sam 1 hour"')

        allowed_units = ['second', 'seconds', 'minute', 'minutes', 'hour', 'hours']

        response = None
        timer_duration = 0  # Default value

        while True:
            response = parse_command().lower().split()
            response.pop(0)  # 'sam'
            if len(response) != 2 or response[1] not in allowed_units:
                speak('Sorry, I couldn\'t understand the time format. Try again...')
                continue
            else:
                break

        val = int(response[0])
        time_unit = response[1]

        if time_unit == 'minute' or time_unit == 'minutes':
            timer_duration = val * 60  # Convert minutes to seconds
        elif time_unit == 'hour' or time_unit == 'hours':
            timer_duration = val * 3600  # Convert hours to seconds

        speak(f'Setting a timer for {val} {time_unit}')
        await asyncio.sleep(timer_duration)

    def get_stock():
        speak('What stock do you want to find information about?')
        print('Example: "sam MSTR", or "sam AAPL"... (Enunciate clearly)')

        response = None

        while True:
            response = parse_command().lower().split()
            response.pop(0)  # 'sam'
            if len(response) == 1 or len(response) == 4:
                if len(response) == 4:
                    response[0] = ''.join(response)
                    print(response[0])
                response = requests.get(f"http://127.0.0.1:8000/finance/stock/{response[0].upper()}")
                if response.status_code == 200:
                    stock_data = response.json()
                    name = stock_data.get('name')
                    symbol = stock_data.get('stock_symbol')
                    sector = stock_data.get('sector')
                    current_price = stock_data.get('current_price')
                    marcap = stock_data.get('market_cap')
                    desc = stock_data.get('description')
                    print(f'{symbol}\n')
                    speak(f'{name} is a {sector} firm with a stock price of ${current_price} and market cap of ${marcap}')
                    print(desc)
                    break
                else:
                    speak("Couldn't find the stock")
            else:
                speak('Ensure your response is in the format below:')
                print('"MSFT"')
                print(f"Your response: {response}, ({len(response)} chars). Try again...")
                continue

    def scrape_stock():
        print('(Web scraping can take a moment to complete)')
        speak('What stock do you want to scrape?')
        print('Example: "sam MSTR", or "sam AAPL"... (Enunciate clearly)')

        response = None

        while True:
            response = parse_command().lower().split()
            response.pop(0)  # 'sam'
            if len(response) == 1 or len(response) == 4:
                if len(response) == 4:
                    response[0] = ''.join(response)
                    print(response[0])
                response = requests.post(f"http://127.0.0.1:8000/finance/run-scraper/{response[0].upper()}")
                if response.status_code == 200:
                    speak(f"Stock scraped successfully")
                    break
                else:
                    speak("Error scraping the stock")
                    print("Yahoo finance doesn't like bots, so try again")
            else:
                speak('Ensure your response is in the format below:')
                print('"MSFT"')
                print(f"Your response: {response}, ({len(response)} chars). Try again...")
                continue

    def weather_full():
        speak('Where do you want weather info from?')
        print('Example: "sam New York", or "sam Savannah Georgia"...')

        while True:
            response = parse_command().lower().split()
            response.pop(0)  # 'sam'

            if len(response) > 0:
                location = ' '.join(response)
                print('Location searched:', location)
                
                response = requests.get(f"http://127.0.0.1:8000/weather/currentfor/{location}")
                
                if response.status_code == 200:
                    weather_data = response.json()
                    
                    # Accessing each attribute
                    city_name = weather_data["name"]
                    region = weather_data["region"]
                    country = weather_data["country"]
                    temperature_fahrenheit = weather_data["temp_f"]
                    is_day = weather_data["is_day"]
                    condition = weather_data["condition"]
                    precipitation = weather_data["precip"]
                    humidity = weather_data["humidity"]

                    # Printing the values
                    print("City:", city_name)
                    print("Region:", region)
                    print("Country:", country)
                    print("Temperature (Fahrenheit):", temperature_fahrenheit)
                    print("Is Day:", is_day)
                    print("Condition:", condition)
                    print("Precipitation:", precipitation)
                    print("Humidity:", humidity)
                    
                    break
                else:
                    speak("Error retrieving the weather")
            else:
                speak('Ensure your response is in the format below:')
                print('Example: "sam New York", or "sam Savannah Georgia"...')
                continue

    async def route_sam_function(query=None, intent=None):
        if intent == 'goodbyes':
            speak('Shutting down...')
            sys.exit(0)

        # sam voice request
        elif query[0] == 'say': 
            if 'hello' in query:
                speak('Hello!')
            else:
                query.pop(0)
                speech = ' '.join(query)
                speak(f'sure {name}, {speech}')

        # clear terminal
        elif intent == 'clear': 
            speak("clearing")
            os.system('cls')

        # stopwatch / timer
        elif intent == 'timer': 
            await set_timer()
            speak("Timer has finished")

        # finance
        elif intent == 'getstock':
            get_stock()

        elif intent == 'scrapestock':
            scrape_stock()

        elif intent == 'weatherfull':
            weather_full()

        elif intent == 'weathershort':
            scrape_stock()

        elif intent == 'help':
            speak('Displaying help text...')
            os.system('cls')
            display_help_file('./aitools/help.txt')
        
        # spotify api current song request
        elif intent == 'song':
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

        elif intent == 'favorites':
            os.system('cls')
            response = requests.get("http://127.0.0.1:8000/spotify/favorites")
            if response.status_code == 200:
                speak('Here are your favorited songs:')
                print('\t(id): (title) by (artist)')
                favorites = response.json()  # Convert the JSON response to a Python list of dictionaries
                for song in favorites:
                    print(f"\t{song["id"]}: {song['name']} by {song["artist"]}")
            else:
                print("Failed to fetch your favorite songs.")
        elif intent == 'favorite': # add to favorites
            response = requests.post("http://127.0.0.1:8000/spotify/favorite")
            if response.status_code == 204:
                speak('Added to favorites')
            else:
                print("Failed to add to favorites.")
        
        elif intent == 'queueid':
            while True:
                speak("What is the id of the song?")
                print('Ex. "sam 5"')
                response = parse_command().lower().split()
                if len(response) != 2:
                    print("Use the format above (sam 1)")
                    continue
                else:
                    response.pop(0)  # 'sam'
                    print(response)
                    if response[0] == 'one':
                        response[0] = 1
                    response = requests.post(f"http://127.0.0.1:8000/spotify/queue-id/{response[0]}")
                    if response.status_code == 204:
                        speak('Queued')
                        break
                    else:
                        print("Failed to queue.")
        elif intent == 'queueartist':
            while True:
                speak("What artist?")
                print('Ex. "sam Future"')
                response = parse_command().lower().split()
                if len(response) < 2:
                    print("Use the format above (sam Future)")
                    continue
                else:
                    response.pop(0)  # 'sam'
                    print(response)
                    response = requests.post(f"http://127.0.0.1:8000/spotify/queue-artist/{' '.join(response)}")
                    if response.status_code == 204:
                        speak('Queued')
                        break
                    else:
                        print("Failed to queue.")

        elif intent == 'play':
            response = requests.put("http://127.0.0.1:8000/spotify/play")
            if response.status_code == 204:
                speak('Playing')
                print("Playback started successfully.")
            else:
                print("Failed to start playback.")
        elif intent == 'pause':
            response = requests.put("http://127.0.0.1:8000/spotify/pause")
            if response.status_code == 204:
                speak('pausing')
                print("Playback paused successfully.")
            else:
                print("Failed to pause playback.")
        elif intent == 'skip':
            response = requests.post("http://127.0.0.1:8000/spotify/skip")
            if response.status_code == 204:
                speak('skipping')
                print("Playback skipped successfully.")
            else:
                print("Failed to skip playback.")
        elif intent == 'rewind':
            response = requests.post("http://127.0.0.1:8000/spotify/rewind")
            if response.status_code == 204:
                speak('rewinding')
                print("Playback reversed successfully.")
            else:
                print("Failed to reverse playback.")

        elif intent == 'volup':
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

        elif intent == 'voldown':
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

        elif len(query) >= 3:
            # navigation request
            if query[0] == 'navigate' or (query[0] == 'go' and query[1] == 'to'):
                query.pop(0)  # Remove 'navigate' or 'go'
                query.pop(0)  # Remove 'to'

                if len(query) > 1 and query[0] == 'and' and query[1] == 'search':
                    query.pop(0)  # Remove 'and'
                    query.pop(0)  # Remove 'search'
                    if query[0] == 'for':
                        query.pop(0)  # Remove 'for'
                    site = query.pop(0)  # Get the site
                    search = '+'.join(query)  # Get the search query
                    url = f'https://www.{site}.com/search?q={search}'
                    webbrowser.open(url)
                else:
                    speech = ' '.join(query)
                    url = 'https://' + ''.join(query) + '.com'
                    webbrowser.open(url)
                    speak(f"Ok, here's {speech}")


            # wikipedia query
            elif query[0] == 'search' and query[1] == 'wikipedia' or query[1] == 'wiki':
                query.pop(0) # search
                query.pop(0) # wikipedia
                query.pop(0) # for
                search = ' '.join(query[0:])
                os.system('cls')
                search_wiki(search=search)

        # default handling
        else:
            speak("I heard you say my name, but didn't hear a keyword after. To refer to the SAM documentation say, sam help!")

    # user loop

    print('Currently listening to everything you are saying! "sam help" for menu')

    while True:
        # message structure: "computer (act word), go to google.com (request) (2 sec silence stops)"
        query = parse_command().lower().split()
        class_query = ' '.join(query)
        ints = predict_class(class_query)
        if ints == []:
            pass
        else:
            dict = ints[0]
            intent_value = dict['intent']
            prob = float(dict['probability'])

            if prob < .8:
                # speak("I'm not quite sure what you mean by that")
                pass
            else:

                # print(intent_value)

                if query[0] == activation_word:
                    query.pop(0)
                else:
                    continue
                
                await route_sam_function(query=query, intent=intent_value)

if __name__ == '__main__':
    asyncio.run(main())