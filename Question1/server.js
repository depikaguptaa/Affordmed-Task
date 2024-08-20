const express = require('express');
const axios = require('axios');
const fs = require('fs');
const app = express();

// Loading configuration from config.json
const config = JSON.parse(fs.readFileSync('config.json'));

const BASE_URL = config.BASE_URL;
const PORT = config.PORT;
const WINDOW_SIZE = config.WINDOW_SIZE;
const TIMEOUT = config.TIMEOUT;
const AUTH_TOKEN = config.AUTH_TOKEN;

// Using a deque-like array with a fixed window size
let window = [];

const fetchNumbers = async (number_id) => {
  const url = ${BASE_URL}/${number_id};
  const headers = {
    'Authorization': Bearer ${AUTH_TOKEN}
  };
  try {
    const startTime = Date.now();
    const response = await axios.get(url, { headers, timeout: TIMEOUT * 1000 });
    const elapsedTime = (Date.now() - startTime) / 1000;
    if (elapsedTime > TIMEOUT || response.status !== 200) {
      return [];
    }
    return response.data.numbers || [];
  } catch (error) {
    return [];
  }
};

const calculateAverage = (numbers) => {
  if (!numbers.length) {
    return 0.0;
  }
  const sum = numbers.reduce((acc, num) => acc + num, 0);
  return sum / numbers.length;
};

app.get('/numbers/:number_id', async (req, res) => {
  const endpoints = {
    'p': 'primes',
    'f': 'fibo',
    'e': 'even',
    'r': 'rand'
  };

  const number_id = req.params.number_id;
  if (!endpoints[number_id]) {
    return res.status(400).json({ error: "Invalid number_id" });
  }

  const windowPrevState = [...window];
  const newNumbers = await fetchNumbers(endpoints[number_id]);
  const newNumbersSet = new Set(newNumbers);
  const uniqueNumbers = [...new Set([...window, ...newNumbersSet])];
  window = uniqueNumbers.slice(-WINDOW_SIZE);

  const average = calculateAverage(window);

  const response = {
    windowPrevState,
    windowCurrState: [...window],
    numbers: newNumbers,
    avg: average
  };

  return res.status(200).json(response);
});

app.listen(PORT, () => {
  console.log(Server is running on port ${PORT});
});