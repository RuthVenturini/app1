# ============================================================
# Agente IA
# Violência contra a Mulher no Brasil
#
# Versão 1.0 - Parte 1
# Interface + Busca Google News RSS
# ============================================================

import streamlit as st
import pandas as pd
import feedparser
from urllib.parse import quote_plus

# --------------------------------------------------------
# Configuração da página
# --------------------------------------------------------

st.set_page_config(
    page_title="Agente IA - Violência contra a Mulher",
    page_icon="📰",
    layout="wide"
)

# --------------------------------------------------------
# Cabeçalho
# --------------------------------------------------------

st.title("📰 Agente IA - Violência contra a Mulher no Brasil")

st.info("""
Protótipo desenvolvido para pesquisa de notícias relacionadas
à violência contra a mulher.

**Fonte utilizada nesta versão**

Google News RSS

**Observação**

Esta versão é um protótipo. O ano selecionado é utilizado
para manter compatibilidade com a arquitetura do projeto,
mas a pesquisa depende dos resultados disponibilizados
pelo Google News.
""")

st.markdown("---")

# --------------------------------------------------------
# Barra lateral
# --------------------------------------------------------

st.sidebar.header("Pesquisa")

ANOS = list(range(2015, 2027))

ano = st.sidebar.selectbox(
    "Ano",
    ANOS,
    index=len(ANOS)-1
)

# --------------------------------------------------------
# Palavras-chave
# --------------------------------------------------------

PALAVRAS = [

    "violência contra mulher",

    "violência doméstica",

    "feminicídio",

    "Lei Maria da Penha",

    "violência sexual"

]

st.sidebar.markdown("### Temas pesquisados")

for palavra in PALAVRAS:

    st.sidebar.write(f"• {palavra}")

# --------------------------------------------------------
# Quantidade
# --------------------------------------------------------

quantidade = st.sidebar.selectbox(

    "Máximo de notícias por tema",

    [10,20,30,50],

    index=1

)

buscar = st.sidebar.button(

    "🔎 Buscar Notícias",

    use_container_width=True

)

# --------------------------------------------------------
# Área principal
# --------------------------------------------------------

c1,c2,c3 = st.columns(3)

c1.metric(

    "Ano",

    ano

)

c2.metric(

    "Fonte",

    "Google News RSS"

)

c3.metric(

    "Temas",

    len(PALAVRAS)

)

st.divider()

# ============================================================
# Função de busca
# ============================================================

def buscar_google_news(consulta, quantidade=20):

    """
    Pesquisa notícias utilizando Google News RSS.
    """

    consulta = quote_plus(consulta)

    url = (
        "https://news.google.com/rss/search?"
        f"q={consulta}"
        "&hl=pt-BR"
        "&gl=BR"
        "&ceid=BR:pt-419"
    )

    feed = feedparser.parse(url)

    noticias = []

    for noticia in feed.entries[:quantidade]:

        noticias.append({

            "Tema": consulta,

            "Título": noticia.get("title",""),

            "Data": noticia.get("published",""),

            "Link": noticia.get("link","")

        })

    return pd.DataFrame(noticias)
