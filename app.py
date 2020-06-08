from flask import Flask, render_template, request, redirect, url_for
import requests
import json
from bson.objectid import ObjectId
from pymongo import MongoClient
import os
from dotenv import load_dotenv #needed for .env
load_dotenv() #needed for .env
import urllib.request

# Databases
host = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/weather')
client = MongoClient(host=f'{host}?retryWrites=false')
db = client.get_default_database()
moods = db.mood
app = Flask(__name__)

ApiKey = os.getenv("WEATHER_API_KEY") #set the api key

@app.route('/',methods=['POST','GET'])
def home():
    if request.method =='POST':
        city_name = request.form['name']
    else:
        city_name = 'richmond'
    # access the openweathermap api
    url = ('http://api.openweathermap.org/data/2.5/weather?q=' + city_name + '&appid=' + ApiKey)
    complete = urllib.request.urlopen(url).read()
    response = json.loads(complete)
    # what is going to be serched for in the api
    weather = {
        "city" : str(response['name']),
        "icon" : response['weather'][0]['icon'],
        "description" : response['weather'][0]['description'],
        "temp": str(response['main']['temp']) + 'k',
        "humidity": str(response['main']['humidity']),
    }
    print(weather)
    return render_template('index.html', weather=weather, moods=moods.find())

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/converter')
def converter():
    return render_template('converter.html')

@app.route('/moods/new')
def new_mood():
    return render_template('new_mood.html', mood={}, title='New Mood Log')

@app.route('/moods', methods=['POST'])
def submit_mood():
    mood = {
    'date': request.form.get('date'),
    'city': request.form.get('city'),
    'weather': request.form.get('weather'),
    'mood': request.form.get('mood')
    }
    print(mood)
    mood_id = moods.insert_one(mood).inserted_id
    return redirect(url_for('show_mood', mood_id=mood_id))

@app.route('/moods/<mood_id>')
def show_mood(mood_id):
    mood = moods.find_one({'_id': ObjectId(mood_id)})
    return render_template('show_mood.html', mood=mood)

@app.route('/moods/<mood_id>/edit')
def edit_mood(mood_id):
    mood = moods.find_one({'_id': ObjectId(mood_id)})
    return render_template('edit_mood.html', mood=mood, title='Edit Mood Log')

@app.route('/moods/<mood_id>', methods=['POST'])
def update_mood(mood_id):
    # Edit my mood
    updated_mood = {
    'date': request.form.get('date'),
    'city': request.form.get('city'),
    'weather': request.form.get('weather'),
    'mood': request.form.get('mood')
    }
    moods.update_one(
        {'_id': ObjectId(moods)},
        {'$set': updated_mood})
    return redirect(url_for('show_mood', mood_id=mood_id))

@app.route('/moods/<mood_id>/delete', methods=['POST'])
def delete_mood(mood_id):
    moods.delete_one({'_id': ObjectId(mood_id)})
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=os.environ.get('PORT', 5000))

