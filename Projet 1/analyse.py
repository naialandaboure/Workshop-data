import pandas as pd
import numpy as np

# Lire le CSV généré
df = pd.read_csv('campaigns.csv')
print("Dimensions :", df.shape)     # (5050, 11)    
print(df.head())           # 5 premières lignes               

# ── Réflexe 1 : vue d'ensemble ──────────────────────────────────
df.info()             # Aperçu des types et valeurs manquantes

#Résultat :
 #   Column         Non-Null Count  Dtype  
 #0   campaign_id    5050 non-null   str    
 #1   date           5050 non-null   str    
 #2   channel        5050 non-null   str    
 #3   campaign_name  5050 non-null   str    
 #4   country        4847 non-null   str    
 #5   segment        5050 non-null   str    
 #6   impressions    5050 non-null   int64  
 #7   clicks         5050 non-null   int64  
 #8   conversions    5050 non-null   int64  
 #9   spend          4793 non-null   float64
 #10  revenue        5050 non-null   float64


# ── Réflexe 2 : statistiques descriptives ───────────────────────
print(df.describe()) # count / mean / std / min / 25% / 50% / 75% / max ; On cherche des min négatifs (clics négatifs), des max aberrants, etc.

#Résultat :
#         impressions        clicks  conversions         spend        revenue
#count    5050.000000   5050.000000  5050.000000   4793.000000    5050.000000
#mean    32950.116436   1880.830297    55.970495   1328.685610    6408.878404
#std     36966.155849   2737.453054    86.531712    917.540354   10103.227676
#min      1120.000000  "" -999.000000 ""    0.000000    115.070000       0.000000
#25%     11504.500000    183.000000     5.000000    725.330000     503.092500
#50%     21409.500000    907.000000    25.000000   1098.790000    2780.260000
#75%     40523.500000   2455.750000    72.000000   1670.010000    8194.250000
#max    541396.000000 34932.000000  1233.000000  16114.110000  180522.720000

# ── Réflexe 3 : valeurs manquantes ──────────────────────────────
print(df.isnull().sum()) # Nombre de NaN par colonne 

#Résultat :
#country          203
#spend            257


# ── Réflexe 4 : doublons ────────────────────────────────────────
print(df.duplicated().sum()) # Nombre de lignes identiques

# Résultat : 50 en doublons