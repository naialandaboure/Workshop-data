import pandas as pd
import requests

df_meteo = pd.read_csv("meteo.csv")
df_countries = pd.read_csv("countries.csv")
df_taux  = pd.read_csv("taux_change.csv")

# Jointure météo + pays sur la colonne "country"
df_ref = df_meteo.merge(df_countries, on="country", how="left")

# Ajouter le taux EUR/USD (même valeur pour tous les pays)
df_ref["eur_usd_rate"] = df_taux["USD"].iloc[0]
df_ref["pop_density"]  = (df_ref["population"] / df_ref["area_km2"]).round(1)

print(df_ref[["country", "temperature_c", "population", "eur_usd_rate"]])
df_ref.to_csv("pays_reference.csv", index=False)
print("✅ pays_reference.csv créé")

#RESULTATS :
#  country  temperature_c  population  eur_usd_rate
#0  France           15.2     67391582          1.08
#1  Germany          10.5     83166711          1.08
#2  Spain            20.3     47351567          1.08
#3  Italy            18.7     59554023          1.08
#4  Netherlands      12.8     17441139          1.08


