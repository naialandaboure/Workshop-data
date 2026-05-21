from bs4 import BeautifulSoup
import requests

url = "http://quotes.toscrape.com"
response = requests.get(url)

soup = BeautifulSoup(response.text, "html.parser")


print(soup.title.text)       # "Quotes to Scrape"                  
quotes = soup.find_all("div", class_="quote")
print(f"{{len(quotes)}} citations sur cette page")  # 10

premier = quotes[0]
print(premier.find("span", class_="text").text)
print(premier.find("small", class_="author").text)
