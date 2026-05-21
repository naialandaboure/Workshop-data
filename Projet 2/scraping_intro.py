import requests

url = "http://quotes.toscrape.com/"
response = requests.get(url)

# 200 = succès, 404 = introuvable, 403 = accès refusé
print(response.status_code)
print(response.text[:500])  
# les 500 premiers chars du HTML