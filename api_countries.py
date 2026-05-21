import requests, pandas as pd
from erreurs_api import get_api

pays_novabrand = ["France", "Germany", "Spain", "Italy", "Netherlands"]
rows = []

for pays in pays_novabrand:
    if pays == "Netherlands":
        url = "https://restcountries.com/v3.1/alpha/NLD?fields=name,population,area,currencies,languages"
        data = requests.get(url).json()
    else:
        url = f"https://restcountries.com/v3.1/name/{pays}?fields=name,population,area,currencies,languages"
        data = requests.get(url).json()[0]


    #url = (f"https://restcountries.com/v3.1/name/{pays}"
    #   f"?fields=name,population,area,currencies,languages")
    #data = get_api.get_api(url)[0]



    rows.append({
    "country"   : pays,
    "population": data["population"],
    "area_km2"  : data["area"],
    "currency"  : ", ".join(data["currencies"].keys()),
    "languages" : ", ".join(data["languages"].values()),
})
    
df_countries = pd.DataFrame(rows)
df_countries.to_csv("countries.csv", index=False)
print(df_countries)