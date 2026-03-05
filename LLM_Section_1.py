import requests
from openai import OpenAI


data = requests.get("http://localhost:11434").content

baseurl = "http://localhost:11434/v1"

ollama = OpenAI(api_key="not-needed", base_url=baseurl)

responses = ollama.chat.completions.create(
    model="minimax-m2.5:cloud",
    messages=[
        {"role": "user", "content": "What is the capital of France?"}
    ]
)
print(responses.choices[0].message.content)

