import streamlit as st
import pandas as pd

st.set_page_config(page_title="KPIs Tráfico • Transportista", layout="wide")
st.title("🚛 Dashboard KPIs – Tráfico (Demo)")

# ==== Datos de ejemplo (reemplaza con tu API/BD) ====
df = pd.DataFrame({
    "Unidad": [f"T-{i}" for i in range(101, 111)],
    "Km": [1540, 2120, 1780, 1950, 2230, 1880, 2100, 1990, 1850, 2300],
    "Combustible_L": [550, 720, 600, 670, 750, 620, 700, 690, 640, 770],
    "Viajes": [20, 28, 23, 25, 30, 24, 27, 26, 22, 31],
    "OnTime_%": [95, 88, 92, 90, 96, 89, 93, 91, 87, 97],
    "Incidentes": [0, 1, 0, 1, 0, 0, 1, 0, 0, 1]
})
df["Km_L"] = (df["Km"] / df["Combustible_L"]).round(2)

# Supuesto simple para demo:
COSTO_LITRO = 24  # MXN
costo_combustible_total = int(df["Combustible_L"].sum() * COSTO_LITRO)
costo_por_km = (costo_combustible_total / df["Km"].sum())

# ==== KPIs principales ====
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Entregas a tiempo (%)", f"{df['OnTime_%'].mean():.1f}%")
col2.metric("Costo por km (MXN)", f"{costo_por_km:.2f}")
col3.metric("Km recorridos (mes)", f"{df['Km'].sum():,}".replace(",", " "))
col4.metric("Rendimiento promedio (km/L)", f"{df['Km_L'].mean():.2f}")
col5.metric("Incidentes (mes)", int(df["Incidentes"].sum()))

st.divider()

# ==== Gráficas rápidas ====
c1, c2, c3 = st.columns(3)
with c1:
    st.subheader("Km por unidad")
    st.bar_chart(df.set_index("Unidad")["Km"])
with c2:
    st.subheader("Rendimiento km/L")
    st.line_chart(df.set_index("Unidad")["Km_L"])
with c3:
    st.subheader("On-Time por unidad (%)")
    st.bar_chart(df.set_index("Unidad")["OnTime_%"])

st.divider()
st.subheader("Detalle operativo")
st.dataframe(df, use_container_width=True)

st.caption("""
**Notas (demo):**
- *Costo por km* calculado sólo con combustible para simplificar (MXN 24/L).
- Reemplaza el DataFrame por tu fuente real (API/BD) y estos KPIs quedarán listos.
""")
