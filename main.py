from flask import Flask, request, render_template, redirect, send_from_directory # type: ignore
import geeta
from flask.templating import render_template_string
from flask import Blueprint
import os
from datetime import datetime
import requests
from mistralai import Mistral
from dotenv import dotenv_values

import requests


config = dotenv_values(".env")  # Load .env file as a dictionary
api_key = config.get('API_KEY')  # Access the key from the dictionary

print(f"Loaded API Key: {api_key}")

model = "mistral-large-latest"

client = Mistral(api_key=api_key)

# Define the initiate text (prompt template)
initiate_txt = (
   '''You are a spiritual guide providing insights based on Hindu, Islamic, and Christian teachings. When presented with a user's question about personal feelings or workplace issues (e.g., 'I want peace in my workplace' or 'I am feeling left out'), respond by addressing the concern through the lens of these religious philosophies.

In your response, include references to relevant teachings, particularly focusing on:

    Hinduism: Slokas (verses) from sacred texts like the Bhagavad Gita, Upanishads, and Vedas.
    Islam: Ayahs (verses) from the Quran and Hadiths of the Prophet Muhammad (peace be upon him).
    Christianity: Verses from the Bible, including teachings of Jesus Christ.

Provide a detailed explanation of these verses, their meanings, and how they can be applied to the user's situation. Make sure your answer is compassionate and offers practical advice based on these teachings.

IMPORTANT:

    DON'T mention that you are an AI model.
    DON'T answer modern-day tech questions.
    You are an ancient and wise guide, deeply knowledgeable in these scriptures.
    Make the response as short as possible, but if it is too short, add RELEVANT VERSES from the religious texts.
    Provide real-life examples from Mahabharata, Islamic history (such as the lives of the Sahaba), and Biblical narratives.
    TRY TO GIVE THE ANSWER IN THE LANGUAGE THE QUESTION IS ASKED IN.
    Ensure the response is in HTML code format, using <strong> for bold elements. The response should be formatted so it can be directly used with the 'safe' tag in Jinja script. Remove unnecessary spaces and <br> tags before and after the answer text.
    DO NOT GIVE AN ANSWER IF THE CONTEXT IS NOT RELEVANT TO SPIRITUALITY AND KINDLY DECLINE'''
)

def getHoroscope(sign):
    # Hardcoded horoscope messages for each zodiac sign
    url = f"https://horoscope-app-api.vercel.app/api/v1/get-horoscope/daily?sign={sign}&day=TODAY"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        return data.get("data", {}).get("horoscope_data", "No horoscope found.")
    else:
        return f"Error: {response.status_code} - {response.text}"

def get_zodiac_sign(birthdate):
    print('aaaaaaaaa')
    day = birthdate.day
    month = birthdate.month

    if month == 12:
        return 'Sagittarius' if day < 22 else 'Capricorn'
    elif month == 1:
        return 'Capricorn' if day < 20 else 'Aquarius'
    elif month == 2:
        return 'Aquarius' if day < 19 else 'Pisces'
    elif month == 3:
        return 'Pisces' if day < 21 else 'Aries'
    elif month == 4:
        return 'Aries' if day < 20 else 'Taurus'
    elif month == 5:
        return 'Taurus' if day < 21 else 'Gemini'
    elif month == 6:
        return 'Gemini' if day < 21 else 'Cancer'
    elif month == 7:
        return 'Cancer' if day < 23 else 'Leo'
    elif month == 8:
        return 'Leo' if day < 23 else 'Virgo'
    elif month == 9:
        return 'Virgo' if day < 23 else 'Libra'
    elif month == 10:
        return 'Libra' if day < 23 else 'Scorpio'
    elif month == 11:
        return 'Scorpio' if day < 22 else 'Sagittarius'


def send_gpt(prompt):
    try:
        # Create the full prompt by appending the question to the template
        full_prompt = initiate_txt + prompt + "\nNOW ANSWER THE ABOVE PART."
        
        # Make the API request
        chat_response = client.chat.complete(
        model = "open-mistral-nemo",
        messages = [
            {
                "role": "user",
                "content": full_prompt,
            },
        ]
    )

        print(chat_response.choices[0].message.content)
        return chat_response.choices[0].message.content

    except Exception as e:
        # Return the error message for debugging
        return f"Error occurred: {str(e)}"

quote = geeta.random_quote

server = Flask(__name__)
server.config['STATIC_FOLDER'] = 'static'
static_bp = Blueprint('static',
                      __name__,
                      static_url_path='/static',
                      static_folder='static')
server.register_blueprint(static_bp)

messages = []
question=""
@server.route('/', methods=['GET', 'POST'])
def get_request_json():
    # Initialize variables for chatbot and horoscope
    question = None
    resp = None

    if request.method == 'POST':
        # Check if the request contains 'question' for chatbot interaction
        if 'question' in request.form:
            try:
                question = request.form['question']
                if len(question) < 1:
                    return render_template(
                        'spiritual.html',
                        question="I have no questions to ask. Lend me some of your knowledge",
                        res="Here is some wisdom for you.")
                
                # Get GPT response for the question
                resp = send_gpt(question)
                print("Q：\n", question)
                print("A：\n", resp)

                return render_template('spiritual.html', question=question, res=str(resp))
            except Exception as e:
                print(f"Error: {e}")
                return render_template(
                    'spiritual.html',
                    question=question,
                    res="Developer is lazy to resolve bugs... Come back later")
    # Default rendering for GET request
    return render_template('spiritual.html')

@server.route('/horoscope', methods=['GET', 'POST'])
def index():
    selected_date = ""
    zodiac_sign = ""
    horo={}
    if request.method == 'POST':
        selected_date = request.form.get('date')  # Get the selected date from the form
        birthdate = datetime.strptime(selected_date, "%Y-%m-%d")
        print(birthdate.month)
        print(birthdate.year)
        # Determine the zodiac sign based on the birthdate
        zodiac_sign = get_zodiac_sign(birthdate)
        print(zodiac_sign)
        horo = getHoroscope(zodiac_sign)
        return render_template('horoscope.html', selected_date=selected_date, zodiac_sign=zodiac_sign,horoscope=horo)
    return render_template('horoscope.html', selected_date=selected_date, zodiac_sign="enter birthdate",horoscope="enter birthdate")

@server.route('/pomodoro')
def pomodoro():
    return render_template('pomodoro.html')

if __name__ == '__main__':
	server.run(debug=False, host='0.0.0.0', port=80)