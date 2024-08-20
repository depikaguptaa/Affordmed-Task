const express = require('express');
const axios = require('axios');

const app = express();
const port = 3000;

// Window size configuration
const windowSize = 11;
let numbers = [];

// Function to fetch a number based on ID
const fetchNumber = async (id) => {
  const thirdPartyUrl = 'http://20.244.56.144/test/even';
  try {
    const response = await axios.get(thirdPartyUrl, { timeout: 500 });
    if (response.data && typeof response.data.number === 'number') {
      console.log(`Fetched number for ID ${id}:`, response.data.number); // Debug log
      return response.data.number;
    } else {
      console.error(`Invalid response format for ID ${id}:`, response.data); // Debug log
      return null;
    }
  } catch (error) {
    console.error(`Error fetching number for ID ${id}:`, error.message); // Debug log
    return null;
  }
};

app.get('/numbers/:id', async (req, res) => {
  const { id } = req.params;
  const validIds = ['p', 'f', 'e', 'r'];

  if (!validIds.includes(id)) {
    return res.status(400).json({ error: 'Invalid ID' });
  }

  const number = await fetchNumber(id);

  const prevState = [...numbers]; // Preserve the previous state

  if (number !== null && !isNaN(number)) {
    if (number <= 500) {  // Filter out numbers greater than 500
      if (numbers.length >= windowSize) {
        numbers.shift(); // Remove the oldest number
      }
      numbers.push(number); // Add the new number
    }
  }

  // Remove duplicates
  const uniqueNumbers = [...new Set(numbers)];

  // Calculate the average
  const average =
    uniqueNumbers.length === 0
      ? 0
      : uniqueNumbers.reduce((acc, curr) => acc + curr, 0) / uniqueNumbers.length;

  res.json({
    windowPrevState: prevState,
    windowCurrState: uniqueNumbers,
    numbers: [number], // Ensure number is wrapped in array
    avg: average.toFixed(2),
  });
});

app.listen(port, () => {
  console.log(`Server running at http://localhost:${port}`);
});
