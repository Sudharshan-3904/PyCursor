import requests

# Define the URL for the Ollama server
url = "http://localhost:1234/v1/models"  # Correct endpoint

# Define the headers
headers = {
    "Content-Type": "application/json"
}

# Define the payload with the user's message
payload = {
    "model": "granite3.1-moe:latest",  # Replace with your model name
    "prompt": "Hello, how are you?",
    "max_tokens": 200
}

# Make the POST request
response = requests.get(url)

# Check the response
if response.status_code == 200:
    response_data = response.json()
    print("Ollama response:", response_data)
else:
    print("Error:", response.status_code, response.text)
