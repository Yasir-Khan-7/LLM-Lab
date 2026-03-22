import requests
from openai import OpenAI

# test the connection to the Ollama API
data = requests.get("http://localhost:11434").content

# initialize the OpenAI client with the base URL for Ollama
baseurl = "http://localhost:11434/v1"

ollama = OpenAI(api_key="not-needed", base_url=baseurl)

# test the client by making a simple request to the chat completions endpoint
responses = ollama.chat.completions.create(
    model="minimax-m2.5:cloud",
    messages=[
        {"role": "user", "content": "What is the capital of France?"}
    ]
)
print(responses.choices[0].message.content)



