import pandas as pd
import requests
from datetime import date
from sqlalchemy import create_engine


# 1. Charger le dataset NovaBrand
df = pd.read_csv("campaigns_clean.csv")
df["date"] = pd.to_datetime(df["date"])


# 2. Agréger par pays — 7 derniers jours
date_limite = df["date"].max() - pd.Timedelta(days=7)
df_s = df[df["date"] >= date_limite]
kpi_pays = df_s.groupby("country").agg(
    nb_campagnes  = ("campaign_id", "count"),
    spend_eur     = ("spend",  "sum"),     
    revenue_eur   = ("revenue", "sum"),   
    conversions   = ("conversions", "sum"),
    roas_moyen    = ("roas", "mean")
).round(2).reset_index()


# 3. Taux de change EUR/USD
taux_data = requests.get("https://api.frankfurter.dev/v1/latest?base=EUR&symbols=USD").json()
#"https://api.frankfurter.dev/v2/rates?base=EUR&symbols=USD"
taux_usd = taux_data["rates"]["USD"]
kpi_pays["spend_usd"]   = (kpi_pays["spend_eur"]   * taux_usd).round(2)
kpi_pays["revenue_usd"] = (kpi_pays["revenue_eur"] * taux_usd).round(2)


# 4. Météo actuelle par capitale
capitales = {
    "France": (48.8566, 2.3522), "Germany": (52.52, 13.405),
    "Spain": (40.4168, -3.7038), "Italy": (41.9028, 12.4964),
    "Netherlands": (52.3676, 4.9041),
}
meteo_rows = []
for pays, (lat, lon) in capitales.items():
    r = requests.get(f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,precipitation").json()
    meteo_rows.append({"country": pays,
        "temperature_c": r["current"]["temperature_2m"],
        "precipitation_mm": r["current"]["precipitation"]})
df_meteo = pd.DataFrame(meteo_rows)


# 5. Merger tout ensemble
rapport = kpi_pays.merge(df_meteo, on="country", how="left")
rapport["taux_eur_usd"] = taux_usd
rapport["date_rapport"] = str(date.today())
rapport = rapport.sort_values("revenue_eur", ascending=False)
print(rapport)

#RESULTATS :
#       country  nb_campagnes  spend_eur  revenue_eur  conversions  roas_moyen  spend_usd  revenue_usd  temperature_c  precipitation_mm  taux_eur_usd date_rapport
#1      Germany            13   21020.69    109011.73          933        8.04   24426.04    126671.63           17.1               0.0         1.162   2026-05-20
#2        Italy            11   14275.71     68817.46          656        6.80   16588.38     79965.89           20.8               0.0         1.162   2026-05-20
#4        Spain            10   14362.85     51315.73          405        4.26   16689.63     59628.88           21.0               0.0         1.162   2026-05-20
#3  Netherlands            13   16136.09     43990.40          355        2.95   18750.14     51116.84           13.7               0.2         1.162   2026-05-20
#0       France             9   12760.61     39769.91          334        4.06   14827.83     46217.18           15.2               0.0         1.162   2026-05-20


rapport.to_csv("rapport_enrichi.csv", index=False)
print(f"✅ rapport_enrichi.csv ({len(rapport)} lignes)")


#___________________RAPPORT FORMATE________________________________________________________________________
aujourd_hui = date.today().strftime("%d/%m/%Y")

lignes = [
    f"══════════════════════════════════════",
    f"  RAPPORT NOVABRAND — {aujourd_hui}",
    f"══════════════════════════════════════",
    "",
    f"  Taux EUR/USD : {taux_usd} (BCE)",
    f"  Campagnes    : {len(df_s)}",
    "",
    f"  {'PAYS':<14} {'SPEND €':>9} {'REVENUE €':>11} {'ROAS':>6} {'T°':>5}",
    f"  {'─'*48}",
]

for _, row in rapport.iterrows():
    lignes.append(
        f" {row['country']:<14} {row['spend_eur']:>9,.0f}"
        f" {row['revenue_eur']:>11,.0f} {row['roas_moyen']:>6.2f}"
        f" {row['temperature_c']:>4.1f}°C"
    )
lignes += [
    f"  {'─'*48}", "",
    f"  TOTAL SPEND   : {rapport['spend_eur'].sum():,.0f} EUR",
    f"  TOTAL REVENUE : {rapport['revenue_eur'].sum():,.0f} EUR",
    f"  ROAS GLOBAL   : {rapport['revenue_eur'].sum()/rapport['spend_eur'].sum():.2f}",
]


rapport_texte = "\n".join(lignes)
with open("rapport_semaine.txt", "w", encoding="utf-8") as f:
    f.write(rapport_texte)
print("✅ rapport_semaine.txt généré")


engine = create_engine("postgresql+psycopg2://postgres:@localhost:5432/campaigniq")
rapport.to_sql("rapport_hebdo", con=engine, if_exists="replace", index=False)
print("✅ Table rapport_hebdo chargée")
engine.dispose()
