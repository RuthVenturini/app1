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
    # ============================================================
# EXECUÇÃO DA PESQUISA
# ============================================================

if buscar:

    st.subheader("🔎 Consultando Google News RSS")

    barra = st.progress(0)

    status = st.empty()

    todas_noticias = []

    total_temas = len(PALAVRAS)

    for indice, palavra in enumerate(PALAVRAS):

        status.info(f"Pesquisando: **{palavra}**")

        try:

            df = buscar_google_news(
                palavra,
                quantidade
            )

            if not df.empty:

                todas_noticias.append(df)

        except Exception as erro:

            st.warning(
                f"Erro ao pesquisar '{palavra}': {erro}"
            )

        barra.progress((indice + 1) / total_temas)

    status.empty()

    # --------------------------------------------------------
    # Consolidação
    # --------------------------------------------------------

    if len(todas_noticias) == 0:

        st.warning("Nenhuma notícia encontrada.")

    else:

        df_final = pd.concat(
            todas_noticias,
            ignore_index=True
        )

        # Remove notícias repetidas
        df_final.drop_duplicates(
            subset=["Link"],
            inplace=True
        )

        # Ordenação
        df_final.sort_values(
            by="Data",
            ascending=False,
            inplace=True
        )

        # ----------------------------------------------------
        # Estatísticas
        # ----------------------------------------------------

        st.success(
            f"Foram encontradas **{len(df_final)} notícias**."
        )

        c1, c2, c3 = st.columns(3)

        c1.metric(
            "Notícias",
            len(df_final)
        )

        c2.metric(
            "Temas pesquisados",
            len(PALAVRAS)
        )

        c3.metric(
            "Ano selecionado",
            ano
        )

        st.divider()

        # ----------------------------------------------------
        # Visualização
        # ----------------------------------------------------

        st.subheader("Primeiras 20 notícias")

        st.dataframe(

            df_final.head(20),

            use_container_width=True,

            hide_index=True

        )

        # ----------------------------------------------------
        # Download CSV
        # ----------------------------------------------------

        csv = df_final.to_csv(
            index=False
        ).encode("utf-8")

        st.download_button(

            "📥 Baixar todas as notícias (CSV)",

            csv,

            file_name=f"noticias_google_{ano}.csv",

            mime="text/csv",

            use_container_width=True

        )

        # ----------------------------------------------------
        # Informações
        # ----------------------------------------------------

        with st.expander("ℹ️ Sobre esta busca"):

            st.write("""

Esta versão utiliza o **Google News RSS**.

As notícias representam os resultados disponibilizados
pelo Google News no momento da consulta.

O ano selecionado é mantido para compatibilidade com
as próximas versões do projeto, que utilizarão uma
base histórica de notícias.

""")
