import slack
import os
from flask import Flask, request, Response
from pathlib import Path
from dotenv import load_dotenv
from slackeventsapi import SlackEventAdapter
import requests
import json

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

app = Flask(__name__)

slack_event_adapter = SlackEventAdapter(os.environ['SIGNING_SECRET'], '/slack/events', app)
client = slack.WebClient(token=os.environ['SLACK_TOKEN'])
BOT_ID = client.api_call('auth.test')['user_id']

# return boot message when root of the domain as been accessed
@app.route('/')
def wakeup():
    return "Dyno Up and Running... :)"

# extract and process user message    
@slack_event_adapter.on('message')
def message(payload):
    event = payload.get('event',{})
    channel_id = event.get('channel')     
    user_id = event.get('user')
    input_text = event.get('text')

    if BOT_ID != user_id:
        # build API url
        url = 'http://api.openweathermap.org/data/2.5/weather?q=' + input_text + '&units=metric&appid=' + os.environ['WEATHER_KEY']
        response = requests.get(url)   

        # check if valid city name have been entered
        if response.status_code == requests.codes.ok:

            # get weather api response
            weather_response = response.text
            weather_data = json.loads(weather_response)["main"]
            #print (weather_data)
            
            output = input_text.capitalize() + " current weather: \n"
            output += "\tTemp: " + str(weather_data['temp']) + " C\n"
            output += "\tFeels Like: " + str(weather_data['feels_like']) + " C\n"
            output += "\tPressure: " + str(weather_data['pressure']) + " hPa\n"
            output += "\tHumidity: " + str(weather_data['humidity']) + " %"
            #print( output )    
            
            # print weather details to the user
            client.chat_postMessage(channel=channel_id, text=output)
        
        else:
            # print back user message
            client.chat_postMessage(channel=channel_id, text=input_text)