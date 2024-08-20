from flask import Flask, jsonify
import requests
import time
import json
from collections import deque

# loading configuration from config.json
with open('config.json') as config_file:
    config = json.load(config_file)

app = Flask(__name__)

# configuring url,port,token and timeout
BASE_URL = config['BASE_URL']
PORT = config['PORT']
WINDOW_SIZE = config['WINDOW_SIZE']
TIMEOUT = config['TIMEOUT']
AUTH_TOKEN = config['AUTH_TOKEN']

# using deque
window = deque(maxlen=WINDOW_SIZE)

def fetch_numbers(number_id):
    url = f"{BASE_URL}/{number_id}"
    headers = {
        'Authorization': f'Bearer {AUTH_TOKEN}'
    }
    try:
        start_time = time.time()
        response = requests.get(url, headers=headers, timeout=TIMEOUT)
        elapsed_time = time.time() - start_time
        if elapsed_time > TIMEOUT or response.status_code != 200:
            return []
        data = response.json()
        return data.get('numbers', [])
    except:                                # in case of errors
        return []

def calculate_average(numbers):
    if not numbers:
        return 0.0
    return sum(numbers) / len(numbers)

@app.route('/numbers/<number_id>', methods=['GET'])
def get_numbers(number_id):
    global window

    endpoints = {
        'p': 'primes',
        'f': 'fibo',
        'e': 'even',
        'r': 'rand'
    }

    if number_id not in endpoints:
        return jsonify({"error": "Invalid numberid"}), 400
    window_prev_state = list(window)
    new_numbers = fetch_numbers(endpoints[number_id])
    new_numbers_set = set(new_numbers)
    unique_numbers = list(set(window) | new_numbers_set)  
    window.clear()
    window.extend(unique_numbers[-WINDOW_SIZE:]) 
    average = calculate_average(window)

    # Response
    response = {
        "windowPrevState": window_prev_state,
        "windowCurrState": list(window),
        "numbers": new_numbers,
        "avg": average
    }

    return jsonify(response), 200

# running the app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT, debug=True)