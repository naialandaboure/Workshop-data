import requests, pandas as pd
from erreurs_api import get_api

#Avec la mauvaise URL
url = "https://api.frankfurter.dev/v2/rates?base=EUR&symbols=USD,GBP,CHF,JPY"
data = get_api.get_api(url)