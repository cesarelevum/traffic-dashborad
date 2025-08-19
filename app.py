import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="KPIs de Tráfico • Transportista", layout="wide")
st.title("🚚 Dashboard de KPIs – Tráfico (Demo Realista)")

# -----------------------------
# 1) Carga de datos
# -----------------------------
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("data.csv")
    except Exception:
        # Fallback si no existe data.csv (datos realistas de ejemplo)
        df = pd.DataFrame({
            "Unidad": [f"T-{i}" for i in range(101, 113)],
            "Km_recorridos": [4200, 3980, 3650, 4400, 3820, 4100, 3950, 3720, 4300, 4050, 3880, 4010],
            "Combustible_L": [1460, 1350, 1300, 1520, 1340, 1410, 1370, 1290, 1480, 1430, 1360, 1390],
            "Viajes":        [32,   29,   27,   34,   28,   31,   30,   26,   33,   31,   29,   30],
            "Entregas_a_tiempo": [30, 27, 25, 33, 26, 29, 28, 24, 31, 29, 27, 28],
            "Entregas_totales":  [32, 30, 27, 34, 28, 31, 30, 26, 33, 31, 29, 30],
            "Tiempo_promedio_h": [7.1, 7.8, 8.2, 6.9, 7.5, 7.3, 7.6, 8.0, 7.0, 7.4, 7.7, 7.5],
            "Disponibilidad_pct": [92, 90, 88, 95, 91, 93, 92, 89, 94, 92, 90, 91],
            "Incidentes": [0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0]
        })
    return df

df = load_data()

# columnas calculadas por unidad
df["Km_por_L"] = (df["Km_recorridos"] / df["Combustible_L"]).round(2)
df["OnTime_pct"] = (df["Entregas_a_tiempo"] / df["Entregas_totales"] * 100).round(1)

# -----------------------------
# 2) Parámetros (sidebar)
# -----------------------------
st.sidebar.header("Parámetros de Costos (demo)")
precio_litro = st.sidebar.number_input("Precio diésel (MXN/L)",  min_value=10.0, max_value=40.0, value=24.0, step=0.5)
mant_km      = st.sidebar.number_input("Mantenimiento (MXN/km)",  min_value=0.0,  max_value=10.0, value=2.0,  step=0.1)
otros_km     = st.sidebar.number_input("Otros costos (MXN/km)",    min_value=0.0,  max_value=10.0, value=1.5,  step=0.1)

# filtro por unidad (opcional)
unidades_sel = st.sidebar.multiselect("Filtrar unidades", options=df["Unidad"].tolist(), default=df["Unidad"].tolist())
df_f = df[df["Unidad"].isin(unidades_sel)].copy()

# -----------------------------
# 3) KPIs globales
# -----------------------------
km_totales = int(df_f["Km_recorridos"].sum())
litros_tot = int(df_f["Combustible_L"].sum())
entregas_tiempo = int(df_f["Entregas_a_tiempo"].sum())
entregas_total  = int(df_f["Entregas_totales"].sum())
on_time_global  = (entregas_tiempo / entregas_total * 100) if entregas_total else 0
util_flota      = ( (df_f["Viajes"]>0).sum() / df_f["Unidad"].nunique() * 100 )
incid_x_100k    = (df_f["Incidentes"].sum() / km_totales * 100000) if km_totales else 0
rend_prom_kml   = df_f["Km_por_L"].mean()

# costo por km (combustible + mantenimiento + otros)
costo_combustible_total = litros_tot * precio_litro
costo_operativo_total   = costo_combustible_total + km_totales * (mant_km + otros_km)
costo_por_km            = (costo_operativo_total / km_totales) if km_totales else 0

# Mostrar KPIs
k1, k2, k3, k4, k5, k6 = st.columns(6)
k1.metric("Utilización de flota", f"{util_flota:0.1f}%")
k2.metric("Entregas a tiempo", f"{on_time_global:0.1f}%")
k3.metric("Costo por km", f"${costo_por_km:0.2f} MXN")
k4.metric("Km recorridos", f"{km_totales:,}".replace(",", " "))
k5.metric("Rendimiento promedio", f"{rend_prom_kml:0.2f} km/L")
k6.metric("Incidentes /100k km", f"{incid_x_100k:0.2f}")

st.divider()

# -----------------------------
# 4) Gráficas
# -----------------------------
c1, c2, c3 = st.columns(3)

with c1:
    st.subheader("Km por unidad")
    fig, ax = plt.subplots()
    df_f.plot(kind="bar", x="Unidad", y="Km_recorridos", ax=ax)
    ax.set_xlabel("Unidad"); ax.set_ylabel("Km")
    st.pyplot(fig, clear_figure=True)

with c2:
    st.subheader("Entregas a tiempo (%) por unidad")
    fig2, ax2 = plt.subplots()
    df_f.plot(kind="bar", x="Unidad", y="OnTime_pct", color="tab:green", ax=ax2)
    ax2.set_ylim(0,100); ax2.set_xlabel("Unidad"); ax2.set_ylabel("%")
    st.pyplot(fig2, clear_figure=True)

with c3:
    st.subheader("Rendimiento (km/L) por unidad")
    fig3, ax3 = plt.subplots()
    df_f.plot(kind="line", x="Unidad", y="Km_por_L", marker="o", ax=ax3)
    ax3.set_xlabel("Unidad"); ax3.set_ylabel("km/L")
    st.pyplot(fig3, clear_figure=True)

st.divider()

# -----------------------------
# 5) Tabla de detalle
# -----------------------------
st.subheader("Detalle operativo")
cols = ["Unidad","Viajes","Km_recorridos","Combustible_L","Km_por_L","Entregas_a_tiempo",
        "Entregas_totales","OnTime_pct","Tiempo_promedio_h","Disponibilidad_pct","Incidentes"]
st.dataframe(df_f[cols].sort_values("Unidad"), use_container_width=True)

st.caption("""
**Notas (demo):**  
- *Costo por km* = (Diésel + Mantenimiento + Otros) / Km totales.  
- Puedes subir tu propio **data.csv** (mismas columnas) para ver tus números reales.  
- Ajusta precios y costos en la barra lateral para simular diferentes escenarios.
""")
