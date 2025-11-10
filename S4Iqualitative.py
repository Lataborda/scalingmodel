import streamlit as st
import pandas as pd
import plotly.express as px
import unicodedata

# --- CONFIGURACIÓN BÁSICA ---
st.set_page_config(
    page_title="Matriz de Análisis de Sensibilidad",
    layout="wide"
)

st.title("Matriz de Análisis de Sensibilidad por Tipo de Actor")
st.markdown("""
Esta herramienta permite filtrar y visualizar el análisis de sensibilidad de la categoria de análisis: "Alineación entre la oferta tecnológica (variedades mejoradas) y la demanda del mercado y del consumidor"
""")

# --- CARGA DEL ARCHIVO ---
@st.cache_data
def load_data():
    df = pd.read_excel("analisis_sensibilidad_variedades_combinado_final_conteo.xlsx")

    # Normalizar nombres de columnas: quitar tildes, minúsculas, sin espacios
    def _normalize(s):
        s = str(s).strip()
        s = unicodedata.normalize("NFKD", s).encode("ASCII", "ignore").decode("ASCII")
        s = s.lower().replace(" ", "_")
        return s

    canonical = {
        "nombre": "nombre",
        "tipo_de_actor": "tipo_de_actor",
        "institucion": "institucion",
        "ubicacion": "ubicacion",
        "alineacion": "alineacion",
        "desalineacion": "desalineacion",
        "num_citas_alineacion": "num_citas_alineacion",
        "num_citas_desalineacion": "num_citas_desalineacion",
        "num_citas_por_persona": "num_citas_por_persona",
        "key": "key",
    }

    cols_map = {}
    for c in df.columns:
        n = _normalize(c)
        if n in canonical:
            cols_map[c] = canonical[n]
        else:
            n2 = n.replace("-", "_")
            if n2 in canonical:
                cols_map[c] = canonical[n2]

    if cols_map:
        df = df.rename(columns=cols_map)

    # Convertir columnas numéricas
    for cnum in ["num_citas_alineacion", "num_citas_desalineacion", "num_citas_por_persona"]:
        if cnum in df.columns:
            df[cnum] = pd.to_numeric(df[cnum], errors="coerce").fillna(0).astype(int)

    return df


df = load_data()

# --- PANEL DE FILTROS ---
st.sidebar.header("🔍 Filtros")

tipo_actor = st.sidebar.multiselect(
    "Tipo de actor",
    options=(df["tipo_de_actor"].dropna().unique() if "tipo_de_actor" in df.columns else []),
)

institucion = st.sidebar.multiselect(
    "Institución",
    options=(df["institucion"].dropna().unique() if "institucion" in df.columns else []),
)

ubicacion = st.sidebar.multiselect(
    "Ubicación",
    options=(df["ubicacion"].dropna().unique() if "ubicacion" in df.columns else []),
)

nombre = st.sidebar.multiselect(
    "Nombre",
    options=(df["nombre"].dropna().unique() if "nombre" in df.columns else []),
)

# --- APLICAR FILTROS ---
df_filtered = df.copy()
if tipo_actor:
    df_filtered = df_filtered[df_filtered["tipo_de_actor"].isin(tipo_actor)]
if institucion:
    df_filtered = df_filtered[df_filtered["institucion"].isin(institucion)]
if ubicacion:
    df_filtered = df_filtered[df_filtered["ubicacion"].isin(ubicacion)]
if nombre:
    df_filtered = df_filtered[df_filtered["nombre"].isin(nombre)]

# --- INTERFAZ PRINCIPAL ---
tab_data, tab_chart, tab_cards = st.tabs(["📄 Datos", "📊 Gráfico", "🧩 Vista por actor"])

# ---------------------------------------------------------------------
# 📄 TABLA DE DATOS
# ---------------------------------------------------------------------
with tab_data:
    st.subheader("📄 Datos filtrados")

    column_config = {}
    if "alineacion" in df_filtered.columns:
        column_config["alineacion"] = st.column_config.TextColumn("Alineación", width="large", max_chars=2000)
    if "desalineacion" in df_filtered.columns:
        column_config["desalineacion"] = st.column_config.TextColumn("Desalineación", width="large", max_chars=2000)

    st.data_editor(
        df_filtered,
        width="stretch",
        hide_index=True,
        column_config=column_config
    )

# ---------------------------------------------------------------------
# 📊 GRÁFICO
# ---------------------------------------------------------------------
with tab_chart:
    st.subheader("📊 Comparación por Tipo de actor")

    col_a = "num_citas_alineacion" if "num_citas_alineacion" in df_filtered.columns else "alineacion"
    col_b = "num_citas_desalineacion" if "num_citas_desalineacion" in df_filtered.columns else "desalineacion"

    if {"tipo_de_actor", col_a, col_b}.issubset(df_filtered.columns):

        # Crear dataset agrupado
        chart_df = (
            df_filtered.groupby("tipo_de_actor")[[col_a, col_b]]
            .sum()
            .reset_index()
        )

        # --- OPCIÓN 1: ALTair (corregido) ---
        try:
            import altair as alt

            chart_altair = (
                alt.Chart(chart_df)
                .transform_fold(
                    [col_a, col_b],
                    as_=["Categoría", "Número de citas"]
                )
                .mark_bar()
                .encode(
                    x=alt.X("tipo_de_actor:N", title="Tipo de actor"),
                    y=alt.Y("Número de citas:Q", title="Número de citas"),
                    color=alt.Color(
                        "Categoría:N",
                        title="Categoría",
                        scale=alt.Scale(
                            domain=[col_a, col_b],
                            range=["#2ca02c", "#d62728"]
                        )
                    ),
                    tooltip=[
                        alt.Tooltip("tipo_de_actor:N", title="Tipo de actor"),
                        alt.Tooltip("Categoría:N", title="Categoría"),
                        alt.Tooltip("Número de citas:Q", title="Número de citas")
                    ]
                )
                .properties(width="container", height=400)
            )

            st.altair_chart(chart_altair, use_container_width=True)
            st.caption("Gráfico generado con Altair")

        except Exception as e:
            st.error(f"Error al generar gráfico con Altair: {e}")

        # --- OPCIÓN 2: Plotly Express ---
        st.divider()
        st.markdown("### 📊 Versión alternativa")
        chart_df_plotly = chart_df.melt(id_vars="tipo_de_actor",
                                        value_vars=[col_a, col_b],
                                        var_name="Categoría",
                                        value_name="Número de citas")

        fig = px.bar(
            chart_df_plotly,
            x="tipo_de_actor",
            y="Número de citas",
            color="Categoría",
            barmode="group",
            color_discrete_map={col_a: "#a0c8a0", col_b: "#bb4040"},
            title="Comparación por tipo de actor (Alineación vs Desalineación)"
        )
        st.plotly_chart(fig, use_container_width=True)

    else:
        st.warning(f"Faltan columnas para el gráfico. Columnas actuales: {', '.join(df_filtered.columns)}")

# ---------------------------------------------------------------------
# 🧩 VISTA POR ACTOR
# ---------------------------------------------------------------------
with tab_cards:
    st.subheader("🧩 Vista narrativa por actor")

    if "nombre" in df_filtered.columns:
        grouped = df_filtered.groupby(["nombre", "institucion"], dropna=False).agg({
            "num_citas_alineacion": "sum" if "num_citas_alineacion" in df_filtered.columns else "count",
            "num_citas_desalineacion": "sum" if "num_citas_desalineacion" in df_filtered.columns else "count",
        }).reset_index()

        for _, row in grouped.iterrows():
            n = row.get("nombre", "N/A")
            inst = row.get("institucion", "N/A")
            a = int(row.get("num_citas_alineacion", 0))
            d = int(row.get("num_citas_desalineacion", 0))
            st.markdown(f"#### {n} — {inst}")
            st.markdown(f"- Alineación: **{a}** citas\n- Desalineación: **{d}** citas")
            st.markdown("---")
    else:
        st.info("No hay columna 'nombre' para generar la vista por actor.")

# --- RESUMEN FINAL ---
#st.markdown("#### 🧮 Resumen general")
#st.write(df_filtered.describe(include="all"))
