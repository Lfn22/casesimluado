"""Dashboard Streamlit para monitorar consumo de internet em Petrolina."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Iterable, Tuple

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="Negreiros NET - Dashboard Avançado",
    page_icon="📡",
    layout="wide",
)

DATA_PATH = Path(__file__).with_name("clientes_petrolina.csv")
BAIRRO_COORDS: Dict[str, Tuple[float, float]] = {
    "Centro": (-9.3890, -40.5020),
    "Areia Branca": (-9.4080, -40.5260),
    "Cohab Massangano": (-9.4110, -40.5000),
    "Jardim Maravilha": (-9.4200, -40.5100),
    "Gercino Coelho": (-9.4300, -40.4950),
    "Dom Avelar": (-9.4400, -40.5000),
    "José e Maria": (-9.4500, -40.5050),
    "Pedra Linda": (-9.4600, -40.5100),
    "Vila Mocó": (-9.4700, -40.5200),
    "Vale do Grande Rio": (-9.4800, -40.5300),
}

PRIMARY_COLOR = "#0E6251"
SECONDARY_COLOR = "#1ABC9C"
ACCENT_COLOR = "#0B5345"


def inject_styles() -> None:
   
    st.markdown(
        f"""
        <style>
            :root {{
                --primary: {PRIMARY_COLOR};
                --secondary: {SECONDARY_COLOR};
                --accent: {ACCENT_COLOR};
            }}
            h1, h2, h3 {{ color: var(--primary); }}
            .stMetric-value {{ color: var(--primary); }}
            div[role="listbox"] div[aria-selected="true"] {{
                background-color: var(--primary) !important;
                color: #ffffff !important;
            }}
            div[role="listbox"] div[aria-selected="false"] {{
                background-color: rgba(26, 188, 156, 0.15) !important;
                color: var(--accent) !important;
            }}
            section[data-testid="stSidebar"] {{
                background: linear-gradient(180deg, rgba(14,98,81,0.9), rgba(26,188,156,0.9));
                color: white;
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_hero(
    total: int,
    critical: int,
    consumo_medio: float,
    container: st.delta_generator.DeltaGenerator | None = None,
) -> None:
    """Render hero banner with dynamic KPIs."""
    consumo_str = f"{consumo_medio:.1f} MB/s" if total else "-"
    target = container if container is not None else st
    target.markdown(
        f"""
        <div style="
            background: linear-gradient(90deg, var(--primary), var(--secondary));
            padding: 40px;
            border-radius: 18px;
            text-align: center;
            color: white;
            box-shadow: 0px 6px 18px rgba(0,0,0,0.25);
            margin-bottom: 1.5rem;
        ">
            <h1 style="font-size: 44px; margin: 0;">Negreiros NET</h1>
            <p style="font-size: 20px; margin: 6px 0 26px 0;">
                Monitoramento de clientes e desempenho de internet em Petrolina
            </p>
            <div style="display:flex; justify-content:center; gap:60px; flex-wrap:wrap;">
                <div><h2 style="margin:0; font-size:38px;">{total}</h2><p style="margin:4px 0 0 0;">Clientes monitorados</p></div>
                <div><h2 style="margin:0; font-size:38px;">{critical}</h2><p style="margin:4px 0 0 0;">Clientes críticos</p></div>
                <div><h2 style="margin:0; font-size:38px;">{consumo_str}</h2><p style="margin:4px 0 0 0;">Consumo médio</p></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _clean_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [col.replace("\n", " ").strip() for col in df.columns]
    return df


def _coerce_numeric(df: pd.DataFrame, columns: Iterable[str]) -> pd.DataFrame:
    df = df.copy()
    for column in columns:
        if column in df.columns:
            df[column] = pd.to_numeric(df[column], errors="coerce")
    return df


def _prepare_coordinates(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["Lat"] = df["Bairro"].map(lambda bairro: BAIRRO_COORDS.get(bairro, (np.nan, np.nan))[0])
    df["Lon"] = df["Bairro"].map(lambda bairro: BAIRRO_COORDS.get(bairro, (np.nan, np.nan))[1])
    return df


def generate_synthetic_data(num_clients: int = 150) -> pd.DataFrame:
    rng = np.random.default_rng(42)
    clientes = [f"{i:03d}" for i in range(1, num_clients + 1)]
    planos = np.array([50, 100, 150, 200, 500])
    tipos_plano = np.array(["Residencial", "Empresarial", "Premium"])
    bairros = sorted(BAIRRO_COORDS.keys())

    df = pd.DataFrame(
        {
            "ClienteID": clientes,
            "Bairro": rng.choice(bairros, size=num_clients),
            "Plano (MB/s)": rng.choice(planos, size=num_clients),
            "Tipo de Plano": rng.choice(tipos_plano, size=num_clients),
            "Consumo Atual (MB/s)": rng.integers(10, 550, size=num_clients),
        }
    )
    return df


@st.cache_data(show_spinner=False)
def load_client_data(csv_path: Path) -> Tuple[pd.DataFrame, str]:
    try:
        df = pd.read_csv(csv_path)
        df = _clean_columns(df)
        df["Bairro"] = df.get("Bairro", "").astype(str).str.strip()
        df["ClienteID"] = df.get("ClienteID", "").astype(str).str.zfill(3)
        df = _coerce_numeric(df, ["Plano (MB/s)", "Consumo Atual (MB/s)"])
        required_columns = {"ClienteID", "Plano (MB/s)", "Consumo Atual (MB/s)", "Tipo de Plano", "Bairro"}
        if not required_columns.issubset(df.columns):
            raise ValueError("CSV não possui todas as colunas necessárias")
        source = "Arquivo CSV"
    except Exception:
        df = generate_synthetic_data()
        source = "Dados simulados"

    df = df.dropna(subset=["Plano (MB/s)", "Consumo Atual (MB/s)", "Tipo de Plano", "Bairro"]).copy()
    df["Bairro"] = df["Bairro"].astype(str).str.strip()
    df["ClienteID"] = df["ClienteID"].astype(str).str.zfill(3)
    df["Excedeu"] = df["Consumo Atual (MB/s)"] > df["Plano (MB/s)"]
    df["Excedeu50"] = df["Consumo Atual (MB/s)"] > df["Plano (MB/s)"] * 1.5
    df = _prepare_coordinates(df)
    return df, source


def render_filters(df: pd.DataFrame) -> Tuple[list[str], list[str], str, int]:
    st.subheader("Filtros de Análise")
    bairros = sorted(df["Bairro"].dropna().unique())
    tipos = sorted(df["Tipo de Plano"].dropna().unique())
    consumo_max = int(np.ceil(df["Consumo Atual (MB/s)"].max() / 10.0) * 10)

    col_f1, col_f2 = st.columns(2)
    with col_f1:
        bairros_sel = st.multiselect("Bairros", bairros, default=bairros)
    with col_f2:
        tipos_sel = st.multiselect("Tipos de Plano", tipos, default=tipos)

    col_f3, col_f4 = st.columns(2)
    with col_f3:
        criticos_sel = st.radio("Clientes críticos", ["Todos", "Apenas críticos", "Sem críticos"], index=0)
    with col_f4:
        consumo_min = st.slider("Consumo mínimo (MB/s)", 0, consumo_max, 0, step=10)

    return bairros_sel, tipos_sel, criticos_sel, consumo_min


def apply_filters(
    df: pd.DataFrame,
    bairros_sel: Iterable[str],
    tipos_sel: Iterable[str],
    criticos_sel: str,
    consumo_min: int,
) -> pd.DataFrame:
    mask = (
        df["Bairro"].isin(bairros_sel)
        & df["Tipo de Plano"].isin(tipos_sel)
        & (df["Consumo Atual (MB/s)"] >= consumo_min)
    )
    df_filtrado = df.loc[mask].copy()

    if criticos_sel == "Apenas críticos":
        df_filtrado = df_filtrado[df_filtrado["Excedeu"]]
    elif criticos_sel == "Sem críticos":
        df_filtrado = df_filtrado[~df_filtrado["Excedeu"]]

    return df_filtrado


def compute_kpis(df: pd.DataFrame) -> Dict[str, float]:
    if df.empty:
        return {
            "total_clientes": 0,
            "total_criticos": 0,
            "total_criticos50": 0,
            "consumo_medio": 0.0,
            "bairro_top": "-",
            "perc_criticos": 0.0,
        }

    total_clientes = int(df.shape[0])
    total_criticos = int(df["Excedeu"].sum())
    total_criticos50 = int(df["Excedeu50"].sum())
    consumo_medio = float(df["Consumo Atual (MB/s)"].mean())
    bairro_top = df["Bairro"].mode().iloc[0]
    perc_criticos = float(total_criticos / total_clientes * 100)

    return {
        "total_clientes": total_clientes,
        "total_criticos": total_criticos,
        "total_criticos50": total_criticos50,
        "consumo_medio": consumo_medio,
        "bairro_top": bairro_top,
        "perc_criticos": perc_criticos,
    }


def render_kpis(kpis: Dict[str, float]) -> None:
    st.subheader("KPIs Estratégicos")
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    col1.metric("Total de clientes", kpis["total_clientes"])
    col2.metric("Clientes críticos", kpis["total_criticos"])
    col3.metric("Críticos +50%", kpis["total_criticos50"])
    col4.metric("Consumo médio (MB/s)", f"{kpis['consumo_medio']:.1f}" if kpis["total_clientes"] else "-")
    col5.metric("Bairro com mais clientes", kpis["bairro_top"])
    col6.metric("% de críticos", f"{kpis['perc_criticos']:.1f}%" if kpis["total_clientes"] else "0.0%")
    st.markdown("---")


def render_charts(df_filtrado: pd.DataFrame, bairros: Iterable[str]) -> None:
    if df_filtrado.empty:
        st.info("Ajuste os filtros para visualizar os gráficos.")
        return

    st.subheader("Distribuição por Tipo de Plano")
    fig_pizza = px.pie(
        df_filtrado,
        names="Tipo de Plano",
        hole=0.4,
        color="Tipo de Plano",
        color_discrete_sequence=px.colors.sequential.Teal,
    )
    st.plotly_chart(fig_pizza, use_container_width=True)

    st.subheader("Clientes por Bairro")
    clientes_bairro = (
        df_filtrado["Bairro"].value_counts().reindex(sorted(bairros), fill_value=0).reset_index()
    )
    clientes_bairro.columns = ["Bairro", "Clientes"]
    fig_bar = px.bar(
        clientes_bairro,
        x="Bairro",
        y="Clientes",
        color="Clientes",
        color_continuous_scale=px.colors.sequential.Teal,
    )
    fig_bar.update_layout(coloraxis_showscale=False)
    st.plotly_chart(fig_bar, use_container_width=True)

    st.subheader("Top 20 Clientes por Consumo")
    top20 = df_filtrado.sort_values("Consumo Atual (MB/s)", ascending=False).head(20)
    fig_top = px.bar(
        top20,
        x="ClienteID",
        y="Consumo Atual (MB/s)",
        color="Excedeu",
        color_discrete_map={True: SECONDARY_COLOR, False: PRIMARY_COLOR},
    )
    st.plotly_chart(fig_top, use_container_width=True)


@st.cache_data(show_spinner=False)
def build_trend_data(seed_data: Tuple[Tuple[str, float], ...]) -> pd.DataFrame:
    if not seed_data:
        return pd.DataFrame(columns=["Bairro", "Mês", "Consumo Médio (MB/s)"])

    rng = np.random.default_rng(2024)
    meses = [
        "Jan", "Fev", "Mar", "Abr", "Mai", "Jun",
        "Jul", "Ago", "Set", "Out", "Nov", "Dez",
    ]
    registros = []
    for bairro, base in seed_data:
        base = base if not np.isnan(base) else rng.uniform(60, 200)
        for idx, mes in enumerate(meses):
            tendencia = max(base + rng.normal(0, 12) + idx * 1.2, 0)
            registros.append({
                "Bairro": bairro,
                "Mês": mes,
                "Consumo Médio (MB/s)": tendencia,
            })
    return pd.DataFrame(registros)


def render_trend(df_base: pd.DataFrame) -> None:
    means = df_base.groupby("Bairro")["Consumo Atual (MB/s)"].mean()
    seed_data = tuple(sorted((bairro, float(valor)) for bairro, valor in means.items()))
    df_tendencia = build_trend_data(seed_data)

    if df_tendencia.empty:
        st.info("Sem dados suficientes para gerar a tendência mensal.")
        return

    st.subheader("Tendência de Consumo Mensal por Bairro")
    fig_tend = px.line(
        df_tendencia,
        x="Mês",
        y="Consumo Médio (MB/s)",
        color="Bairro",
        line_shape="spline",
        markers=True,
        color_discrete_sequence=px.colors.qualitative.Dark24,
    )
    st.plotly_chart(fig_tend, use_container_width=True)


def render_map(df_filtrado: pd.DataFrame) -> None:
    if df_filtrado.empty:
        st.info("Sem dados para exibir no mapa.")
        return

    mapa_bairro = (
        df_filtrado.groupby("Bairro").agg(
            Lat=("Lat", "first"),
            Lon=("Lon", "first"),
            Clientes=("ClienteID", "count"),
            Consumo=("Consumo Atual (MB/s)", "mean"),
            Criticos=("Excedeu", "sum"),
        )
    ).reset_index()
    mapa_bairro = mapa_bairro.dropna(subset=["Lat", "Lon"])

    if mapa_bairro.empty:
        st.warning("Os bairros filtrados não possuem coordenadas cadastradas.")
        return

    mapa_bairro["Tamanho"] = mapa_bairro["Clientes"] + mapa_bairro["Consumo"] / 12

    fig_map = px.scatter_mapbox(
        mapa_bairro,
        lat="Lat",
        lon="Lon",
        size="Tamanho",
        size_max=65,
        hover_name="Bairro",
        hover_data={
            "Clientes": True,
            "Consumo": ":.1f",
            "Criticos": True,
            "Lat": False,
            "Lon": False,
            "Tamanho": False,
        },
        color="Criticos",
        color_continuous_scale=px.colors.sequential.Teal,
        zoom=12,
        height=600,
    )
    fig_map.update_layout(mapbox_style="open-street-map", coloraxis_showscale=False)
    st.plotly_chart(fig_map, use_container_width=True)


def render_table(df_filtrado: pd.DataFrame) -> None:
    st.subheader("Tabela de Dados Filtrados")
    if df_filtrado.empty:
        st.info("Nenhum registro encontrado com os filtros selecionados.")
        return

    st.dataframe(df_filtrado)
    csv = df_filtrado.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Exportar CSV",
        data=csv,
        file_name="clientes_filtrados.csv",
        mime="text/csv",
    )


def main() -> None:
    inject_styles()
    df, data_source = load_client_data(DATA_PATH)

    hero_placeholder = st.empty()
    bairros_sel, tipos_sel, criticos_sel, consumo_min = render_filters(df)
    df_filtrado = apply_filters(df, bairros_sel, tipos_sel, criticos_sel, consumo_min)

    kpis = compute_kpis(df_filtrado)
    render_hero(
        kpis["total_clientes"],
        kpis["total_criticos"],
        kpis["consumo_medio"],
        container=hero_placeholder,
    )
    st.caption(f"Fonte dos dados: {data_source}.")

    render_kpis(kpis)

    tab1, tab2, tab3, tab4 = st.tabs(["Gráficos", "Tendência", "Mapa", "Tabela"])

    with tab1:
        render_charts(df_filtrado, bairros_sel or df["Bairro"].unique())
    with tab2:
        render_trend(df_filtrado if not df_filtrado.empty else df)
    with tab3:
        render_map(df_filtrado)
    with tab4:
        render_table(df_filtrado)


if __name__ == "__main__":
    main()
