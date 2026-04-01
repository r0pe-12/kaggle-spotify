import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import warnings
import os

warnings.filterwarnings('ignore')
sns.set_theme(style="whitegrid", palette="husl")
plt.rcParams['figure.figsize'] = (12, 7)
plt.rcParams['font.size'] = 11
plt.rcParams['figure.dpi'] = 150

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))


def separator(title):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


# ============================================================================
#  1. UCITAVANJE I CISCENJE PODATAKA
# ============================================================================

separator("1. UCITAVANJE I CISCENJE PODATAKA")

df = pd.read_csv(os.path.join(OUTPUT_DIR, "spotify_global_trends_2026.csv"))

print(f"Dimenzije dataseta: {df.shape[0]} redova x {df.shape[1]} kolona")
print(f"\nKolone: {list(df.columns)}")
print(f"\nTipovi podataka:")
print(df.dtypes.to_string())

# Provjera null vrijednosti
null_counts = df.isnull().sum()
print(f"\nNull vrijednosti po koloni:")
if null_counts.sum() == 0:
    print("  Nema null vrijednosti - dataset je kompletan!")
else:
    print(null_counts[null_counts > 0].to_string())

# Provjera duplikata
duplicates = df.duplicated().sum()
print(f"\nBroj duplikata: {duplicates}")
if duplicates > 0:
    df = df.drop_duplicates()
    print(f"  -> Uklonjeno {duplicates} duplikata. Novi broj redova: {len(df)}")

# Ciscenje - strip whitespace iz string kolona
str_cols = df.select_dtypes(include='object').columns
for col in str_cols:
    df[col] = df[col].str.strip()

# Provjera negativnih streamova (greska u podacima?)
neg_streams = (df['streams'] < 0).sum()
if neg_streams > 0:
    print(f"\n  UPOZORENJE: {neg_streams} pjesama ima negativne streamove!")

print(f"\nPrvih 5 redova:")
print(df.head().to_string())


# ============================================================================
#  2. OSNOVNA STATISTIKA (EDA)
# ============================================================================

separator("2. EKSPLORATIVNA DATA ANALIZA (EDA)")

numeric_cols = ['streams', 'stream_change', '7day', 'pos', 'days', 'viral_score']

print("Deskriptivna statistika numerickih kolona:")
print(df[numeric_cols].describe().round(2).to_string())

print(f"\n--- Frekvencije kategorickih kolona ---")

categorical_cols = ['genre', 'country', 'trend', 'popularity_category', 'longevity']
for col in categorical_cols:
    print(f"\n{col.upper()}:")
    vc = df[col].value_counts()
    for val, cnt in vc.items():
        pct = cnt / len(df) * 100
        print(f"  {val}: {cnt} ({pct:.1f}%)")


# ============================================================================
#  3. ANALIZA PO ZANROVIMA
# ============================================================================

separator("3. ANALIZA PO ZANROVIMA")

genre_stats = df.groupby('genre').agg(
    broj_pjesama=('track_name', 'count'),
    ukupni_streamovi=('streams', 'sum'),
    prosjecni_streamovi=('streams', 'mean'),
    prosjecni_viral=('viral_score', 'mean'),
    prosjecni_stream_change=('stream_change', 'mean'),
    max_streams=('streams', 'max')
).round(0)

genre_stats = genre_stats.sort_values('ukupni_streamovi', ascending=False)

print("Top 10 zanrova po ukupnim streamovima:")
print(genre_stats.head(10).to_string())

print(f"\nZanrovi sa najvecim prosjecnim rastom (stream_change):")
growing_genres = genre_stats.sort_values('prosjecni_stream_change', ascending=False).head(5)
for genre, row in growing_genres.iterrows():
    print(f"  {genre}: {row['prosjecni_stream_change']:+,.0f} prosjecan stream_change")

print(f"\nZanrovi sa najvecim padom:")
declining_genres = genre_stats.sort_values('prosjecni_stream_change').head(5)
for genre, row in declining_genres.iterrows():
    print(f"  {genre}: {row['prosjecni_stream_change']:+,.0f} prosjecan stream_change")


# ============================================================================
#  4. ANALIZA PO ZEMLJAMA
# ============================================================================

separator("4. ANALIZA PO ZEMLJAMA")

country_stats = df.groupby('country').agg(
    broj_pjesama=('track_name', 'count'),
    ukupni_streamovi=('streams', 'sum'),
    prosjecni_streamovi=('streams', 'mean'),
    prosjecni_viral=('viral_score', 'mean')
).round(0).sort_values('ukupni_streamovi', ascending=False)

print("Top 10 zemalja po ukupnim streamovima:")
print(country_stats.head(10).to_string())

# Dominantni zanrovi po zemljama
print(f"\nDominantni zanrovi po top zemljama:")
top_countries = country_stats.head(10).index
for country in top_countries:
    country_df = df[df['country'] == country]
    top_genre = country_df['genre'].value_counts().index[0]
    count = country_df['genre'].value_counts().values[0]
    print(f"  {country}: {top_genre} ({count} pjesama)")


# ============================================================================
#  5. TREND ANALIZA
# ============================================================================

separator("5. TREND ANALIZA")

trend_stats = df.groupby('trend').agg(
    broj_pjesama=('track_name', 'count'),
    prosjecni_streamovi=('streams', 'mean'),
    prosjecni_viral=('viral_score', 'mean'),
    prosjecni_stream_change=('stream_change', 'mean'),
    prosjecni_dani=('days', 'mean')
).round(0)

print("Statistike po trendu (Rising vs Falling):")
print(trend_stats.to_string())

# Rising po zanrovima
print(f"\nZanrovi sa najvise RISING pjesama:")
rising_df = df[df['trend'] == 'Rising']
rising_genres = rising_df['genre'].value_counts().head(10)
for genre, count in rising_genres.items():
    total = len(df[df['genre'] == genre])
    pct = count / total * 100 if total > 0 else 0
    print(f"  {genre}: {count} rising od {total} ukupno ({pct:.0f}%)")

# Longevity analiza
print(f"\nAnaliza po longevity kategoriji:")
longevity_stats = df.groupby('longevity').agg(
    broj_pjesama=('track_name', 'count'),
    prosjecni_streamovi=('streams', 'mean'),
    prosjecni_viral=('viral_score', 'mean'),
    prosjecni_dani=('days', 'mean')
).round(0).sort_values('prosjecni_streamovi', ascending=False)
print(longevity_stats.to_string())

# Popularity category analiza
print(f"\nAnaliza po popularity_category:")
pop_stats = df.groupby('popularity_category').agg(
    broj_pjesama=('track_name', 'count'),
    prosjecni_streamovi=('streams', 'mean'),
    prosjecni_viral=('viral_score', 'mean'),
    min_streams=('streams', 'min'),
    max_streams=('streams', 'max')
).round(0).sort_values('prosjecni_streamovi', ascending=False)
print(pop_stats.to_string())


# ============================================================================
#  6. KORELACIONA ANALIZA
# ============================================================================

separator("6. KORELACIONA ANALIZA")

corr_matrix = df[numeric_cols].corr().round(3)
print("Korelaciona matrica:")
print(corr_matrix.to_string())

# Najjace korelacije (izvan dijagonale)
print(f"\nNajjace korelacije:")
corr_pairs = []
for i in range(len(numeric_cols)):
    for j in range(i+1, len(numeric_cols)):
        corr_pairs.append((numeric_cols[i], numeric_cols[j], corr_matrix.iloc[i, j]))

corr_pairs.sort(key=lambda x: abs(x[2]), reverse=True)
for col1, col2, corr in corr_pairs[:8]:
    strength = "JAKA" if abs(corr) > 0.7 else "SREDNJA" if abs(corr) > 0.4 else "SLABA"
    direction = "pozitivna" if corr > 0 else "negativna"
    print(f"  {col1} <-> {col2}: {corr:.3f} ({strength} {direction})")


# ============================================================================
#  7. NAPREDNA ANALIZA
# ============================================================================

separator("7. NAPREDNA ANALIZA")

# --- Feature Engineering ---
print("--- Feature Engineering ---\n")

df['streams_per_day'] = np.where(df['days'] > 0, df['streams'] / df['days'], df['streams'])
df['efficiency_score'] = np.where(df['streams'] > 0, df['viral_score'] / df['streams'], 0)
df['growth_rate'] = np.where(df['streams'] > 0, df['stream_change'] / df['streams'] * 100, 0)
df['weekly_avg'] = df['7day'] / 7

print("Kreirane nove kolone:")
print("  - streams_per_day: prosjecni streamovi po danu na listi")
print("  - efficiency_score: viral_score / streams (viralnost po streamu)")
print("  - growth_rate: stream_change / streams * 100 (% rasta)")
print("  - weekly_avg: prosjecni dnevni streamovi u poslednjih 7 dana")

# Top 10 najefikasnijih pjesama (najvisi efficiency_score)
print(f"\nTop 10 pjesama po efficiency_score (viralnost po streamu):")
top_efficient = df.nlargest(10, 'efficiency_score')[['track_name', 'artist_name', 'streams', 'viral_score', 'efficiency_score']]
for _, row in top_efficient.iterrows():
    print(f"  {row['track_name']} - {row['artist_name']}: {row['efficiency_score']:.2f}")

# Top 10 po streams_per_day
print(f"\nTop 10 pjesama po streamovima dnevno:")
top_daily = df.nlargest(10, 'streams_per_day')[['track_name', 'artist_name', 'streams_per_day', 'days']]
for _, row in top_daily.iterrows():
    print(f"  {row['track_name']} - {row['artist_name']}: {row['streams_per_day']:,.0f}/dan ({row['days']:.0f} dana)")

# --- Outlier detekcija (IQR) ---
print(f"\n--- Outlier detekcija (IQR metoda) ---\n")
for col in ['streams', 'viral_score', 'stream_change']:
    Q1 = df[col].quantile(0.25)
    Q3 = df[col].quantile(0.75)
    IQR = Q3 - Q1
    lower = Q1 - 1.5 * IQR
    upper = Q3 + 1.5 * IQR
    outliers = df[(df[col] < lower) | (df[col] > upper)]
    print(f"  {col}: {len(outliers)} outlier-a (granice: [{lower:,.0f}, {upper:,.0f}])")
    if len(outliers) > 0 and len(outliers) <= 5:
        for _, row in outliers.iterrows():
            print(f"    -> {row['track_name']} ({row[col]:,.0f})")

# --- Pareto analiza ---
print(f"\n--- Pareto analiza ---\n")
artist_streams = df.groupby('artist_name')['streams'].sum().sort_values(ascending=False)
total_streams = artist_streams.sum()
n_artists = len(artist_streams)
top_20_pct = max(1, int(n_artists * 0.2))
top_20_streams = artist_streams.head(top_20_pct).sum()
pareto_pct = top_20_streams / total_streams * 100

print(f"Ukupno artista: {n_artists}")
print(f"Top 20% artista ({top_20_pct}): generise {pareto_pct:.1f}% ukupnih streamova")
print(f"\nTop 10 artista po ukupnim streamovima:")
for artist, streams in artist_streams.head(10).items():
    pct = streams / total_streams * 100
    print(f"  {artist}: {streams:,.0f} ({pct:.1f}%)")

# --- Pivot analiza ---
print(f"\n--- Pivot: Prosjecni streamovi po zanru i trendu ---\n")
top_genres_list = genre_stats.head(8).index.tolist()
pivot = df[df['genre'].isin(top_genres_list)].pivot_table(
    values='streams', index='genre', columns='trend', aggfunc='mean'
).round(0)
print(pivot.to_string())

print(f"\n--- Pivot: Broj pjesama po popularity_category i longevity ---\n")
pivot2 = pd.crosstab(df['popularity_category'], df['longevity'])
print(pivot2.to_string())


# ============================================================================
#  8. VIZUALIZACIJE
# ============================================================================

separator("8. GENERISANJE VIZUALIZACIJA")

# --- Graf 1: Top 15 pjesama po streamovima ---
fig, ax = plt.subplots(figsize=(14, 8))
top15 = df.nlargest(15, 'streams')
colors = ['#e74c3c' if t == 'Falling' else '#2ecc71' for t in top15['trend']]
bars = ax.barh(range(len(top15)), top15['streams'], color=colors, edgecolor='white', linewidth=0.5)
ax.set_yticks(range(len(top15)))
ax.set_yticklabels([f"{row['track_name']} - {row['artist_name']}" for _, row in top15.iterrows()], fontsize=9)
ax.set_xlabel('Streams', fontsize=12)
ax.set_title('Top 15 pjesama po broju streamova', fontsize=14, fontweight='bold')
ax.invert_yaxis()
for i, (_, row) in enumerate(top15.iterrows()):
    ax.text(row['streams'] + 50000, i, f"{row['streams']:,.0f}", va='center', fontsize=8)
ax.legend(handles=[
    plt.Rectangle((0,0),1,1, color='#2ecc71', label='Rising'),
    plt.Rectangle((0,0),1,1, color='#e74c3c', label='Falling')
], loc='lower right')
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, 'graf_01_top15_pjesama.png'), bbox_inches='tight')
plt.close()
print("  [1/12] graf_01_top15_pjesama.png")

# --- Graf 2: Top 10 artista po ukupnim streamovima ---
fig, ax = plt.subplots(figsize=(14, 7))
top10_artists = artist_streams.head(10)
colors_art = sns.color_palette("viridis", len(top10_artists))
bars = ax.barh(range(len(top10_artists)), top10_artists.values, color=colors_art, edgecolor='white')
ax.set_yticks(range(len(top10_artists)))
ax.set_yticklabels(top10_artists.index, fontsize=10)
ax.set_xlabel('Ukupni Streams', fontsize=12)
ax.set_title('Top 10 artista po ukupnim streamovima', fontsize=14, fontweight='bold')
ax.invert_yaxis()
for i, val in enumerate(top10_artists.values):
    ax.text(val + 100000, i, f"{val:,.0f}", va='center', fontsize=9)
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, 'graf_02_top10_artista.png'), bbox_inches='tight')
plt.close()
print("  [2/12] graf_02_top10_artista.png")

# --- Graf 3: Distribucija zanrova (Pie chart) ---
fig, ax = plt.subplots(figsize=(12, 8))
genre_counts = df['genre'].value_counts()
top_n = 8
other_count = genre_counts[top_n:].sum()
pie_data = pd.concat([genre_counts[:top_n], pd.Series({'Ostali': other_count})])
colors_pie = sns.color_palette("Set2", len(pie_data))
wedges, texts, autotexts = ax.pie(pie_data.values, labels=pie_data.index,
                                   autopct='%1.1f%%', colors=colors_pie,
                                   startangle=140, pctdistance=0.85)
for text in autotexts:
    text.set_fontsize(9)
ax.set_title('Distribucija pjesama po zanrovima', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, 'graf_03_distribucija_zanrova.png'), bbox_inches='tight')
plt.close()
print("  [3/12] graf_03_distribucija_zanrova.png")

# --- Graf 4: Korelaciona matrica (Heatmap) ---
fig, ax = plt.subplots(figsize=(10, 8))
mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
sns.heatmap(corr_matrix, mask=mask, annot=True, fmt='.2f', cmap='RdBu_r',
            center=0, square=True, linewidths=1, ax=ax,
            vmin=-1, vmax=1, cbar_kws={'shrink': 0.8})
ax.set_title('Korelaciona matrica numerickih varijabli', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, 'graf_04_korelaciona_matrica.png'), bbox_inches='tight')
plt.close()
print("  [4/12] graf_04_korelaciona_matrica.png")

# --- Graf 5: Streams vs Viral Score (Scatter) ---
fig, ax = plt.subplots(figsize=(12, 8))
trend_colors = {'Rising': '#2ecc71', 'Falling': '#e74c3c'}
for trend_val, color in trend_colors.items():
    mask = df['trend'] == trend_val
    ax.scatter(df.loc[mask, 'streams'], df.loc[mask, 'viral_score'],
               c=color, label=trend_val, alpha=0.6, s=60, edgecolors='white', linewidth=0.5)
z = np.polyfit(df['streams'], df['viral_score'], 1)
p = np.poly1d(z)
x_line = np.linspace(df['streams'].min(), df['streams'].max(), 100)
ax.plot(x_line, p(x_line), "--", color='gray', alpha=0.7, label=f'Trend linija (r={corr_matrix.loc["streams","viral_score"]:.2f})')
ax.set_xlabel('Streams', fontsize=12)
ax.set_ylabel('Viral Score', fontsize=12)
ax.set_title('Odnos: Streams vs Viral Score', fontsize=14, fontweight='bold')
ax.legend(fontsize=11)
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, 'graf_05_streams_vs_viral.png'), bbox_inches='tight')
plt.close()
print("  [5/12] graf_05_streams_vs_viral.png")

# --- Graf 6: Box plot - Streamovi po popularity_category ---
fig, ax = plt.subplots(figsize=(12, 7))
order = df.groupby('popularity_category')['streams'].median().sort_values(ascending=False).index
sns.boxplot(data=df, x='popularity_category', y='streams', order=order,
            palette='Set2', ax=ax, linewidth=1.5)
ax.set_xlabel('Popularity Category', fontsize=12)
ax.set_ylabel('Streams', fontsize=12)
ax.set_title('Distribucija streamova po popularity kategoriji', fontsize=14, fontweight='bold')
for i, cat in enumerate(order):
    median = df[df['popularity_category'] == cat]['streams'].median()
    ax.text(i, median, f'{median:,.0f}', ha='center', va='bottom', fontweight='bold', fontsize=9)
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, 'graf_06_boxplot_popularity.png'), bbox_inches='tight')
plt.close()
print("  [6/12] graf_06_boxplot_popularity.png")

# --- Graf 7: Box plot - Viral score po longevity ---
fig, ax = plt.subplots(figsize=(12, 7))
order_long = df.groupby('longevity')['viral_score'].median().sort_values(ascending=False).index
sns.boxplot(data=df, x='longevity', y='viral_score', order=order_long,
            palette='coolwarm', ax=ax, linewidth=1.5)
ax.set_xlabel('Longevity', fontsize=12)
ax.set_ylabel('Viral Score', fontsize=12)
ax.set_title('Distribucija viral score-a po longevity kategoriji', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, 'graf_07_boxplot_longevity.png'), bbox_inches='tight')
plt.close()
print("  [7/12] graf_07_boxplot_longevity.png")

# --- Graf 8: Trend distribucija po top zanrovima (Stacked bar) ---
fig, ax = plt.subplots(figsize=(14, 7))
top_genres_for_chart = genre_stats.head(10).index.tolist()
trend_pivot = df[df['genre'].isin(top_genres_for_chart)].groupby(['genre', 'trend']).size().unstack(fill_value=0)
trend_pivot = trend_pivot.loc[top_genres_for_chart]
trend_pivot.plot(kind='bar', stacked=True, ax=ax, color=['#e74c3c', '#2ecc71'], edgecolor='white')
ax.set_xlabel('Zanr', fontsize=12)
ax.set_ylabel('Broj pjesama', fontsize=12)
ax.set_title('Rising vs Falling distribucija po top zanrovima', fontsize=14, fontweight='bold')
ax.legend(title='Trend', fontsize=10)
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, 'graf_08_trend_po_zanrovima.png'), bbox_inches='tight')
plt.close()
print("  [8/12] graf_08_trend_po_zanrovima.png")

# --- Graf 9: Top 10 zemalja po broju pjesama ---
fig, ax = plt.subplots(figsize=(12, 7))
top10_countries = df['country'].value_counts().head(10)
colors_country = sns.color_palette("rocket", len(top10_countries))
bars = ax.bar(range(len(top10_countries)), top10_countries.values, color=colors_country, edgecolor='white')
ax.set_xticks(range(len(top10_countries)))
ax.set_xticklabels(top10_countries.index, rotation=45, ha='right', fontsize=10)
ax.set_ylabel('Broj pjesama', fontsize=12)
ax.set_title('Top 10 zemalja po broju trending pjesama', fontsize=14, fontweight='bold')
for i, val in enumerate(top10_countries.values):
    ax.text(i, val + 0.3, str(val), ha='center', fontweight='bold', fontsize=10)
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, 'graf_09_top10_zemalja.png'), bbox_inches='tight')
plt.close()
print("  [9/12] graf_09_top10_zemalja.png")

# --- Graf 10: Histogram distribucije streamova ---
fig, ax = plt.subplots(figsize=(12, 7))
ax.hist(df['streams'], bins=30, color='#3498db', edgecolor='white', alpha=0.8)
ax.axvline(df['streams'].mean(), color='red', linestyle='--', linewidth=2, label=f"Prosjek: {df['streams'].mean():,.0f}")
ax.axvline(df['streams'].median(), color='orange', linestyle='--', linewidth=2, label=f"Medijan: {df['streams'].median():,.0f}")
ax.set_xlabel('Streams', fontsize=12)
ax.set_ylabel('Frekvencija', fontsize=12)
ax.set_title('Distribucija streamova (histogram)', fontsize=14, fontweight='bold')
ax.legend(fontsize=11)
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, 'graf_10_histogram_streamova.png'), bbox_inches='tight')
plt.close()
print("  [10/12] graf_10_histogram_streamova.png")

# --- Graf 11: Days on chart vs Streams (scatter, boja = longevity) ---
fig, ax = plt.subplots(figsize=(12, 8))
longevity_colors = {'New': '#e74c3c', 'Stable Hit': '#f39c12', 'Evergreen': '#2ecc71', 'Average': '#3498db'}
for longevity_val, color in longevity_colors.items():
    mask = df['longevity'] == longevity_val
    if mask.sum() > 0:
        ax.scatter(df.loc[mask, 'days'], df.loc[mask, 'streams'],
                   c=color, label=longevity_val, alpha=0.6, s=60, edgecolors='white', linewidth=0.5)
ax.set_xlabel('Dani na listi', fontsize=12)
ax.set_ylabel('Streams', fontsize=12)
ax.set_title('Dani na listi vs Streams (po longevity kategoriji)', fontsize=14, fontweight='bold')
ax.legend(fontsize=11)
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, 'graf_11_days_vs_streams.png'), bbox_inches='tight')
plt.close()
print("  [11/12] graf_11_days_vs_streams.png")

# --- Graf 12: Prosjecni streamovi po zanru i trendu (Grouped bar) ---
fig, ax = plt.subplots(figsize=(14, 7))
top8_genres = genre_stats.head(8).index.tolist()
grouped = df[df['genre'].isin(top8_genres)].groupby(['genre', 'trend'])['streams'].mean().unstack(fill_value=0)
grouped = grouped.loc[[g for g in top8_genres if g in grouped.index]]
x = np.arange(len(grouped))
width = 0.35
if 'Falling' in grouped.columns:
    ax.bar(x - width/2, grouped['Falling'], width, label='Falling', color='#e74c3c', edgecolor='white')
if 'Rising' in grouped.columns:
    ax.bar(x + width/2, grouped['Rising'], width, label='Rising', color='#2ecc71', edgecolor='white')
ax.set_xticks(x)
ax.set_xticklabels(grouped.index, rotation=45, ha='right', fontsize=10)
ax.set_ylabel('Prosjecni Streams', fontsize=12)
ax.set_title('Prosjecni streamovi po zanru i trendu', fontsize=14, fontweight='bold')
ax.legend(fontsize=11)
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, 'graf_12_grouped_zanr_trend.png'), bbox_inches='tight')
plt.close()
print("  [12/12] graf_12_grouped_zanr_trend.png")


# ============================================================================
#  9. KLJUCNI UVIDI (INSIGHTS)
# ============================================================================

separator("9. KLJUCNI UVIDI IZ ANALIZE")

top_artist = artist_streams.index[0]
top_artist_streams = artist_streams.values[0]
top_artist_pct = top_artist_streams / total_streams * 100
top_song = df.loc[df['streams'].idxmax()]
total_rising = len(df[df['trend'] == 'Rising'])
total_falling = len(df[df['trend'] == 'Falling'])
top_genre = genre_stats.index[0]
top_country = country_stats.index[0]
avg_streams = df['streams'].mean()
median_streams = df['streams'].median()

evergreen_df = df[df['longevity'] == 'Evergreen']
new_df = df[df['longevity'] == 'New']

print(f"1. DOMINANTAN ARTIST: {top_artist} sa {top_artist_streams:,.0f} ukupnih streamova ({top_artist_pct:.1f}% svih)")
print(f"   - Najpopularnija pjesma: '{top_song['track_name']}' sa {top_song['streams']:,.0f} streamova")
print()
print(f"2. TREND BILANS: {total_rising} Rising vs {total_falling} Falling pjesama ({total_rising/(total_rising+total_falling)*100:.0f}% vs {total_falling/(total_rising+total_falling)*100:.0f}%)")
print()
print(f"3. DOMINANTAN ZANR: {top_genre} sa {genre_stats.loc[top_genre, 'ukupni_streamovi']:,.0f} ukupnih streamova")
print()
print(f"4. DOMINANTNA ZEMLJA: {top_country} sa {country_stats.loc[top_country, 'ukupni_streamovi']:,.0f} ukupnih streamova")
print()
print(f"5. DISTRIBUCIJA STREAMOVA: Prosjek={avg_streams:,.0f}, Medijan={median_streams:,.0f}")
skewness = avg_streams / median_streams
if skewness > 1.2:
    print(f"   -> Distribucija je POZITIVNO ISKRIVLJENA (skewed right) - mali broj pjesama ima izuzetno visoke streamove")
print()
print(f"6. PARETO EFEKAT: Top 20% artista ({top_20_pct}) generise {pareto_pct:.1f}% ukupnih streamova")
print()
if len(evergreen_df) > 0 and len(new_df) > 0:
    print(f"7. LONGEVITY: Evergreen pjesme ({len(evergreen_df)}) imaju prosjek od {evergreen_df['streams'].mean():,.0f} streamova")
    print(f"   New pjesme ({len(new_df)}) imaju prosjek od {new_df['streams'].mean():,.0f} streamova")
    print(f"   Evergreen pjesme u prosjeku provode {evergreen_df['days'].mean():.0f} dana na listi vs {new_df['days'].mean():.0f} za New")
print()

# Najbrze rastuca pjesma
if len(rising_df) > 0:
    fastest_growing = rising_df.nlargest(1, 'stream_change').iloc[0]
    print(f"8. NAJBRZI RAST: '{fastest_growing['track_name']}' - {fastest_growing['artist_name']}")
    print(f"   Stream change: +{fastest_growing['stream_change']:,.0f}")

print()
print(f"9. KORELACIJE:")
top_corr = corr_pairs[0]
print(f"   Najjaca korelacija: {top_corr[0]} <-> {top_corr[1]} ({top_corr[2]:.3f})")

print()
print(f"10. UKUPNO: {len(df)} pjesama, {n_artists} artista, {len(df['genre'].unique())} zanrova, {len(df['country'].unique())} zemalja")

separator("ANALIZA ZAVRSENA")
print(f"Generisano 12 grafova u direktorijumu: {OUTPUT_DIR}")
print(f"Ukupno obradjeno: {len(df)} redova sa {len(df.columns)} kolona\n")
