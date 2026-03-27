
# Create a product that builds a Brochure for a company to be used for prospective clients, investors and potential recruits.
# We will be provided a company name and their primary website."

#import neccesry libraries
import json
import os 
from openai import OpenAI
from dotenv import load_dotenv
from scrapper import scrape_content, fetch_website_links
import markdown as md


# ollama base url 
base_url="http://localhost:11434/v1"

Model = "minimax-m2.5:cloud"

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
    print(f"Selecting relevant links for {url} by calling  {Model}")
    responses = ollama.chat.completions.create(
        model=Model,
        messages=[
            {"role": "system", "content": link_system_prompt},
            {"role": "user", "content": get_link_user_prompt(url)}
        ],
        response_format={"type": "json_object"}
    )
    results = responses.choices[0].message.content
    if isinstance(results, str):
        if not results.strip():
            raise ValueError("Model returned empty content; cannot parse JSON.")
        links = json.loads(results)
    elif isinstance(results, dict):
        links = results
    else:
        raise TypeError(f"Unexpected response content type: {type(results)}")
    print(f"found {len(links['links'])} relevant links for {url}")
    return links

output = select_relevant_links("https://edwarddonner.com/")

# print(output)


#Step 2 Creation of brochure content

def fetch_page_and_relevant_links(url):
    contents = scrape_content(url)
    relevant_links = select_relevant_links(url)
    print(contents)
    print(relevant_links)
    result = f"## Landing Page:\n\n{contents}\n## Relevant Links:\n"

    for link in relevant_links['links']:
      result += f"\n\n### Link: {link['type']}\n"
      result += scrape_content(link["url"])
    return result


brochure_system_prompt = """
You are an assistant that analyzes the contents of several relevant pages from a company website
and creates a short brochure about the company for prospective customers, investors and recruits.
Respond in markdown without code blocks.
Include details of company culture, customers and careers/jobs if you have the information.
"""


def get_brochure_user_prompt(company_name, url):
    user_prompt = f"""
You are looking at a company called: {company_name}
Here are the contents of its landing page and other relevant pages;
use this information to build a short brochure of the company in markdown without code blocks.\n\n
"""
    user_prompt += fetch_page_and_relevant_links(url)
    user_prompt = user_prompt[:5_000] # Truncate if more than 5,000 characters
    return user_prompt


print(fetch_page_and_relevant_links("https://huggingface.co"))


def create_brochure(company_name, url):
    print(f"Creating brochure for {company_name} by calling {Model}")
    responses = ollama.chat.completions.create(
        model = Model,
        messages = [
            {"role":"system", "content": brochure_system_prompt},
            {"role":"user", "content": get_brochure_user_prompt(company_name, url)}
        ]
    )
    brochure_content = responses.choices[0].message.content


    print(md.markdown(brochure_content))



create_brochure("Hugging Face", "https://huggingface.co")