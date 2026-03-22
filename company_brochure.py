
# Create a product that builds a Brochure for a company to be used for prospective clients, investors and potential recruits.
# We will be provided a company name and their primary website."

#import neccesry libraries
import os 
from openai import OpenAI
from dotenv import load_dotenv
from scrapper import scrape_content, fetch_website_links


# ollama base url 
base_url="http://localhost:11434/v1"


#initialization and constants

load_dotenv(override=True)

api_key = os.getenv("GROQ_API_KEY")


if api_key and api_key.startswith("gsk_"):
    print("API key is set correctly.")
else:
    print("API key is not set correctly. Please check your .env file.")


#testing the scrapper function 
# links = fetch_website_links("https://www.apple.com")

# print(links)

#initialize the openai client
ollama = OpenAI(api_key=api_key, base_url= base_url)

#defining link_system prompt
link_system_prompt= """

You are provided with a list of links found on a webpage.
You are able to decide which of the links would be most relevant to include in a brochure about the company,
such as links to an About page, or a Company page, or Careers/Jobs pages.
You should respond in JSON as in this example:

{
    "links": [
        {"type": "about page", "url": "https://full.url/goes/here/about"},
        {"type": "careers page", "url": "https://another.full.url/careers"}
    ]
}

"""
#defining the user prompt for link selection
def get_link_user_prompt(url):


    user_prompt =F"""

        Here is the list of links on the website {url} -
        Please decide which of these are relevant web links for a brochure about the company, 
        respond with the full https URL in JSON format.
        Do not include Terms of Service, Privacy, email links.

        Links (some might be relative links):
        """
    
    links = fetch_website_links(url)
    user_prompt += "\n".join(links)
    return user_prompt


# testing the link selection function
def select_relevant_links(url):

    responses = ollama.chat.completions.create(
        model ="minimax-m2.5:cloud",

        messages =[
            {"role":"system", "content": link_system_prompt},
            {"role":"user", "content": get_link_user_prompt(url)}
        ]
      

    )
    return responses.choices[0].message.content



result = select_relevant_links("https://edwarddonner.com/")

result = select_relevant_links("https://www.apple.com/")

print(result)