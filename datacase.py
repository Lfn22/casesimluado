import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import random

# --- Configuração da Página ---
st.set_page_config(
    page_title="Negreiros NET - Dashboard Avançado",
    page_icon="📡",
    layout="wide"
)

# --- CSS customizado ---
st.markdown("""
<style>
h1, h2, h3 { color: #004080; }
div[role="listbox"] div[aria-selected="true"] {
    background-color: #27ae60 !important;  
    color: white !important;
}
div[role="listbox"] div[aria-selected="false"] {
    background-color: #a3e4a3 !important;  
    color: #004d00 !important;
}
</style>
""", unsafe_allow_html=True)

# --- Banner Profissional ---
st.markdown("""
<div style="
    background: linear-gradient(90deg, #27ae60, #1abc9c);
    padding: 40px;
    border-radius: 15px;
    text-align: center;
    color: white;
    box-shadow: 0px 4px 20px rgba(0,0,0,0.3);
">
    <h1 style="font-size: 48px; margin: 0;">Negreiros NET</h1>
    <p style="font-size: 20px; margin: 5px 0 20px 0;">Dashboard de Clientes e Consumo de Internet - Petrolina</p>
    <div style="display:flex; justify-content:center; gap:50px;">
        <div><h2 id="total_clientes">150</h2><p>Clientes</p></div>
        <div><h2 id="criticos">35</h2><p>Críticos</p></div>
        <div><h2 id="consumo_medio">200 MB/s</h2><p>Consumo Médio</p></div>
    </div>
</div>
""", unsafe_allow_html=True)

# --- Dados fictícios ---
random.seed(42)
np.random.seed(42)

clientes = [f"{i:03d}" for i in range(1, 151)]
planos = [50, 200, 500]
tipos_plano = ["Residencial", "Empresarial", "Premium"]
bairros = sorted(["Centro", "Areia Branca", "Cohab Massangano", "Jardim Maravilha",
           "Gercino Coelho", "Dom Avelar", "José e Maria", "Pedra Linda",
           "Vila Mocó", "Vale do Grande Rio"])  # ordenados alfabeticamente

coord_bairros = {
    "Centro": (-9.3890, -40.5020),
    "Areia Branca": (-9.4080, -40.5260),
    "Cohab Massangano": (-9.4110, -40.5000),
    "Jardim Maravilha": (-9.4200, -40.5100),
    "Gercino Coelho": (-9.4300, -40.4950),
    "Dom Avelar": (-9.4400, -40.5000),
    "José e Maria": (-9.4500, -40.5050),
    "Pedra Linda": (-9.4600, -40.5100),
    "Vila Mocó": (-9.4700, -40.5200),
    "Vale do Grande Rio": (-9.4800, -40.5300)
}

df = pd.DataFrame({
    "ClienteID": clientes,
    "Bairro": np.random.choice(bairros, size=150),
    "Plano (MB/s)": np.random.choice(planos, size=150),
    "Tipo de Plano": np.random.choice(tipos_plano, size=150),
    "Consumo Atual (MB/s)": np.random.randint(10, 600, size=150)
})

df["Excedeu"] = df["Consumo Atual (MB/s)"] > df["Plano (MB/s)"]
df["Excedeu50"] = df["Consumo Atual (MB/s)"] > df["Plano (MB/s)"]*1.5
df["Lat"] = df["Bairro"].apply(lambda x: coord_bairros[x][0])
df["Lon"] = df["Bairro"].apply(lambda x: coord_bairros[x][1])

# --- Filtros horizontais ---
st.subheader("Filtros de Análise")
col_f1, col_f2, col_f3, col_f4 = st.columns(4)

with col_f1:
    bairros_sel = st.multiselect("Bairro", bairros, default=bairros)

with col_f2:
    planos_sel = st.multiselect("Tipo de Plano", sorted(df["Tipo de Plano"].unique()), default=df["Tipo de Plano"].unique())

with col_f3:
    criticos_sel = st.radio("Mostrar críticos?", ["Todos", "Apenas Críticos", "Sem Críticos"])

with col_f4:
    consumo_min = st.slider("Consumo mínimo (MB/s)", 0, 600, 0)

# --- Filtragem ---
df_filtrado = df[
    (df["Bairro"].isin(bairros_sel)) &
    (df["Tipo de Plano"].isin(planos_sel)) &
    (df["Consumo Atual (MB/s)"] >= consumo_min)
]

if criticos_sel == "Apenas Críticos":
    df_filtrado = df_filtrado[df_filtrado["Excedeu"]]
elif criticos_sel == "Sem Críticos":
    df_filtrado = df_filtrado[~df_filtrado["Excedeu"]]

# --- KPIs ---
st.subheader("KPIs Estratégicos")
if not df_filtrado.empty:
    total_clientes = df_filtrado.shape[0]
    total_criticos = df_filtrado["Excedeu"].sum()
    total_criticos50 = df_filtrado["Excedeu50"].sum()
    consumo_medio = df_filtrado["Consumo Atual (MB/s)"].mean()
    bairro_top = df_filtrado["Bairro"].mode()[0]
    perc_criticos = (total_criticos/total_clientes)*100
else:
    total_clientes, total_criticos, total_criticos50, consumo_medio, bairro_top, perc_criticos = 0,0,0,0,"-",0

col1, col2, col3, col4, col5, col6 = st.columns(6)
col1.metric("Total Clientes", total_clientes)
col2.metric("Clientes Críticos", total_criticos)
col3.metric("Críticos +50%", total_criticos50)
col4.metric("Consumo Médio (MB/s)", f"{consumo_medio:.1f}")
col5.metric("Bairro mais populoso", bairro_top)
col6.metric("% Críticos", f"{perc_criticos:.1f}%")

st.markdown("---")

# --- Criar dados simulados de tendência mensal ---
meses = [f"Mês {i}" for i in range(1,13)]
tendencia = []
for bairro in bairros:
    consumo_base = np.random.randint(50, 300)
    for mes in meses:
        consumo_mes = consumo_base + np.random.randint(-30,30)
        tendencia.append({"Bairro": bairro, "Mês": mes, "Consumo Médio (MB/s)": max(consumo_mes,0)})

df_tendencia = pd.DataFrame(tendencia)

# --- Abas para gráficos e mapa ---
tab1, tab2, tab3, tab4 = st.tabs(["Gráficos", "Tendência", "Mapa", "Tabela"])

# --- Aba Gráficos ---
with tab1:
    st.subheader("Distribuição por Tipo de Plano")
    fig_pizza = px.pie(
        df_filtrado,
        names="Tipo de Plano",
        hole=0.4,
        color="Tipo de Plano",
        color_discrete_map={"Residencial": "#004080", "Empresarial": "#0073e6", "Premium": "#00b300"}
    )
    st.plotly_chart(fig_pizza, use_container_width=True)

    st.subheader("Clientes por Bairro")
    clientes_bairro = df_filtrado["Bairro"].value_counts().reindex(bairros).reset_index()
    clientes_bairro.columns = ["Bairro", "Clientes"]
    fig_bar = px.bar(
        clientes_bairro,
        x="Bairro",
        y="Clientes",
        color="Clientes",
        color_continuous_scale=px.colors.sequential.Greens
    )
    st.plotly_chart(fig_bar, use_container_width=True)

    st.subheader("Top 20 Clientes por Consumo")
    top20 = df_filtrado.sort_values("Consumo Atual (MB/s)", ascending=False).head(20)
    fig_top = px.bar(
        top20,
        x="ClienteID",
        y="Consumo Atual (MB/s)",
        color="Excedeu",
        color_discrete_map={True: "#2ecc71", False: "#1f77b4"}
    )
    st.plotly_chart(fig_top, use_container_width=True)

# --- Aba Tendência ---
with tab2:
    st.subheader("Tendência de Consumo Mensal por Bairro")
    fig_tend = px.line(
        df_tendencia,
        x="Mês",
        y="Consumo Médio (MB/s)",
        color="Bairro",
        line_shape="spline",
        markers=True
    )
    st.plotly_chart(fig_tend, use_container_width=True)

# --- Aba Mapa ---
with tab3:
    st.subheader("Mapa de Clientes - Petrolina")
    mapa_bairro = df_filtrado.groupby("Bairro").agg({
        "Lat":"first",
        "Lon":"first",
        "ClienteID":"count",
        "Consumo Atual (MB/s)":"mean",
        "Excedeu":"sum"
    }).reset_index()
    mapa_bairro["Tamanho"] = mapa_bairro["ClienteID"] + mapa_bairro["Consumo Atual (MB/s)"]/10

    fig_map = px.scatter_mapbox(
        mapa_bairro,
        lat="Lat",
        lon="Lon",
        size="Tamanho",
        size_max=70,
        hover_name="Bairro",
        hover_data={"ClienteID":True,"Consumo Atual (MB/s)":":.1f","Excedeu":True,"Lat":False,"Lon":False,"Tamanho":False},
        color="Excedeu",
        color_discrete_map={True:"#2ecc71", False:"#004080"},
        zoom=12,
        height=600
    )
    fig_map.update_layout(mapbox_style="open-street-map")
    st.plotly_chart(fig_map, use_container_width=True)

# --- Aba Tabela ---
with tab4:
    st.subheader("Tabela de Dados Filtrados")
    st.dataframe(df_filtrado)
    csv = df_filtrado.to_csv(index=False).encode('utf-8')
    st.download_button("Exportar CSV", data=csv, file_name="clientes_filtrados.csv", mime="text/csv")
