from flask import Flask, jsonify
import requests
import time
from collections import deque

app = Flask(__name__)

# configuring url,port,token and timeout

BASE_URL = 'http://20.244.56.144/test'
PORT = 9876
WINDOW_SIZE = 10
TIMEOUT = 0.5  # 500 milliseconds
AUTH_TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJNYXBDbGFpbXMiOnsiZXhwIjoxNzI0MTYzOTU2LCJpYXQiOjE3MjQxNjM2NTYsImlzcyI6IkFmZm9yZG1lZCIsImp0aSI6ImY0OTA2NTRjLWE1NjgtNDJhNi1hYzI5LWIwYzBmOWM3ZjA0NiIsInN1YiI6ImRlcGlrYWcyMUBiYmRuaXRtLmFjLmluIn0sImNvbXBhbnlOYW1lIjoiQkJETklUTSIsImNsaWVudElEIjoiZjQ5MDY1NGMtYTU2OC00MmE2LWFjMjktYjBjMGY5YzdmMDQ2IiwiY2xpZW50U2VjcmV0IjoiaWhQaUlDa1FQc3Npd2x4ViIsIm93bmVyTmFtZSI6IkRlcGlrYSBHdXB0YSIsIm93bmVyRW1haWwiOiJkZXBpa2FnMjFAYmJkbml0bS5hYy5pbiIsInJvbGxObyI6IjIxMDA1NDE1MzAwMjYifQ.i5jbnEMZX_rU_j5H5GI98mzF2xbNA6nRUTfVVAQJB3Y'

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
