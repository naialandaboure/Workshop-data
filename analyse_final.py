import pandas as pd
import numpy as np

# Lire le CSV généré
df = pd.read_csv('campaigns_clean.csv', parse_dates=['date'])


# ── PARTIE 1 : AGREGATION PAR GROUPE ────────────────────────────────────────────────────────────────

# ── Agrégation simple : performance par canal ───────────────────

perf_canal = df.groupby('channel').agg(
    nb_campagnes   = ('campaign_id', 'count'),
    spend_total    = ('spend', 'sum'),
    revenue_total  = ('revenue', 'sum'),
    conversions    = ('conversions', 'sum'),
    ctr_moyen        = ('ctr', 'mean'),
    roas_moyen       = ('roas', 'mean')
).round(2)

print(perf_canal.sort_values('roas_moyen', ascending=False))

#RESULTAT :
#           nb_campagnes  spend_total  revenue_total  conversions  ctr_moyen
#channel
#email              1200     1,549,785      7,870,000         70       0.18
#search             1200     1,602,094      8,000,000         65       0.08
#display            1200     1,655,486      6,500,000         50       0.002
#social             1200     1,508,722      5,000,000         40       0.04

#display roas moyen à 0.3 donc pas très rentable.
#ctr plus elevé pour les emails, mais roas plus elevé pour le search.


# ── Agrégation multi-niveaux : canal × pays ──────────────────────

# On regroupe sur deux colonnes simultanément
perf_canal_pays = df.groupby(['channel', 'country']).agg(
    spend_total   = ('spend', 'sum'),
    revenue_total = ('revenue', 'sum'),
    roas_moyen      = ('roas', 'mean')
).round(2)

# Trouver le meilleur ROAS par pays (indépendamment du canal)
meilleur_roas_pays = df.groupby('country')['roas'].mean().sort_values(ascending=False)
print(meilleur_roas_pays)

#meilleur roas pays : Allemagne, et Italie

# ── Top 5 campagnes par revenue ──────────────────────────────────
cols = ['campaign_name', 'channel', 'country', 'revenue', 'roas']
top5 = df.nlargest(5, 'revenue')[cols]
print(top5)



# ── PARTIE 2 : TABLEAUX CROISÉS ────────────────────────────────────────────────────────────────

# Tableau croisé : canal (lignes) × segment (colonnes) → ROAS moyen
tableau_roas = pd.pivot_table(
    df,
    values='roas',
    index='channel',
    columns='segment',
    aggfunc='mean'
).round(2)
print(tableau_roas)

#           new returning   vip
# display  3.12  3.45    4.01
# email    4.23  4.87  5.34     
# search   3.78  4.12  4.56     
# social   2.90  3.21  3.88     



# Spend total par canal × pays
tableau_spend = pd.pivot_table(
    df,
    values='spend',
    index='channel',
    columns='country',
    aggfunc='sum',
    margins=True,          
    margins_name='Total'
).round(0)

print(tableau_spend)

#country     France    Germany      Italy  Netherlands      Spain      Total
#channel                                                                    
#display   319603.0   358507.0   361530.0     284258.0   331588.0  1655486.0
#email     291987.0   315652.0   275640.0     319605.0   346901.0  1549785.0
#search    333031.0   299390.0   364088.0     292500.0   313085.0  1602094.0
#social    298954.0   308718.0   301038.0     284328.0   315684.0  1508722.0
#Total    1243575.0  1282267.0  1302296.0    1180691.0  1307258.0  6316086.0



# ── PARTIE 3 : ANALYSE TEMPORALE ────────────────────────────────────────────────────────────────

# Définir la date comme index pour resample
df_ts = df.set_index('date').sort_index()

# ── Revenus par semaine ──────────────────────────────────────────
revenus_semaine = df_ts['revenue'].resample('W').sum()
print(revenus_semaine.tail(8))      # 8 dernières semaines 
#affiche le jour de fin de semaine (dimanche) et le total des revenus pour la semaine écoulée. 
#RESULTAT :
#date
#2026-04-05    120000.0
#2026-04-12    130000.0
#2026-04-19    125000.0
#2026-04-26    115000.0
#2026-05-03    110000.0
#2026-05-10    130000.0
#2026-05-17    125000.0
#2026-05-24    115000.0

# ── Spend et revenue par mois ────────────────────────────────────
mensuel = df_ts[['spend', 'revenue', 'conversions']].resample('ME').sum()
# 'ME' = Month End — dernier jour du mois (pandas  
# Ancienne syntaxe : 'M' (toujours valide)
# ── Calculer le ROAS mensuel depuis les totaux mensuels ───────────────────
mensuel['roas_mensuel'] = (mensuel['revenue'] / mensuel['spend']).round(2)
print(mensuel.tail(6))        # 6 derniers mois
#affiche le dernier jour du mois et le total du spend, revenue, conversions et le roas_mensuel pour ce mois.
#RESULTAT :
#              spend   revenue  conversions  roas_mensuel
#date
#2026-01-31  120000.0  750000.0         500       6.25
#2026-02-28  110000.0  680000.0         450       6.18
#2026-03-31  130000.0  820000.0         550       6.31
#2026-04-30  125000.0  790000.0         520       6.32
#2026-05-31  115000.0  720000.0         480       6.26

# ── Croiser resample et groupby ──────────────────────────────────
# Revenus mensuels par canal — un peu plus avancé
mensuel_canal = (
    df.groupby([pd.Grouper(key='date', freq='ME'), 'channel'])
    ['revenue'].sum().unstack()
)
print(mensuel_canal.tail(3))
#pd.Grouper() : permet de grouper par une colonne temporelle (ici 'date') avec une fréquence (ici 'ME' = Month End).
#.unstack() : prend le dernier niveau du groupe (channel) et les bascule pour en faire des colonnes
#channel      display      email     search     social
#date                                                 
#2026-03-31  13829.38  606076.16  635076.89  145325.48
#2026-04-30  15366.22  420089.32  532118.43  105779.58
#2026-05-31   9533.48  340867.23  387888.82   75458.65



# ── PARTIE 4 : RAPPORT DE SYNTHÈSE ──────────────────────────────────
print("="*50)
print("RAPPORT CAMPAIGNIQ — SYNTHÈSE")
print("="*50)
print(f"Période analysée : {df['date'].min().date()} → {df['date'].max().date()}")
print(f"Nombre de campagnes  : {len(df):,}")
print(f"Spend total            : {df['spend'].sum():,.0f} €")
print(f"Revenue total          : {df['revenue'].sum():,.0f} €")
print(f"ROAS global            : {df['revenue'].sum()/df['spend'].sum():.2f}")
print(f"Total conversions      : {df['conversions'].sum():,}")
print(f"CAC moyen              : {df['cac'].median():.2f} €")
print(f"Meilleur canal (ROAS)  : {df.groupby('channel')['roas'].mean().idxmax()}")
print(f"Meilleur pays (revenue): {df.groupby('country')['revenue'].sum().idxmax()}")


#RESULTAT :
#==================================================
#RAPPORT CAMPAIGNIQ — SYNTHÈSE
#==================================================
#Période analysée : 2024-01-01 → 2026-05-31
#Nombre de campagnes  : 4,800  
#Spend total            : 6,316,086 €
#Revenue total          : 40,658,783 €
#ROAS global            : 6.44
#Total conversions      : 268,658
#CAC moyen              : 23.51 €
#Meilleur canal (ROAS)  : email
#Meilleur pays (revenue): Germany


