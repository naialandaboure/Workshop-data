import pandas as pd
import numpy as np

df = pd.read_csv('campaigns.csv')

# ── CORRECTION 1 : Convertir la colonne date en datetime ──────────────────────────────────
df['date'] = pd.to_datetime(df['date'])

# Vérification
print(df['date'].dtype)     # datetime64[ns]  ✅
print(df['date'].min())     # date la plus ancienne
print(df['date'].max())     # date la plus récente


# ── CORRECTION 2 : Les valeurs manquantes ─────────────────────────────────────────────────
# ── Stratégie 1 : supprimer les lignes où country est inconnu ───
# On ne peut pas analyser les performances par pays sans le pays
print("Avant dropna, nb country non vides:", len(df), "lignes")
df = df.dropna(subset=['country'])
print("Après dropna, nb country non vides:", len(df), "lignes")

# ── Stratégie 2 : remplacer spend manquant par la médiane ───────
# On ne veut pas perdre des lignes pour un budget manquant.
# La médiane est plus robuste que la moyenne face aux valeurs extrêmes.
mediane_spend = df['spend'].median()
df['spend'] = df['spend'].fillna(mediane_spend)
print(f"spend NaN remplacés par la médiane : {mediane_spend:.2f} €")

# Vérification — plus aucun NaN
print(df[['spend', 'country']].isnull().sum())


# ── CORRECTION 3 : Supprimer les doublons ────────────────────────────────────────────────
print("Avant dédoublonnage :", len(df), "lignes")
df = df.drop_duplicates()
df = df.reset_index(drop=True)   # réindexer proprement après suppression
print("Après dédoublonnage :", len(df), "lignes")

# Vérification
print("Doublons restants :", df.duplicated().sum())   # doit afficher 0


# ── CORRECTION 4 : Traiter les valeurs aberrantes dans clicks ─────────────────────────────
# Compter les lignes aberrantes avant filtrage
# 10 lignes
print("Clics négatifs :", (df['clicks'] < 0).sum())         
print("Clics > impressions :", (df['clicks'] > df['impressions']).sum())

# Filtrer : garder seulement les lignes valides
df = df[df['clicks'] >= 0]
df = df[df['clicks'] <= df['impressions']]
df = df.reset_index(drop=True)
print("Après nettoyage aberrations :", len(df), "lignes")



# ── Calcul des KPIs ──────────────────────────────────────────────────────────────────────────────
# CTR (clic / impressions) : % de personnes qui ont cliqué
# éviter la division par zéro avec np.where
# np.where(condition, valeur_si_vrai, valeur_si_faux) 
df['ctr'] = np.where(
    df['impressions'] > 0,
    df['clicks'] / df['impressions'],
    0
)

# CAC — coût d'acquisition (spend / conversions) : Combien coûte chaque client acquis. Plus c'est bas,mieux c'est.
# (NaN si 0 conversions — normal, on garde)
df['cac'] = df['spend'] / df['conversions'].replace(0, np.nan)

# ROAS — retour sur investissement publicitaire (revenue / spend) : Combien rapporte chaque euro dépensé. ROAS > 1 = rentable.
df['roas'] = df['revenue'] / df['spend'].replace(0, np.nan)

# CVR — taux de conversion (conversions / clicks) : % de cliqueurs qui achètent. 
df['cvr'] = np.where(
    df['clicks'] > 0,
    df['conversions'] / df['clicks'],
    0
)

# Vérification des nouvelles colonnes
print(df[['ctr', 'cac', 'roas', 'cvr']].describe().round(3))


# ── Extraire des composantes temporelles depuis la date ──────────────────────────────────────────────────────────────────────────────
df['year'] = df['date'].dt.year 
df['month'] = df['date'].dt.month
df['week'] = df['date'].dt.isocalendar().week.astype(int)
df['day_of_week'] = df['date'].dt.day_name() # 'Monday', 'Tuesday', etc.



# Sauvegarder le dataset nettoyé et enrichi
df.to_csv('campaigns_clean.csv', index=False)
print(f"Dataset nettoyé : {len(df)} lignes, {len(df.columns)} colonnes")
print("Colonnes :", df.columns.tolist())


