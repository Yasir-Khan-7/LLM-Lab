
# Create a product that builds a Brochure for a company to be used for prospective clients, investors and potential recruits.
# We will be provided a company name and their primary website."

#import neccesry libraries
import json
import os 
from urllib.parse import urlparse
from openai import OpenAI
from dotenv import load_dotenv
from scrapper import scrape_content, fetch_website_links

from IPython.display import display, Markdown, update_display

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
Return at most 5 links.
Only include links that are on the same website domain as the company.
Do not include external social media or third-party links.
You should respond in JSON as in this example:

{
    "links": [
        {"type": "about page", "url": "https://full.url/goes/here/about"},
        {"type": "careers page", "url": "https://another.full.url/careers"}
    ]
}

"
# Alternative link system prompt example:
#
# link_system_prompt = """
# You will receive a list of URLs from a company homepage.
# Pick the most useful internal pages for a brochure, such as About, Careers, Pricing, Product, or Blog.
# Return at most 5 links in JSON only.
# Exclude external sites, social profiles, and legal pages.
# """

#defining the user prompt for link selection
def get_link_user_prompt(url):


    user_prompt =F"""

        Here is the list of links on the website {url} -
        Please decide which of these are relevant internal web links for a brochure about the company.
        Respond with the full https URL in JSON format.
        Do not include Terms of Service, Privacy, email links, or external social/third-party links.
        Return no more than 5 links.

        Links (some might be relative links):
        """
    
    links = fetch_website_links(url)
    user_prompt += "\n".join(links)
    return user_prompt

# Alternative link user prompt example:
# def get_link_user_prompt(url):
#     user_prompt = f"""
#         Here are the URLs found on {url}.
#         Select up to 5 links that would help a brochure reader understand the company.
#         Only return same-domain pages and ignore legal, terms, privacy, login, and social links.
#         Format the output as a JSON object with `type` and `url` fields.
#         """
#     urls = fetch_website_links(url)
#     user_prompt += "\n".join(urls)
#     return user_prompt


def filter_relevant_links(links, base_url, max_links=5):
    host = urlparse(base_url).netloc
    filtered = []
    for link in links.get("links", []):
        href = link.get("url", "")
        parsed = urlparse(href)
        if parsed.netloc and not (parsed.netloc == host or parsed.netloc.endswith("." + host)):
            continue
        filtered.append(link)
        if len(filtered) >= max_links:
            break
    return {"links": filtered}


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
    links = filter_relevant_links(links, url, max_links=5)
    print(f"found {len(links['links'])} relevant links for {url}")
    return links

# output = select_relevant_links("https://edwarddonner.com/")

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

# Alternative brochure system prompt example:
# brochure_system_prompt = """
# You are a marketing copywriter.
# Use the page contents to write a concise brochure that highlights:
# - what the company does
# - who it serves
# - why it is unique
# - any hiring or careers information
# Output in clean markdown with headings and short paragraphs.
# Do not include code blocks.
# """

# This function generates the user prompt for the brochure creation by combining the content from the landing page and the relevant links. It calls the fetch_page_and_relevant_links function to get the necessary information and then formats it into a user prompt that can be used to generate the brochure content.
def get_brochure_user_prompt(company_name, url):
    user_prompt = f"""
You are looking at a company called: {company_name}
Here are the contents of its landing page and other relevant pages;
use this information to build a short brochure of the company in markdown without code blocks.\n\n
"""
    user_prompt += fetch_page_and_relevant_links(url)
    user_prompt = user_prompt[:5_000] # Truncate if more than 5,000 characters
    return user_prompt


# print(fetch_page_and_relevant_links("https://huggingface.co"))


# This function creates a brochure for the company by calling the language model with the appropriate system and user prompts, and then prints the generated brochure content.
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

    print("\n=== Generated Brochure ===\n")
    print(brochure_content)



#Stream the brochure content as it's being generated by the model, instead of waiting for the entire response to be ready. This can provide a more responsive experience, especially if the brochure content is lengthy or if the model takes some time to generate the response.
def stream_brochure(company_name, url):
    stream = ollama.chat.completions.create(
        model=Model,
        messages=[
            {"role": "system", "content": brochure_system_prompt},
            {"role": "user", "content": get_brochure_user_prompt(company_name, url)}
          ],
        stream=True
    )    
    response = ""
    display_handle = display(Markdown(""), display_id=True)
    for chunk in stream:
        response += chunk.choices[0].delta.content or ''
        update_display(Markdown(response), display_id=display_handle.display_id)

create_brochure("Hugging Face", "https://huggingface.co")