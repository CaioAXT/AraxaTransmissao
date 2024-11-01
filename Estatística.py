#region Bibliotecas
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import dash
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
#endregion

#region Definir Configurações de página
st.set_page_config(layout="wide", page_title="Trabalho de Estatística", page_icon="📊", )
app = dash.Dash(__name__,external_stylesheets=[dbc.themes.LUX])
#endregion

#region Definir Base de Dados
df = pd.read_csv("Spotify Most Streamed Songs.csv", sep=',', encoding='latin-1')
df = df.drop(index=0)
df['streams'] = pd.to_numeric(df['streams'], errors='coerce')
df["released_year"] = pd.to_numeric(df["released_year"], errors='coerce')
df["released_month"] = pd.to_numeric(df["released_month"], errors='coerce')
df["released_day"] = pd.to_numeric(df["released_day"], errors='coerce')
df = df.dropna(subset=['streams'])
#endregion

#region Tratamento de Dados

df["Data de Lançamento"] = pd.to_datetime(df["released_year"].astype(str) + "-" + df["released_month"].astype(str), format="%Y-%m", errors='coerce')
df_agrupado = df.groupby(df["Data de Lançamento"].dt.to_period("M")).agg({"streams": "sum"}).reset_index()
df_agrupado["Data de Lançamento"] = df_agrupado["Data de Lançamento"].dt.to_timestamp()

anos_disponiveis = sorted(df_agrupado["Data de Lançamento"].dt.year.unique())

df_expanded = df.assign(artist_name=df['artist(s)_name'].str.split(',')).explode('artist_name')
df_expanded['artist_name'] = df_expanded['artist_name'].str.strip()
df_expanded = df_expanded[["artist_name"]].sort_values("artist_name")

#endregion

#region Barra Lateral
st.sidebar.image("Logo_IFSC_ParaVideoaula-1024x1024.png",width=200)
ano_selecionado = st.sidebar.slider("Selecione o ano de lançamento",min_value=min(anos_disponiveis),
                                                                    max_value=max(anos_disponiveis), 
                                                                    value=(min(anos_disponiveis), 
                                                                           max(anos_disponiveis)),
                                                                    step=1)
mes_inicio, mes_fim = st.sidebar.slider(
    "Selecione o mês de lançamento",
    min_value=1, max_value=12,
    value=(1, 7),
    format="Mês %d"
)
artista = st.sidebar.multiselect("Selecione o(s) artista(s)", df_expanded["artist_name"].unique())
#endregion

#region Filtros na base de dados
top = df
top = df[df['artist(s)_name'].apply(lambda x: any(art in x for art in artista))]
top = top.nlargest(10, 'streams')
top['streams'] = top['streams'].apply(lambda x: f'{x:,.2f}')

top = top[
    (top["Data de Lançamento"].dt.year >= ano_selecionado[0]) &
    (top["Data de Lançamento"].dt.year <= ano_selecionado[1]) &
    (top["Data de Lançamento"].dt.month >= mes_inicio) &
    (top["Data de Lançamento"].dt.month <= mes_fim)
]
#endregion

st.title("Trabalho de Estatística")
"""Autoria: Caio Rodrigues Alves"""
"""Professor: Adriano Vitor"""
st.subheader("Músicas mais famosas nos serviços de streaming")

"""Essa base de dados foi retirada de https://www.kaggle.com/datasets/abdulszz/spotify-most-streamed-songs"""
"""Vídeo de Explicação: https://www.kaggle.com/code/abdulszz/spotify-most-streamed-songs/notebook"""
'''Este conjunto de dados contém informações abrangentes sobre algumas das músicas mais transmitidas no Spotify, enriquecidas com informações adicionais de outras plataformas populares de streaming, como Apple Music, Deezer e Shazam. Sendo um apaixonado por programação e um entusiasta de aprendizado de máquina, foi uma ótima experiência realizar esse trabalho.'''

#region Grafico Top 10 musicas mais ouvidas
fig = px.bar(top, x='track_name', y='streams', text='streams', labels={'x': 'Música', 'y': 'Quantidade de Streams'})
fig.update_layout(title='Top 10 musicas mais ouvidas', xaxis_title='Música', yaxis_title='Quantidade de Streams')
st.plotly_chart(fig)
#endregion

#region Grafico de linha das Playlists por Artista
fig = go.Figure(data=[  go.Scatter(x=top['track_name'], y=top['in_spotify_playlists'], name="Spotify"),
                        go.Scatter(x=top['track_name'], y=top['in_deezer_playlists'], name="Deezer"),
                        go.Scatter(x=top['track_name'], y=top['in_apple_playlists'], name="Apple Music")])
fig.update_layout(title='Músicas mais ouvidas por plataforma', xaxis_title='Música', yaxis_title='Número de playlists')
st.plotly_chart(fig)
#endregion

#region Streams por mês de lançamento
fig = px.line(top, x="Data de Lançamento", y="streams", 
              title=f"Streams Mensais das Músicas Lançadas em {ano_selecionado} ({mes_inicio} até {mes_fim})")
fig.update_layout(xaxis_title="Mês", yaxis_title="Streams")
st.plotly_chart(fig)
#endregion

#region Gráficos de Pizza
col1, col2 = st.columns([1, 1])

with col1:
    fig = px.pie(top.assign(grupo=top["danceability_%"] // 5 * 5), names="grupo", color="grupo", color_discrete_map={i:f"rgba({i},{i},{i},{i/100*255})" for i in range(0, 101, 5)}, title="Gêneros de Músicas Dançantes")
    st.plotly_chart(fig)
    
    fig = px.pie(top.assign(grupo=top["energy_%"] // 5 * 5), names="grupo", color="grupo", color_discrete_map={i:f"rgba({i},{i},{i},{i/100*255})" for i in range(0, 101, 5)}, title="Gêneros de Músicas Dançantes")
    st.plotly_chart(fig)
    
with col2:
    fig = px.pie(top.assign(grupo=top["acousticness_%"] // 5 * 5), names="grupo", color="grupo", color_discrete_map={i:f"rgba({i},{i},{i},{i/100*255})" for i in range(0, 101, 5)}, title="Trecho de Instrumental na música")
    st.plotly_chart(fig)
    
    fig = px.pie(top.assign(grupo=top["bpm"] // 10 * 10), names="grupo", color="grupo", color_discrete_map={i:f"rgba({i},{i},{i},{i/100*255})" for i in range(0, 101, 5)}, title="BPM da Música")
    st.plotly_chart(fig)
#endregion

#region Tabela Top 10 Músicas 
'''Top 10 músicas mais ouvidas'''
st.table(top[["track_name", "artist(s)_name", "streams"]])
#endregion

