from flask import Flask, request, render_template, session
from flask_session import Session
import geeta
import re
from datetime import datetime
import requests
from mistralai import Mistral
from dotenv import dotenv_values
import geeta

# Load environment variables
config = dotenv_values(".env")
api_key = config.get('API_KEY')

# Initialize Mistral client
client = Mistral(api_key=api_key)

# Initialize Flask app
server = Flask(__name__)
server.secret_key = 'your_secret_key_here'  # Replace with a real secret key

# Configure server-side sessions
server.config['SESSION_TYPE'] = 'filesystem'
server.config['SESSION_FILE_DIR'] = './.flask_session/'
Session(server)

# Define the initiate text (prompt template)
initiate_txt = (
    '''You are a spiritual guide providing insights based on selected religions.
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

if __name__ == '__main__':
    server.run(debug=False, host='0.0.0.0', port=80)