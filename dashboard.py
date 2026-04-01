import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

# ============================================================================
#  KONFIGURACIJA STRANICE
# ============================================================================

st.set_page_config(
    page_title="Spotify Global Trends 2026",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
#  UCITAVANJE PODATAKA
# ============================================================================

@st.cache_data
def load_data():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "spotify_global_trends_2026.csv")
    df = pd.read_csv(path)
    for col in df.select_dtypes(include='object').columns:
        df[col] = df[col].str.strip()
    df['streams_per_day'] = np.where(df['days'] > 0, df['streams'] / df['days'], df['streams'])
    df['efficiency_score'] = np.where(df['streams'] > 0, df['viral_score'] / df['streams'], 0)
    df['growth_rate'] = np.where(df['streams'] > 0, df['stream_change'] / df['streams'] * 100, 0)
    df['weekly_avg'] = df['7day'] / 7
    return df

df = load_data()

# ============================================================================
#  SIDEBAR - FILTERI
# ============================================================================

st.sidebar.title("🎛️ Filteri")

# Zanr filter
all_genres = sorted(df['genre'].unique())
selected_genres = st.sidebar.multiselect("Žanrovi", all_genres, default=all_genres)

# Zemlja filter
all_countries = sorted(df['country'].unique())
selected_countries = st.sidebar.multiselect("Zemlje", all_countries, default=all_countries)

# Trend filter
selected_trends = st.sidebar.multiselect("Trend", ['Rising', 'Falling'], default=['Rising', 'Falling'])

# Longevity filter
all_longevity = sorted(df['longevity'].unique())
selected_longevity = st.sidebar.multiselect("Longevity", all_longevity, default=all_longevity)

# Popularity filter
all_popularity = sorted(df['popularity_category'].unique())
selected_popularity = st.sidebar.multiselect("Popularity Category", all_popularity, default=all_popularity)

# Streams range
min_streams = int(df['streams'].min())
max_streams = int(df['streams'].max())
streams_range = st.sidebar.slider(
    "Raspon streamova",
    min_value=min_streams, max_value=max_streams,
    value=(min_streams, max_streams),
    format="%d",
    step=100000
)

# Days range
min_days = int(df['days'].min())
max_days = int(df['days'].max())
days_range = st.sidebar.slider(
    "Dani na listi",
    min_value=min_days, max_value=max_days,
    value=(min_days, max_days)
)

# Primjena filtera
filtered_df = df[
    (df['genre'].isin(selected_genres)) &
    (df['country'].isin(selected_countries)) &
    (df['trend'].isin(selected_trends)) &
    (df['longevity'].isin(selected_longevity)) &
    (df['popularity_category'].isin(selected_popularity)) &
    (df['streams'] >= streams_range[0]) &
    (df['streams'] <= streams_range[1]) &
    (df['days'] >= days_range[0]) &
    (df['days'] <= days_range[1])
]

st.sidebar.markdown("---")
st.sidebar.metric("Filtrirano pjesama", f"{len(filtered_df)} / {len(df)}")

# ============================================================================
#  HEADER
# ============================================================================

st.title("🎵 Spotify Global Trends 2026 - Interaktivni Dashboard")
st.markdown("Napredna analiza dataseta trending pjesama sa Spotify platforme")

# ============================================================================
#  KPI METRIKE (vrh stranice)
# ============================================================================

col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    st.metric("Ukupno pjesama", len(filtered_df))
with col2:
    st.metric("Artista", filtered_df['artist_name'].nunique())
with col3:
    st.metric("Žanrova", filtered_df['genre'].nunique())
with col4:
    st.metric("Prosj. streamovi", f"{filtered_df['streams'].mean():,.0f}")
with col5:
    rising_pct = len(filtered_df[filtered_df['trend'] == 'Rising']) / max(len(filtered_df), 1) * 100
    st.metric("Rising %", f"{rising_pct:.1f}%")
with col6:
    st.metric("Ukupni streamovi", f"{filtered_df['streams'].sum():,.0f}")

st.markdown("---")

# ============================================================================
#  TABOVI ZA NAVIGACIJU
# ============================================================================

tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
    "📊 Pregled",
    "🎸 Žanrovi",
    "🌍 Zemlje",
    "📈 Trendovi",
    "🔗 Korelacije",
    "🔬 Napredna analiza",
    "🔍 Pretraga",
    "📋 Dataset"
])

# ============================================================================
#  TAB 1: PREGLED
# ============================================================================

with tab1:
    st.header("Opšti pregled dataseta")

    col_left, col_right = st.columns(2)

    with col_left:
        # Top 15 pjesama
        top_n = st.slider("Top N pjesama", 5, 30, 15, key="top_n_songs")
        top_songs = filtered_df.nlargest(top_n, 'streams')
        fig = px.bar(
            top_songs, x='streams', y='track_name',
            color='trend',
            color_discrete_map={'Rising': '#2ecc71', 'Falling': '#e74c3c'},
            orientation='h',
            hover_data=['artist_name', 'genre', 'country', 'viral_score', 'days'],
            title=f'Top {top_n} pjesama po streamovima'
        )
        fig.update_layout(yaxis={'categoryorder': 'total ascending'}, height=500)
        st.plotly_chart(fig, use_container_width=True)

    with col_right:
        # Top artisti
        top_n_artists = st.slider("Top N artista", 5, 20, 10, key="top_n_artists")
        artist_streams = filtered_df.groupby('artist_name')['streams'].sum().nlargest(top_n_artists).reset_index()
        fig2 = px.bar(
            artist_streams, x='streams', y='artist_name',
            orientation='h',
            color='streams',
            color_continuous_scale='viridis',
            title=f'Top {top_n_artists} artista po ukupnim streamovima'
        )
        fig2.update_layout(yaxis={'categoryorder': 'total ascending'}, height=500, showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)

    col_left2, col_right2 = st.columns(2)

    with col_left2:
        # Distribucija zanrova
        genre_counts = filtered_df['genre'].value_counts().reset_index()
        genre_counts.columns = ['genre', 'count']
        fig3 = px.pie(
            genre_counts.head(10), values='count', names='genre',
            title='Distribucija žanrova (Top 10)',
            hole=0.35
        )
        fig3.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig3, use_container_width=True)

    with col_right2:
        # Histogram streamova
        fig4 = px.histogram(
            filtered_df, x='streams', nbins=30,
            color='trend',
            color_discrete_map={'Rising': '#2ecc71', 'Falling': '#e74c3c'},
            title='Distribucija streamova',
            marginal='box'
        )
        fig4.add_vline(x=filtered_df['streams'].mean(), line_dash="dash", line_color="red",
                       annotation_text=f"Prosjek: {filtered_df['streams'].mean():,.0f}")
        fig4.add_vline(x=filtered_df['streams'].median(), line_dash="dash", line_color="orange",
                       annotation_text=f"Medijan: {filtered_df['streams'].median():,.0f}")
        st.plotly_chart(fig4, use_container_width=True)

    # Deskriptivna statistika
    st.subheader("Deskriptivna statistika")
    numeric_cols = ['streams', 'stream_change', '7day', 'pos', 'days', 'viral_score',
                    'streams_per_day', 'efficiency_score', 'growth_rate']
    desc = filtered_df[numeric_cols].describe().round(2)
    st.dataframe(desc, use_container_width=True)


# ============================================================================
#  TAB 2: ZANROVI
# ============================================================================

with tab2:
    st.header("Analiza po žanrovima")

    # Metrika za analizu
    metric_option = st.selectbox(
        "Odaberi metriku za analizu",
        ['streams', 'viral_score', 'stream_change', '7day', 'streams_per_day', 'efficiency_score'],
        key="genre_metric"
    )

    agg_option = st.radio("Agregacija", ['Prosjek', 'Ukupno', 'Medijan', 'Maksimum'], horizontal=True, key="genre_agg")
    agg_map = {'Prosjek': 'mean', 'Ukupno': 'sum', 'Medijan': 'median', 'Maksimum': 'max'}

    genre_stats = filtered_df.groupby('genre')[metric_option].agg(agg_map[agg_option]).sort_values(ascending=False).reset_index()
    genre_stats.columns = ['genre', metric_option]

    col1, col2 = st.columns(2)

    with col1:
        fig = px.bar(
            genre_stats.head(15), x=metric_option, y='genre',
            orientation='h', color=metric_option,
            color_continuous_scale='turbo',
            title=f'{agg_option} {metric_option} po žanru (Top 15)'
        )
        fig.update_layout(yaxis={'categoryorder': 'total ascending'}, height=550)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        genre_trend = filtered_df.groupby(['genre', 'trend']).size().reset_index(name='count')
        top_genres = filtered_df['genre'].value_counts().head(12).index
        genre_trend_top = genre_trend[genre_trend['genre'].isin(top_genres)]
        fig2 = px.bar(
            genre_trend_top, x='genre', y='count', color='trend',
            color_discrete_map={'Rising': '#2ecc71', 'Falling': '#e74c3c'},
            title='Rising vs Falling po žanru',
            barmode='group'
        )
        fig2.update_layout(height=550, xaxis_tickangle=-45)
        st.plotly_chart(fig2, use_container_width=True)

    # Box plot po zanrovima
    top_genres_box = filtered_df['genre'].value_counts().head(10).index
    df_top_genres = filtered_df[filtered_df['genre'].isin(top_genres_box)]
    fig3 = px.box(
        df_top_genres, x='genre', y=metric_option,
        color='genre', title=f'Distribucija {metric_option} po top žanrovima',
        points='all'
    )
    fig3.update_layout(height=500, xaxis_tickangle=-45, showlegend=False)
    st.plotly_chart(fig3, use_container_width=True)

    # Tabela zanrova
    st.subheader("Kompletna tabela po žanrovima")
    genre_table = filtered_df.groupby('genre').agg(
        Pjesama=('track_name', 'count'),
        Prosj_streams=('streams', 'mean'),
        Ukupni_streams=('streams', 'sum'),
        Prosj_viral=('viral_score', 'mean'),
        Prosj_change=('stream_change', 'mean'),
        Rising=('trend', lambda x: (x == 'Rising').sum()),
        Falling=('trend', lambda x: (x == 'Falling').sum())
    ).round(0).sort_values('Ukupni_streams', ascending=False)
    st.dataframe(genre_table, use_container_width=True)


# ============================================================================
#  TAB 3: ZEMLJE
# ============================================================================

with tab3:
    st.header("Geografska analiza")

    col1, col2 = st.columns(2)

    with col1:
        country_stats = filtered_df.groupby('country').agg(
            Pjesama=('track_name', 'count'),
            Ukupni_streams=('streams', 'sum'),
            Prosj_streams=('streams', 'mean')
        ).round(0).sort_values('Ukupni_streams', ascending=False).reset_index()

        fig = px.bar(
            country_stats.head(15), x='Ukupni_streams', y='country',
            orientation='h', color='Ukupni_streams',
            color_continuous_scale='plasma',
            hover_data=['Pjesama', 'Prosj_streams'],
            title='Top zemlje po ukupnim streamovima'
        )
        fig.update_layout(yaxis={'categoryorder': 'total ascending'}, height=500)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        country_count = filtered_df['country'].value_counts().reset_index()
        country_count.columns = ['country', 'count']
        fig2 = px.pie(
            country_count.head(10), values='count', names='country',
            title='Distribucija pjesama po zemljama (Top 10)',
            hole=0.35
        )
        st.plotly_chart(fig2, use_container_width=True)

    # Dominantni zanrovi po zemljama
    st.subheader("Dominantni žanrovi po zemljama")
    country_genre = filtered_df.groupby(['country', 'genre']).size().reset_index(name='count')
    top_10_countries = filtered_df['country'].value_counts().head(10).index
    cg_top = country_genre[country_genre['country'].isin(top_10_countries)]

    fig3 = px.bar(
        cg_top, x='country', y='count', color='genre',
        title='Žanrovska kompozicija po top zemljama',
        barmode='stack'
    )
    fig3.update_layout(height=500, xaxis_tickangle=-45)
    st.plotly_chart(fig3, use_container_width=True)

    # Tabela po zemljama
    st.subheader("Kompletna tabela po zemljama")
    country_table = filtered_df.groupby('country').agg(
        Pjesama=('track_name', 'count'),
        Prosj_streams=('streams', 'mean'),
        Ukupni_streams=('streams', 'sum'),
        Prosj_viral=('viral_score', 'mean'),
        Dom_zanr=('genre', lambda x: x.value_counts().index[0]),
        Rising=('trend', lambda x: (x == 'Rising').sum())
    ).round(0).sort_values('Ukupni_streams', ascending=False)
    st.dataframe(country_table, use_container_width=True)


# ============================================================================
#  TAB 4: TRENDOVI
# ============================================================================

with tab4:
    st.header("Trend analiza")

    col1, col2, col3 = st.columns(3)

    rising_df = filtered_df[filtered_df['trend'] == 'Rising']
    falling_df = filtered_df[filtered_df['trend'] == 'Falling']

    with col1:
        st.metric("Rising pjesama", len(rising_df),
                  delta=f"{len(rising_df)/max(len(filtered_df),1)*100:.1f}%")
    with col2:
        st.metric("Falling pjesama", len(falling_df),
                  delta=f"-{len(falling_df)/max(len(filtered_df),1)*100:.1f}%")
    with col3:
        if len(rising_df) > 0 and len(falling_df) > 0:
            diff = rising_df['streams'].mean() - falling_df['streams'].mean()
            st.metric("Razlika prosj. streamova", f"{abs(diff):,.0f}",
                      delta="Rising vodi" if diff > 0 else "Falling vodi")

    col_left, col_right = st.columns(2)

    with col_left:
        # Trend po metrici
        trend_comparison = filtered_df.groupby('trend')[['streams', 'viral_score', 'stream_change', 'days']].mean().round(0)
        fig = go.Figure()
        for col_name in trend_comparison.columns:
            fig.add_trace(go.Bar(name=col_name, x=trend_comparison.index, y=trend_comparison[col_name]))
        fig.update_layout(barmode='group', title='Poređenje Rising vs Falling (prosjeci)', height=450)
        st.plotly_chart(fig, use_container_width=True)

    with col_right:
        # Longevity analiza
        fig2 = px.box(
            filtered_df, x='longevity', y='streams', color='trend',
            color_discrete_map={'Rising': '#2ecc71', 'Falling': '#e74c3c'},
            title='Streamovi po longevity i trendu',
            points='all'
        )
        fig2.update_layout(height=450)
        st.plotly_chart(fig2, use_container_width=True)

    # Popularity category
    col_left2, col_right2 = st.columns(2)

    with col_left2:
        fig3 = px.box(
            filtered_df, x='popularity_category', y='streams', color='popularity_category',
            title='Streamovi po popularity kategoriji',
            points='all'
        )
        fig3.update_layout(height=450, showlegend=False)
        st.plotly_chart(fig3, use_container_width=True)

    with col_right2:
        fig4 = px.box(
            filtered_df, x='longevity', y='viral_score', color='longevity',
            title='Viral score po longevity kategoriji',
            points='all'
        )
        fig4.update_layout(height=450, showlegend=False)
        st.plotly_chart(fig4, use_container_width=True)

    # Longevity tabela
    st.subheader("Statistike po longevity kategoriji")
    longevity_table = filtered_df.groupby('longevity').agg(
        Pjesama=('track_name', 'count'),
        Prosj_streams=('streams', 'mean'),
        Prosj_viral=('viral_score', 'mean'),
        Prosj_dani=('days', 'mean'),
        Rising_pct=('trend', lambda x: f"{(x=='Rising').mean()*100:.1f}%")
    ).round(0).sort_values('Prosj_streams', ascending=False)
    st.dataframe(longevity_table, use_container_width=True)


# ============================================================================
#  TAB 5: KORELACIJE
# ============================================================================

with tab5:
    st.header("Korelaciona analiza")

    numeric_cols_corr = ['streams', 'stream_change', '7day', 'pos', 'days', 'viral_score',
                         'streams_per_day', 'efficiency_score', 'growth_rate']

    selected_corr_cols = st.multiselect(
        "Odaberi varijable za korelacionu matricu",
        numeric_cols_corr,
        default=['streams', 'stream_change', '7day', 'pos', 'days', 'viral_score']
    )

    if len(selected_corr_cols) >= 2:
        corr_matrix = filtered_df[selected_corr_cols].corr().round(3)

        fig = px.imshow(
            corr_matrix,
            text_auto='.3f',
            color_continuous_scale='RdBu_r',
            zmin=-1, zmax=1,
            title='Korelaciona matrica',
            aspect='auto'
        )
        fig.update_layout(height=600)
        st.plotly_chart(fig, use_container_width=True)

        # Rangiranje korelacija
        st.subheader("Rangirane korelacije")
        corr_pairs = []
        for i in range(len(selected_corr_cols)):
            for j in range(i+1, len(selected_corr_cols)):
                corr_pairs.append({
                    'Varijabla 1': selected_corr_cols[i],
                    'Varijabla 2': selected_corr_cols[j],
                    'Korelacija': corr_matrix.iloc[i, j],
                    'Apsolutna': abs(corr_matrix.iloc[i, j]),
                    'Jačina': 'JAKA' if abs(corr_matrix.iloc[i, j]) > 0.7 else 'SREDNJA' if abs(corr_matrix.iloc[i, j]) > 0.4 else 'SLABA'
                })
        corr_df = pd.DataFrame(corr_pairs).sort_values('Apsolutna', ascending=False)
        st.dataframe(corr_df.drop(columns='Apsolutna'), use_container_width=True)

    # Scatter plot - korisnik bira varijable
    st.subheader("Interaktivni scatter plot")
    col1, col2, col3 = st.columns(3)
    with col1:
        x_var = st.selectbox("X osa", numeric_cols_corr, index=0, key="scatter_x")
    with col2:
        y_var = st.selectbox("Y osa", numeric_cols_corr, index=5, key="scatter_y")
    with col3:
        color_var = st.selectbox("Boja po", ['trend', 'longevity', 'popularity_category', 'genre', 'country'], key="scatter_color")

    fig2 = px.scatter(
        filtered_df, x=x_var, y=y_var, color=color_var,
        hover_data=['track_name', 'artist_name', 'genre', 'streams'],
        title=f'{x_var} vs {y_var}',
        trendline='ols',
        opacity=0.7, size_max=15
    )
    fig2.update_layout(height=600)
    st.plotly_chart(fig2, use_container_width=True)


# ============================================================================
#  TAB 6: NAPREDNA ANALIZA
# ============================================================================

with tab6:
    st.header("Napredna analiza")

    analysis_type = st.selectbox(
        "Odaberi analizu",
        ["Outlier detekcija (IQR)", "Pareto analiza", "Pivot analiza", "Feature Engineering - Top liste"]
    )

    if analysis_type == "Outlier detekcija (IQR)":
        st.subheader("Outlier detekcija - IQR metoda")

        outlier_col = st.selectbox("Kolona za analizu", ['streams', 'viral_score', 'stream_change', '7day', 'days'])

        Q1 = filtered_df[outlier_col].quantile(0.25)
        Q3 = filtered_df[outlier_col].quantile(0.75)
        IQR = Q3 - Q1
        lower = Q1 - 1.5 * IQR
        upper = Q3 + 1.5 * IQR

        outliers = filtered_df[(filtered_df[outlier_col] < lower) | (filtered_df[outlier_col] > upper)]
        normal = filtered_df[(filtered_df[outlier_col] >= lower) & (filtered_df[outlier_col] <= upper)]

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Q1", f"{Q1:,.0f}")
        with col2:
            st.metric("Q3", f"{Q3:,.0f}")
        with col3:
            st.metric("IQR", f"{IQR:,.0f}")
        with col4:
            st.metric("Outlier-a", len(outliers))

        st.markdown(f"**Donja granica:** {lower:,.0f} | **Gornja granica:** {upper:,.0f}")

        fig = go.Figure()
        fig.add_trace(go.Box(y=filtered_df[outlier_col], name=outlier_col, boxpoints='all',
                             marker_color='#3498db', jitter=0.3, pointpos=-1.8))
        fig.add_hline(y=upper, line_dash="dash", line_color="red", annotation_text=f"Gornja granica: {upper:,.0f}")
        fig.add_hline(y=lower, line_dash="dash", line_color="red", annotation_text=f"Donja granica: {lower:,.0f}")
        fig.update_layout(title=f'Box plot sa outlier granicama - {outlier_col}', height=500)
        st.plotly_chart(fig, use_container_width=True)

        if len(outliers) > 0:
            st.subheader(f"Outlier-i ({len(outliers)} pronađeno)")
            st.dataframe(
                outliers[['track_name', 'artist_name', outlier_col, 'genre', 'trend', 'longevity']]
                .sort_values(outlier_col, ascending=False),
                use_container_width=True
            )

    elif analysis_type == "Pareto analiza":
        st.subheader("Pareto analiza (Pravilo 80/20)")

        pareto_by = st.radio("Grupiši po", ['artist_name', 'genre', 'country'], horizontal=True)
        pareto_metric = st.selectbox("Metrika", ['streams', 'viral_score', '7day'], key="pareto_metric")

        group_totals = filtered_df.groupby(pareto_by)[pareto_metric].sum().sort_values(ascending=False).reset_index()
        group_totals.columns = [pareto_by, pareto_metric]
        total = group_totals[pareto_metric].sum()
        group_totals['procenat'] = group_totals[pareto_metric] / total * 100
        group_totals['kumulativni_pct'] = group_totals['procenat'].cumsum()

        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(
            go.Bar(x=group_totals[pareto_by].head(20), y=group_totals[pareto_metric].head(20),
                   name=pareto_metric, marker_color='#3498db'),
            secondary_y=False
        )
        fig.add_trace(
            go.Scatter(x=group_totals[pareto_by].head(20), y=group_totals['kumulativni_pct'].head(20),
                       name='Kumulativni %', marker_color='#e74c3c', mode='lines+markers'),
            secondary_y=True
        )
        fig.add_hline(y=80, line_dash="dash", line_color="orange",
                      annotation_text="80% linija", secondary_y=True)
        fig.update_layout(title=f'Pareto analiza: {pareto_metric} po {pareto_by}', height=550,
                          xaxis_tickangle=-45)
        fig.update_yaxes(title_text=pareto_metric, secondary_y=False)
        fig.update_yaxes(title_text="Kumulativni %", secondary_y=True)
        st.plotly_chart(fig, use_container_width=True)

        n_groups = len(group_totals)
        top_20_n = max(1, int(n_groups * 0.2))
        top_20_pct = group_totals.head(top_20_n)['procenat'].sum()

        st.info(f"**Rezultat:** Top 20% ({top_20_n} od {n_groups}) generiše **{top_20_pct:.1f}%** ukupnih {pareto_metric}")

        st.dataframe(group_totals.head(20), use_container_width=True)

    elif analysis_type == "Pivot analiza":
        st.subheader("Dvodimenzionalna pivot analiza")

        col1, col2, col3 = st.columns(3)
        with col1:
            pivot_index = st.selectbox("Redovi (index)", ['genre', 'country', 'longevity', 'popularity_category'], key="piv_idx")
        with col2:
            pivot_columns = st.selectbox("Kolone", ['trend', 'longevity', 'popularity_category', 'genre'], index=0, key="piv_col")
        with col3:
            pivot_values = st.selectbox("Vrijednosti", ['streams', 'viral_score', 'stream_change', '7day'], key="piv_val")

        pivot_agg = st.radio("Agregacija", ['Prosjek', 'Ukupno', 'Broj', 'Medijan'], horizontal=True, key="piv_agg")
        agg_map_pivot = {'Prosjek': 'mean', 'Ukupno': 'sum', 'Broj': 'count', 'Medijan': 'median'}

        pivot = filtered_df.pivot_table(
            values=pivot_values, index=pivot_index, columns=pivot_columns,
            aggfunc=agg_map_pivot[pivot_agg], fill_value=0
        ).round(0)

        fig = px.imshow(
            pivot, text_auto='.0f',
            color_continuous_scale='YlOrRd',
            title=f'Pivot: {pivot_agg} {pivot_values} po {pivot_index} × {pivot_columns}',
            aspect='auto'
        )
        fig.update_layout(height=max(400, len(pivot) * 30))
        st.plotly_chart(fig, use_container_width=True)

        st.dataframe(pivot, use_container_width=True)

    elif analysis_type == "Feature Engineering - Top liste":
        st.subheader("Top liste po izvedenim metrikama")

        fe_metric = st.selectbox("Metrika", ['streams_per_day', 'efficiency_score', 'growth_rate', 'weekly_avg'])
        top_n_fe = st.slider("Broj rezultata", 5, 50, 15, key="fe_top_n")

        top_fe = filtered_df.nlargest(top_n_fe, fe_metric)
        fig = px.bar(
            top_fe, x=fe_metric, y='track_name', color='trend',
            color_discrete_map={'Rising': '#2ecc71', 'Falling': '#e74c3c'},
            orientation='h',
            hover_data=['artist_name', 'genre', 'streams', 'days', 'viral_score'],
            title=f'Top {top_n_fe} pjesama po {fe_metric}'
        )
        fig.update_layout(yaxis={'categoryorder': 'total ascending'}, height=max(400, top_n_fe * 28))
        st.plotly_chart(fig, use_container_width=True)

        st.dataframe(
            top_fe[['track_name', 'artist_name', fe_metric, 'streams', 'days', 'viral_score', 'trend', 'genre']],
            use_container_width=True
        )


# ============================================================================
#  TAB 7: PRETRAGA
# ============================================================================

with tab7:
    st.header("Pretraga pjesama i artista")

    search_type = st.radio("Pretraži po", ['Pjesma', 'Artist', 'Žanr'], horizontal=True)

    if search_type == 'Pjesma':
        search_term = st.text_input("Unesi naziv pjesme (ili dio naziva)")
        if search_term:
            results = filtered_df[filtered_df['track_name'].str.contains(search_term, case=False, na=False)]
            st.markdown(f"**Pronađeno:** {len(results)} rezultata")
            if len(results) > 0:
                for _, row in results.iterrows():
                    with st.expander(f"🎵 {row['track_name']} - {row['artist_name']}"):
                        c1, c2, c3, c4 = st.columns(4)
                        c1.metric("Streams", f"{row['streams']:,.0f}")
                        c2.metric("Viral Score", f"{row['viral_score']:,.0f}")
                        c3.metric("Stream Change", f"{row['stream_change']:+,.0f}")
                        c4.metric("Pozicija", f"#{int(row['pos'])}")
                        c5, c6, c7, c8 = st.columns(4)
                        c5.metric("Žanr", row['genre'])
                        c6.metric("Zemlja", row['country'])
                        c7.metric("Trend", row['trend'])
                        c8.metric("Dani na listi", int(row['days']))

    elif search_type == 'Artist':
        search_term = st.text_input("Unesi ime artista (ili dio imena)")
        if search_term:
            results = filtered_df[filtered_df['artist_name'].str.contains(search_term, case=False, na=False)]
            st.markdown(f"**Pronađeno:** {len(results)} pjesama")
            if len(results) > 0:
                # Artist summary
                total = results['streams'].sum()
                avg = results['streams'].mean()
                st.markdown(f"**Ukupni streamovi:** {total:,.0f} | **Prosječni po pjesmi:** {avg:,.0f}")

                fig = px.bar(
                    results.sort_values('streams', ascending=True),
                    x='streams', y='track_name', orientation='h',
                    color='trend',
                    color_discrete_map={'Rising': '#2ecc71', 'Falling': '#e74c3c'},
                    hover_data=['viral_score', 'days', 'genre'],
                    title=f'Pjesme artista koji sadrži "{search_term}"'
                )
                fig.update_layout(height=max(300, len(results) * 35))
                st.plotly_chart(fig, use_container_width=True)

                st.dataframe(results[['track_name', 'artist_name', 'streams', 'viral_score',
                                      'stream_change', 'trend', 'genre', 'days']].sort_values('streams', ascending=False),
                             use_container_width=True)

    elif search_type == 'Žanr':
        selected_genre = st.selectbox("Odaberi žanr", sorted(filtered_df['genre'].unique()))
        genre_data = filtered_df[filtered_df['genre'] == selected_genre]

        if len(genre_data) > 0:
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Pjesama", len(genre_data))
            c2.metric("Prosj. streams", f"{genre_data['streams'].mean():,.0f}")
            c3.metric("Rising", len(genre_data[genre_data['trend'] == 'Rising']))
            c4.metric("Prosj. viral", f"{genre_data['viral_score'].mean():,.0f}")

            fig = px.bar(
                genre_data.sort_values('streams', ascending=True),
                x='streams', y='track_name', orientation='h',
                color='trend',
                color_discrete_map={'Rising': '#2ecc71', 'Falling': '#e74c3c'},
                hover_data=['artist_name', 'viral_score', 'days'],
                title=f'Sve pjesme žanra: {selected_genre}'
            )
            fig.update_layout(height=max(300, len(genre_data) * 35))
            st.plotly_chart(fig, use_container_width=True)


# ============================================================================
#  TAB 8: DATASET
# ============================================================================

with tab8:
    st.header("Kompletan dataset")

    # Sortiranje
    sort_col = st.selectbox("Sortiraj po", df.columns, index=2, key="sort_col")
    sort_order = st.radio("Redoslijed", ['Opadajuće', 'Rastuće'], horizontal=True)

    sorted_df = filtered_df.sort_values(sort_col, ascending=(sort_order == 'Rastuće'))

    st.markdown(f"Prikazano **{len(sorted_df)}** od **{len(df)}** pjesama (filtrirano)")

    st.dataframe(sorted_df, use_container_width=True, height=600)

    # Download
    csv = sorted_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="⬇️ Preuzmi filtrirane podatke (CSV)",
        data=csv,
        file_name="spotify_filtered.csv",
        mime="text/csv"
    )
