from flask import Flask, request, render_template, session
from flask_session import Session
import geeta
import re
from datetime import datetime
import requests
from mistralai import Mistral
from dotenv import dotenv_values
import geeta
import contact

config = dotenv_values(".env")  # Load .env file as a dictionary
api_key = config.get('API_KEY')  # Access the key from the dictionary

print(f"Loaded API Key: {api_key}")
# Initialize Mistral client
client = Mistral(api_key=api_key)

# Initialize Flask app
server = Flask(__name__)
server.secret_key = 'your_secret_key_here'  # Replace with a real secret key

# Configure server-side sessions
server.config['SESSION_TYPE'] = 'filesystem'
server.config['SESSION_FILE_DIR'] = './.flask_session/'
Session(server)


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


# Define the initiate text (prompt template)
initiate_txt = (
    '''You are a spiritual guide providing insights based on selected religions. Answer in detail like 7 8 lines
    Format your response using this exact pattern:
    
    ===ReligionName===
    [Response content]
    
    Use only: Hinduism, Islam, Christianity.
    Never add markdown/HTML tags.
    Keep responses under 200 words per religion.'''
)

def send_gpt(prompt, religions):
    try:
        full_prompt = f"{initiate_txt}\nQuestion: {prompt}\nSelected Religions: {', '.join(religions)}"
        chat_response = client.chat.complete(
            model="open-mistral-nemo",
            messages=[{"role": "user", "content": full_prompt}]
        )
        return chat_response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

def parse_response(response, selected_religions):
    religion_responses = {}
    current_religion = None
    buffer = []
    
    for line in response.split('\n'):
        line = line.strip()
        if line.startswith('===') and line.endswith('==='):
            if current_religion and current_religion in selected_religions:
                religion_responses[current_religion] = '\n'.join(buffer)
            current_religion = line[3:-3].strip()
            buffer = []
        elif current_religion and current_religion in selected_religions:
            buffer.append(line)
    
    if current_religion and current_religion in selected_religions:
        religion_responses[current_religion] = '\n'.join(buffer)
    
    print(religion_responses)
    return religion_responses

@server.route('/', methods=['GET', 'POST'])
def get_request_json():
    if 'conversation_history' not in session:
        session['conversation_history'] = []

    if request.method == 'POST' and 'question' in request.form:
        try:
            question = request.form['question']
            selected_religions = request.form.getlist('religions')
            
            if not selected_religions:
                return render_template('spiritual.html',
                    error="Please select at least one religion",
                    conversation_history=session['conversation_history'])

            resp = send_gpt(question, selected_religions)
            parsed_responses = parse_response(resp, selected_religions)

            session['conversation_history'].append({
                "question": question,
                "answer": parsed_responses,
                "religions": selected_religions
            })
            
            # Keep only last 3 conversations
            session['conversation_history'] = session['conversation_history'][-3:]
            session.modified = True

            return render_template('spiritual2.html',
                                 conversation_history=session['conversation_history'])
            
        except Exception as e:
            print(f"Error: {e}")
            return render_template('spiritual2.html',
                                 error="An error occurred. Please try again.",
                                 conversation_history=session['conversation_history'])

    return render_template('spiritual2.html',
                         conversation_history=session['conversation_history'])

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


@server.route('/numerology', methods=['GET', 'POST'])
def numerology():
    selected_date = ""
    numerology_number = ""
    insight = ""
    tagline=""

    if request.method == 'POST':
        selected_date = request.form.get('date')
        if selected_date:
            birthdate = datetime.strptime(selected_date, "%Y-%m-%d")

            # Calculate Life Path Number
            total = sum(int(digit) for digit in birthdate.strftime('%Y%m%d'))
            while total > 9 and total not in [11, 22, 33]:
                total = sum(int(d) for d in str(total))
            numerology_number = total

            # Get Insight
            insights = {
                1: '''You loveee to lead! You’re a hard worker with a spirit for innovation. You also have a passion for art. You can manifest super easily, and you have a strong desire to always be number one at anything you do. You don’t let anything, or anyone, stand in the way of you and your dreams. All you’ve got to do is focus on what you want, and you can achieve it!

Your downfall: you’re critical of yourself and others. You have a hard fast no on laziness, and you expect the best from yourself and therefore everyone else around you. You have a tendency to be self-centered and demanding. Because you are passionate about being the best, you can sometimes come off as arrogant or boastful. But it’s just your innate desire to be successful. ''',
                2: '''Think of all two’s in life. They thrive in partnership, and working with others. You are very sensitive and in tune with the world around you. You are your best self when helping others and making shizz happen behind the scenes. You’re great with details. You flourish when your focus is on serving the greater good of the group. You are a natural peacemaker, and can see all views of any situation. It’s your superpower.

Your downfall: you give, and you give, and you give some more, until it makes you withdraw with resentment. It’s important that you find your purpose in your own way, and not the way you believe others see you. You’re a pleaser, but it’s often what hurts you. You are sensitive, which can sometimes also be your downfall. You are afraid of being hurt, and that usually causes you to avoid confrontation which results in your own resentment towards the person or situation. ''',
                3: '''You live on a strong vibration and a high level of creativity and self expression. You’re independent and thrive in communication. Because of your communication skills, both verbal and written, you would be greatly suited as a poet, writer, actor, artist, or musician. You are optimistic and extremely generous. You can always find the positive in any situation. You easily make those around you feel comfortable and at ease. You have such high potential for being successful, specifically in the arts, and if you can figure out a way to make money at it; you’ll be set for a great career.

Your downfalls: because you live in the moment, you aren’t very good with money and responsibilities. You believe everything will work out and not to worry about tomorrow. When you are hurt emotionally, you can lash out and give biting comments to others. ''',
                4: '''You’re all about putting the pieces together and making it work. You’re a hard worker, super grounded, determined, practical and disciplined. You’re “the building blocks of society” as you create the foundation for others to thrive on. You don’t look for an easy way to the top and you’re usually considered very down-to-earth. You love to be organized and have a plan. If you’ve got a plan, you can easily tackle any of your never ending to-do-list. Home is your haven, and you need everything in your home environment to be in place. If your home is messy and unkept, it is a clear sign that you’re not doing well.

Your downfalls: you’ve got a lot happening in your mind, so it’s important that you find ways to relax your mind. Otherwise, great ideas will live and die in your head. You have a very strong sense of right and wrong, and you value honesty in yourself and others. But, that can sometimes lead to judgement towards yourself and others. You can be so set in your ways that you come across as stubborn or too serious. You show your feelings easily and don’t hold anything back, which sometimes can turn others away. You’re also extremely cautious, hating to deviate from your master plan, which causes you to miss opportunities. ''',
                5: '''Your number is that of freedom and change. You seek freedom above all else. You love to be adventurous, and can become restless very easily. You’re always on the go, wanting change and variety in your life. You love meeting new people, trying new things, and always living in the moment. You’ll typically want to be your own boss, and would be a great traveling salesman. You don’t like mundane or repetitive, so you always need to strive for something new. Your life is all about the senses, and your desire for experience can manifest itself in so many ways.

Your downfalls: If you don’t live adventurously, you’ll become very dramatic. You have a fear of being trapped or smothered in a relationship, so you have a hard time settling down. Your need for adventure keeps you distracted and can keep you unaware of the feelings of those around you. You’re easily manipulative and controlling of others. It’s your purpose to find balance in your life and inner freedom through discipline, focus, and experience. ''',
                6: '''You have a strong innate sense of responsibility and awareness, which makes you great at nurturing. You’re all about family, home, and community. You’re loving, warm, compassionate, and have an interest in pleasing others. You thrive as a caretaker and provider. You love nothing more than serving your family and friends. Your parenting instincts are also super strong. You’re a big picture kind of person and highly dislike being told what to do. You’re all about enriching your home and those around it, and it brings you great joy.

Your downfalls: You become self-righteous easily and critical of others. Because you are so giving, you can also become a slave to others needs and neglect your own. You might not have a good balance between helping and meddling. You may also become an enabler in someone else’s life, specifically your children, and may keep them from experiencing life and all its lessons. You’re a control freak, so strive to accept the perfection of imperfection. ''',
                7: '''You are very spiritually driven, and have a strong bend towards being a force in our world. You have the potential to reach high, and can live on a different spiritual plane than others. Your number gives a higher awareness and wider point of view. You have an air of mystery about you, but can also easily become a loner. You are wise and studious. You are always searching for the true meaning, and the underlying answer, of everything. You have a love for natural beauty: the ocean, green grass, plans, flowers, etc. You’re here to be a truth seeker. Embrace that.

Your downfalls: You need to learn to have faith, as if you don’t, you’ll turn very cynical and escape through drugs, alcohol, work, and geography. Your love of solitude can make it hard for you to find close relationships. People struggle to feel like they know you, and you can come off as eccentric. You can become easily frustrated and critical when out of alignment. ''',
                8: '''You’re a powerhouse and proud of it! You have an excellent judge of character and attract the right kind of people around you. You would make a great executive in the business or political world. You have a need for success and a strong desire for achievement. Your number represents authority, material wealth, ambition, and caution. You’ll work diligently to achieve your goals.

Your downfalls: You struggle feeling “safe” unless you have financial security. Your status is important to you which can cause you to live above your means. It is very difficult for you to take advice. You can be prone to becoming a workaholic, and can sometimes neglect family and friends in pursuit of financial wealth. Work on balance, and embracing opportunities for new lessons in this life to find inner success and wealth. Dream big and go for it!''',
                9: '''In numerology, the number nine is the number of completeness. You are a natural born leader and people assume you’re in charge even if you’re not. You take care of everyone else, but need to speak up when you need support and love yourself. You have an extremely strong sense of compassion and generosity, and helping others is of utmost importance to you. Your generosity knows no bounds, and you make people feel very comfortable around you. Your ultimate goal is working towards a better world.

Your downfalls: It’s hard for you to let go of that past. You might feel unloved or abandoned by your mother or father which makes you feel responsible for them. You are so giving that your finances might not be in the best state. You also have a tendency to be scattered if out of alignment. If you are pursuing materialistic gains other than your true sense of giving, you could feel deeply dissatisfied with yourself. ''',
                11: '''You are the most intuitive of all numbers and have a strong capacity for healing. You are sensitive and care a ton about what’s going on behind the scenes. You pick up on other people’s feelings and hidden attributes easily. You also have the qualities of the number two magnified. You are a visionary.

Your downfalls: You can become easily overwhelmed by your gifts. Fears and phobias are very typical of your number. You can also become nervous and moody easily. You are the most spiritually inclined of all the numbers, and therefore can be sensitive and anxious. ''',
                22: '''Your foundation rests in the number four, but with 22 you bring an intensity into changing people’s lives in a practical way through your teaching. You’ve come with a higher spiritual purpose, and you will no doubt feel that intensity in everything you do. You strive to serve the greater good of humanity and you are the ultimate visionary.

Your downfalls: You can seem extremely rigid and are your own worst enemy. You may paralyze yourself with your fear of failure. It can take someone with this number well into your adulthood before you manifest your dreams. But when you get there, it will be extraordinary. ''',
                33: '''This number is very rare. It’s usually the likes of a spiritual leader such as Dalai Lama or Gandhi. 33 is also a very nurturing number, and this life path is focused on reaching the world and uplifting the loving energy of mankind. You are not concerned with personal ambition and have a great devotion to cause.

Your downfalls: It’s all about coming to terms with your need for perfection and control and instead using your energy to make the world a better place.'''
            }
            insight = insights.get(numerology_number, "No insight available for this number.")

            taglines = {
                1: "1 Life Path – The Leader",
                2: "2 Life Path – The Harmony Seeker ",
                3: "3 Life Path – The Communicator ",
                4: "Life Path – The Busy Bee of Society (oh, and this is my life path number!)",
                5: "5 Life Path – The Free Bird ",
                6: "6 Life Path – The Nurturer",
                7: "7 Life Path – The Seeker ",
                8: "8 Life Path – The Manifesting Boss",
                9: "9 Life Path – The Humanitarian ",
                11: "11/2 Life Path - Most Intuitive",
                22: "22/4 Life Path -  Higher Spiritual Purpose",
                33: "33/6 Life Path - Spiritual Leader"
            }
            tagline = taglines.get(numerology_number, "No insight available for this number.")

    return render_template(
        'numerology.html',
        selected_date=selected_date,
        numerology_number=numerology_number if numerology_number else "Enter a birthdate",
        insight=insight if insight else "Enter a birthdate",
        tagline=tagline
    )

@server.route('/pomodoro')
def pomodoro():
    return render_template('pomodoro.html')

server.add_url_rule('/contact', view_func=contact.contact)

if __name__ == '__main__':
    server.run(debug=True, host='0.0.0.0', port=80)