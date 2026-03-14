#this file serves as scrapper which will help in scrapping the data from the website 


import requests
from bs4 import BeautifulSoup

headers= {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
} 

def scrape_content(url):


    response = requests.get(url, headers=headers, timeout=10)

    if response.status_code == 200:

        soup = BeautifulSoup(response.content, "html.parser")

        title = soup.title.string if soup.title else "No title found"
        if soup.body:
            for irrelevant in (["script", "style", "img", "input"]):
                irrelevant.decompose()

            text = soup.body.get_text(separator="\n",strip = True)

        else:
            text = "No body content found"
        return (title + "\n\n"  +text)[:2000]



def fetch_website_links(url):


    response   = requests.get(url, headers = headers, timeout=10)

    if response.status_code == 200:

        soup = BeautifulSoup(response.content, "html.parser")


        links = [link.get("href") for link in soup.find_all("a")]

        return [link for link in links if link]