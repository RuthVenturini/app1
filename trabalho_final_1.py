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
import plotly.express as px
from urllib.parse import quote_plus
import geopandas as gpd
import matplotlib.pyplot as plt

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

""")

st.markdown("---")

# --------------------------------------------------------
# Barra lateral
# --------------------------------------------------------

st.sidebar.header("Pesquisa")

# --------------------------------------------------------
# Palavras-chave
# --------------------------------------------------------

TEMAS = {
    "Violência contra a mulher": "violência contra mulher",
    "Violência doméstica": "violência doméstica",
    "Feminicídio": "feminicídio",
    "Lei Maria da Penha": '"Lei Maria da Penha"',
    "Violência sexual": "violência sexual",
    "Assédio": "assédio contra mulher",
    "Agressão": "agressão contra mulher",
    "Violência psicológica": "violência psicológica mulher",
    "Violência patrimonial": "violência patrimonial mulher",
    "Violência moral": "violência moral mulher"
}

st.sidebar.selectbox(
    "Fonte de dados",
    ["Google News RSS"],
    index=0
)

st.sidebar.selectbox(
    "Idioma",
    ["Português"],
    index=0
)

temas_escolhidos = st.sidebar.multiselect(
    "Tipos de violência",
    options=list(TEMAS.keys()),
    default=[
        "Violência contra a mulher",
        "Violência doméstica",
        "Feminicídio"
    ]
)

# --------------------------------------------------------
# Quantidade
# --------------------------------------------------------

buscar = st.sidebar.button(
    "🔎 Buscar Notícias",
    use_container_width=True
)

# --------------------------------------------------------
# Área principal
# --------------------------------------------------------

c1, c2, c3 = st.columns(3)

c1.metric("Fonte", "Google News RSS")
c2.metric("Temas", len(temas_escolhidos))
c3.metric("Status", "Pronto")

st.divider()

# ============================================================
# Constantes e Funções Globais
# ============================================================

ESTADOS = [
    "Acre", "Alagoas", "Amapá", "Amazonas", "Bahia", "Ceará",
    "Distrito Federal", "Espírito Santo", "Goiás", "Maranhão",
    "Mato Grosso", "Mato Grosso do Sul", "Minas Gerais", "Pará",
    "Paraíba", "Paraná", "Pernambuco", "Piauí", "Rio de Janeiro",
    "Rio Grande do Norte", "Rio Grande do Sul", "Rondônia",
    "Roraima", "Santa Catarina", "São Paulo", "Sergipe", "Tocantins"
]

def localizar_estado(texto):
    texto = str(texto).lower()
    for estado in ESTADOS:
        if estado.lower() in texto:
            return estado
    return None

@st.cache_data(show_spinner=False)
def buscar_google_news(consulta):
    """
    Pesquisa notícias utilizando Google News RSS.
    """
    tema = consulta
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

    for noticia in feed.entries:
        noticias.append({
            "Tema": tema,
            "Título": noticia.get("title", ""),
            "Resumo": noticia.get("summary",""),
            "Data": noticia.get("published", ""),
            "Link": noticia.get("link", "")
        })

    return pd.DataFrame(noticias)

# ============================================================
# EXECUÇÃO DA PESQUISA
# ============================================================

if buscar:

    if len(temas_escolhidos) == 0:
        st.warning("Selecione pelo menos um tipo de violência.")
        st.stop()

    st.subheader("🔎 Consultando Google News RSS")

    barra = st.progress(0)
    status = st.empty()
    consultas = [TEMAS[t] for t in temas_escolhidos]
    todas_noticias = []
    total_temas = len(consultas)

    for indice, palavra in enumerate(consultas):
        status.info(f"Pesquisando: **{palavra}**")
        try:
            df = buscar_google_news(palavra)
            if not df.empty:
                todas_noticias.append(df)
        except Exception as erro:
            st.warning(f"Erro ao pesquisar '{palavra}': {erro}")

        barra.progress((indice + 1) / total_temas)

    status.empty()
    barra.empty()

    # --------------------------------------------------------
    # Consolidação
    # --------------------------------------------------------

    if len(todas_noticias) == 0:
        st.warning("Nenhuma notícia encontrada.")
    else:
        df_final = pd.concat(todas_noticias, ignore_index=True)
        df_final.reset_index(drop=True, inplace=True)
        df_final.drop_duplicates(subset=["Link"], inplace=True)
        df_final.reset_index(drop=True, inplace=True)
        
        # Extrair o portal a partir do título
        df_final["Portal"] = (
            df_final["Título"]
            .str.extract(r"[-|—]\s*(.+)$", expand=False)
            .fillna("Não identificado")
        )
        
        # Limpar o título (remover o nome do portal)
        df_final["Título"] = (
            df_final["Título"]
            .str.replace(r"\s*[-|—]\s*.+$", "", regex=True)
        )

        # Conversão da data
        df_final["Data"] = pd.to_datetime(df_final["Data"], errors="coerce", utc=True)
        df_final["Ano"] = df_final["Data"].dt.year

        # Identificação de Estados
        df_final["Estado"] = (
            df_final["Título"].fillna("") + " " + df_final["Resumo"].fillna("")
        ).apply(localizar_estado)

        ocorrencias = (
            df_final
            .dropna(subset=["Estado"])
            .groupby("Estado")
            .size()
            .reset_index(name="Ocorrências")
        )
        
        # Salva o DataFrame para reutilização fora do if principal
        st.session_state["df_final"] = df_final
        st.session_state["ocorrencias"] = ocorrencias

        # ----------------------------------------------------
        # Estatísticas
        # ----------------------------------------------------

        st.success(f"Foram encontradas **{len(df_final)} notícias**.")

        c1, c2, c3 = st.columns(3)
        c1.metric("Notícias", len(df_final))
        c2.metric("Temas pesquisados", len(temas_escolhidos))
        c3.metric("Portais", df_final["Portal"].nunique())

        st.divider()

        # ----------------------------------------------------
        # Visualização
        # ----------------------------------------------------

        st.subheader("Primeiras 20 notícias")
        st.dataframe(
            df_final[["Tema", "Data", "Portal", "Resumo", "Título", "Link"]].head(20),
            use_container_width=True,
            hide_index=True
        )

        # ----------------------------------------------------
        # Download CSV
        # ----------------------------------------------------

        csv = df_final.to_csv(index=False).encode("utf-8")

        st.download_button(
            "📥 Baixar todas as notícias (CSV)",
            csv,
            file_name="noticias_google.csv",
            mime="text/csv",
            use_container_width=True
        )

# ============================================================
# Análises em Sessão (fora do botão Buscar)
# ============================================================

if "df_final" in st.session_state and "ocorrencias" in st.session_state:

    df_final = st.session_state["df_final"]
    ocorrencias = st.session_state["ocorrencias"]
    
    st.divider()
    st.header("📊 Análises e Espacialização")

    col1, col2, col3 = st.columns(3)
        
    with col1:
        grafico_ano = st.button("📈 Notícias por ano", use_container_width=True)
        
    with col2:
        grafico_tema = st.button("📊 Notícias por tema", use_container_width=True)
        
    with col3:
        gerar_mapa = st.button("🗺️ Gerar mapa", use_container_width=True)
        
    # ----------------------------------------------------
    # Primeiro gráfico (Pizza)
    # ----------------------------------------------------
            
    if grafico_ano:
        dados = (
            df_final
            .groupby("Ano")
            .size()
            .reset_index(name="Quantidade")
        )
            
        fig = px.pie(
            dados,
            names="Ano",
            values="Quantidade",
            title="Distribuição das notícias por ano"
        )
            
        st.plotly_chart(fig, use_container_width=True)
            
    # ----------------------------------------------------
    # Segundo gráfico (Barras)
    # ----------------------------------------------------
            
    if grafico_tema:
        dados = (
            df_final
            .groupby(["Tema", "Ano"])
            .size()
            .reset_index(name="Quantidade")
        )
            
        fig = px.bar(
            dados,
            x="Tema",
            y="Quantidade",
            color="Ano",
            barmode="stack",
            text_auto=True,
            title="Quantidade de notícias por tema"
        )
            
        st.plotly_chart(fig, use_container_width=True)

    # ----------------------------------------------------
    # Mapa Temático
    # ----------------------------------------------------
    
    if gerar_mapa:
        try:
            url_github = "https://github.com/RuthVenturini/app1/blob/main/BR_UF_2024.zip"
            # Lê o shapefile/zip oficial
            uf = gpd.read_file("url_github")
            
            # Faz o join espacial usando o nome do estado (coluna NM_UF padrão do IBGE)
            mapa = uf.merge(
                ocorrencias,
                left_on="NM_UF",
                right_on="Estado",
                how="left"
            )
            
            mapa["Ocorrências"] = mapa["Ocorrências"].fillna(0)
    
            fig, ax = plt.subplots(figsize=(10, 10))
            mapa.plot(
                column="Ocorrências",
                cmap="Reds",
                linewidth=0.8,
                edgecolor="black",
                legend=True,
                legend_kwds={'label': "Número de Notícias", 'orientation': "horizontal"},
                ax=ax
            )
            
            ax.set_title("Violência contra a mulher: Menções por Estado", fontdict={'fontsize': 14})
            ax.axis("off")
            st.pyplot(fig)
            
        except FileNotFoundError:
            st.error("Erro: Arquivo cartográfico não encontrado. Certifique-se de que o arquivo 'BR_UF_2024.zip' (padrão IBGE) está salvo na pasta 'dados/'.")
        except Exception as e:
            st.error(f"Erro ao gerar o mapa: {e}")

# ----------------------------------------------------
# Informações
# ----------------------------------------------------

with st.expander("ℹ️ Sobre esta busca"):
    st.write(
        """
Esta versão utiliza o **Google News RSS**.

Os resultados correspondem às notícias
disponibilizadas pelo Google News no momento
da consulta.

Próximas etapas do projeto:

- Processamento de Linguagem Natural (PLN)
- Identificação automática do estado citado
- Estatísticas
- Gráficos
- Mapa temático
"""
    )
