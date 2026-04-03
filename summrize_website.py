from  openai import  OpenAI
from bs4 import BeautifulSoup
import requests
#challenge scrape any url and summarize the content using openai chat client 

#create neccessay functions and variables for cleancode 


base_url = "http://localhost:11434/v1"

ollama = OpenAI(api_key="not-needed", base_url=base_url)



# Function to scrape content from a given URL
def scrape_content(url):
    try: 
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract text from the webpage
        text = soup.get_text()
        return text
    except Exception as e:
        print(f"Error scraping the webpage: {e}")
        return None
    
 # Function to summarize the content using OpenAI's chat completions   
def summarize_content(content):


    responses = ollama.chat.completions.create(

        model = "minimax-m2.5:cloud",

        messages = [
                
                    {"role":"user","content": f"please summarize the content of this webpage: {content}"}
                    
                    ]

    )
    return responses.choices[0].message.content

# user_prompt = input("Enter the URL of the webpage you want to summarize: ")
content = input("Enter the URL of the webpage you want to summarize: ")

scrape_data = scrape_content(content)
summary = summarize_content(scrape_data)
print(f"summary of the webpage:\n {summary}")