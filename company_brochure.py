
# Create a product that builds a Brochure for a company to be used for prospective clients, investors and potential recruits.
# We will be provided a company name and their primary website."

#import neccesry libraries
import os 
from openai import OpenAI
from dotenv import load_dotenv
from scrapper import scrape_content

#initialization and constants

load_dotenv(override=True)

api_key = os.getenv("GROQ_API_KEY")


if api_key and api_key.startswith("gsk_"):
    print("API key is set correctly.")
else:
    print("API key is not set correctly. Please check your .env file.")






