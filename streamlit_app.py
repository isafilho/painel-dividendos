import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# ==========================================
# CONFIGURAÇÃO
# ==========================================

YIELD_MINIMO = 0.06  # 6%

st.set_page_config(
    page_title="Painel Dividendos",
    layout="wide"
)

# ==========================================
# FUNÇÕES
# ==========================================

@st.cache_data(ttl=300)
def obter_cotacao(ticker):
    """
    Obtém a cotação atual do Yahoo Finance.
    Atualiza a cada 5 minutos.
    """

    try:
        ativo = yf.Ticker(f"{ticker}.SA")

        info = ativo.fast_info

        return {
            "preco": round(info["lastPrice"], 2),
            "abertura": round(info["open"], 2),
            "maxima": round(info["dayHigh"], 2),
            "minima": round(info["dayLow"], 2),
            "volume": info.get("lastVolume", 0)
        }

    except Exception as e:
        st.error(f"Erro ao obter cotação: {e}")
        return None


@st.cache_data(ttl=3600)
def obter_historico(ticker):

    dados = yf.download(
        f"{ticker}.SA",
        period="1y",
        auto_adjust=True,
        progress=False
    )

    return dados


def calcular_pt(dividendo_anual):
    return dividendo_anual / YIELD_MINIMO


def calcular_margem_seguranca(pt_medio, cotacao):
    return ((pt_medio / cotacao) - 1) * 100


# ==========================================
# INTERFACE
# ==========================================

st.title("📈 Painel de Dividendos")

ticker = st.text_input(
    "Ticker",
    value="TAEE4"
).upper()

col1, col2 = st.columns([1, 3])

with col1:

    dividendo_medio = st.number_input(
        "Dividendo Médio Anual",
        value=1.24,
        step=0.01
    )

    dividendo_projetivo = st.number_input(
        "Dividendo Projetivo",
        value=1.22,
        step=0.01
    )

# ==========================================
# DADOS
# ==========================================

cotacao_info = obter_cotacao(ticker)

if cotacao_info:

    cotacao = cotacao_info["preco"]

    pt_medio = calcular_pt(dividendo_medio)
    pt_projetivo = calcular_pt(dividendo_projetivo)

    dy_medio = (dividendo_medio / cotacao) * 100
    dy_projetivo = (dividendo_projetivo / cotacao) * 100

    margem = calcular_margem_seguranca(
        pt_medio,
        cotacao
    )

    # ======================================
    # CARDS
    # ======================================

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Cotação Atual",
        f"R$ {cotacao:.2f}"
    )

    c2.metric(
        "PT Médio",
        f"R$ {pt_medio:.2f}"
    )

    c3.metric(
        "PT Projetivo",
        f"R$ {pt_projetivo:.2f}"
    )

    c4, c5, c6 = st.columns(3)

    c4.metric(
        "DY Médio",
        f"{dy_medio:.2f}%"
    )

    c5.metric(
        "DY Projetivo",
        f"{dy_projetivo:.2f}%"
    )

    c6.metric(
        "Margem Segurança",
        f"{margem:.2f}%"
    )

    st.divider()

    # ======================================
    # STATUS
    # ======================================

    if cotacao < pt_projetivo:
        st.success(
            "✅ Oportunidade à vista! "
            "Cotação abaixo do PT Médio e PT Projetivo."
        )

    elif cotacao < pt_medio:
        st.warning(
            "⚠️ Cotação abaixo apenas do PT Médio."
        )

    else:
        st.error(
            "❌ Cotação acima dos preços teto."
        )

    # ======================================
    # GRÁFICO COMPARATIVO
    # ======================================

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=[
                "Cotação",
                "PT Médio",
                "PT Projetivo"
            ],
            y=[
                cotacao,
                pt_medio,
                pt_projetivo
            ],
            text=[
                f"R$ {cotacao:.2f}",
                f"R$ {pt_medio:.2f}",
                f"R$ {pt_projetivo:.2f}"
            ],
            textposition="outside"
        )
    )

    fig.update_layout(
        title=f"{ticker} - Comparativo",
        height=450,
        showlegend=False
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # ======================================
    # HISTÓRICO
    # ======================================

    st.subheader("Histórico de Preços")

    historico = obter_historico(ticker)

    fig2 = go.Figure()

    fig2.add_trace(
        go.Scatter(
            x=historico.index,
            y=historico["Close"],
            mode="lines",
            name="Cotação"
        )
    )

    fig2.update_layout(
        height=500,
        xaxis_title="Data",
        yaxis_title="Preço (R$)"
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )

    # ======================================
    # RESUMO
    # ======================================

    resumo = pd.DataFrame({
        "Indicador": [
            "Cotação",
            "PT Médio",
            "PT Projetivo",
            "DY Médio",
            "DY Projetivo",
            "Margem Segurança"
        ],
        "Valor": [
            f"R$ {cotacao:.2f}",
            f"R$ {pt_medio:.2f}",
            f"R$ {pt_projetivo:.2f}",
            f"{dy_medio:.2f}%",
            f"{dy_projetivo:.2f}%",
            f"{margem:.2f}%"
        ]
    })

    st.dataframe(
        resumo,
        hide_index=True,
        use_container_width=True
    )