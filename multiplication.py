
# scaler_stock_tunnels_timeline.py
# Interpolador/extrapolador de STOCK y TÚNELES con costos + cronograma (timeline) y UI bilingüe (ES/EN)
# Autor: ChatGPT — Oct/2025

import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="Stock & Tunnels Scaler — with Costs + Timeline (ES/EN)", layout="wide")

# (Code content identical to previous cell; re-inserting for persistence)

LANGS = {
    "ES": {
        "title": "Escalador de STOCK y TÚNELES — con costos + línea de tiempo",
        "caption": "Calcula **stock con riego (ha)**, **área de túneles (m²)**, compara **costos** (Riego+túneles vs solo túneles) y muestra un **cronograma** mínimo para alcanzar la meta, respetando ventanas de lluvia y madurez (≥6 meses).",
        "sidebar_main": "🎯 Meta y supuestos clave",
        "meta": "Meta de huella (ha)",
        "rho": "Densidad (plantas/ha, ρ)",
        "stock_prod": "Productividad del STOCK",
        "cuts": "Estacas por planta por año (stock)",
        "s_stock": "Viabilidad stock (%)",
        "tunnels_prod": "Túneles (productividad)",
        "r_cut": "Estacas por m² por corte (r_cut)",
        "tau": "Meses por corte (τ)",
        "s_tunnel": "Viabilidad túnel (%)",
        "calendar": "Calendario",
        "irrigation": "¿Riego en STOCK?",
        "commercial_window": "Ventana COMERCIAL (meses, lluvia)",
        "stock_window": "Ventana STOCK (si NO riego)",
        "L_stock_min": "Madurez mínima de stock (meses)",
        "prod_months_distrib": "Meses efectivos de producción/plantación por año (distribuido)",
        "prod_months_window": "Meses de ventana concentrada (pico)",
        "renewal": "Renovación del stock",
        "k_years": "Cadencia de renovación (años)",
        "mode_renewal": "Modo de renovación",
        "mode_uniform": "Uniforme anual (promediado)",
        "mode_batch": "Por lotes en año de recambio",
        "tunnel_size": "Tamaño de túnel (para convertir a #)",
        "costs": "💸 Costos y moneda",
        "currency": "Moneda",
        "fx": "COP por USD (si usas USD)",
        "tunnel_unit_cost": "Costo por túnel (COP/ud)",
        "tc11": "Aplicar +11% (TC) a túnel",
        "irrig_capex": "CAPEX riego por ha de STOCK (COP/ha)",
        "irrig_opex": "OPEX riego anual (COP/ha/año) — opcional",
        "ciat_pkg": "🤝 Paquete de asistencia / partnership (CIAT)",
        "pkg_select": "Selecciona nivel",
        "include_pkg": "Incluir costo del paquete en el total",
        "kpis_main": ["🎯 Meta de huella (ha)", "🌱 Stock requerido (ha, con riego)", "🧪 Plantas en stock"],
        "dim_tunnels": "📦 Dimensión de TÚNELES",
        "distributed": "Distribuido ({m} m/año)",
        "window_uniform": "Ventana (uniforme, {m} m)",
        "window_peak": "Ventana (año pico, {m} m)",
        "cost_compare": "💰 Comparador de costos — Multiplicación hasta sostener la meta",
        "A_title": "A) **Riego + túneles (distribuido)**",
        "B_title": "B) **Solo túneles (ventana)**",
        "area_tunnels": "Área túneles",
        "capex_tunnels": "CAPEX túneles",
        "capex_irrig": "CAPEX riego (stock {ha:.1f} ha)",
        "opex_irrig": "OPEX riego anual (referencia)",
        "total_capex": "**CAPEX total**",
        "cost_per_ha": "Costo por ha de meta ≈ {x}",
        "diff_A_better": "Con estos supuestos, **A) Riego + túneles** requiere **{x} menos** de CAPEX que **B) Solo túneles**.",
        "diff_B_better": "Con estos supuestos, **B) Solo túneles** requiere **{x} menos** de CAPEX que **A) Riego + túneles**.",
        "graph_scale_title": "Escalamiento: meta (ha) → stock requerido (ha)",
        "graph_scale_x": "Meta de huella (ha)",
        "graph_scale_y": "Stock requerido (ha)",
        "timeline": "🗓️ Línea de tiempo mínima (12–24 meses)",
        "timeline_note": "Las cohortes de stock deben tener **≥ {L} meses** antes de abastecer cada mes de la ventana comercial. Con riego, plantamos exactamente {L} meses antes; sin riego, desplazamos la siembra al **mes lluvioso previo** en la ventana de stock.",
        "timeline_stock": "Cohortes de stock (plantación)",
        "timeline_maturity": "Stock llega a madurez (≥{L} m)",
        "timeline_deploy": "Siembra comercial (ventana)",
        "formulas": "📘 Fórmulas",
        "footer": "© 2025 — Dimensionamiento, costos y cronograma. Ajustar a condiciones locales. Autores: Alejandro Taborda, Roosevelt Escobar, Sean Fenstemaker"
    },
    "EN": {
        "title": "STOCK & TUNNELS Scaler — with costs + timeline",
        "caption": "Compute **stock with irrigation (ha)**, **tunnel area (m²)**, compare **costs** (Irrigation+tunnels vs tunnels-only) and display a **minimal timeline** to reach the target, honoring rainy windows and ≥6-month stock maturity.",
        "sidebar_main": "🎯 Target & key assumptions",
        "meta": "Footprint target (ha)",
        "rho": "Planting density (plants/ha, ρ)",
        "stock_prod": "STOCK productivity",
        "cuts": "Cuttings per plant per year (stock)",
        "s_stock": "Stock viability (%)",
        "tunnels_prod": "Tunnels (productivity)",
        "r_cut": "Cuttings per m² per cut (r_cut)",
        "tau": "Months per cut (τ)",
        "s_tunnel": "Tunnel viability (%)",
        "calendar": "Calendar",
        "irrigation": "Irrigation in STOCK?",
        "commercial_window": "COMMERCIAL window (rainy months)",
        "stock_window": "STOCK window (if NO irrigation)",
        "L_stock_min": "Stock maturity minimum (months)",
        "prod_months_distrib": "Effective production/planting months per year (distributed)",
        "prod_months_window": "Window months (peak)",
        "renewal": "Stock renewal",
        "k_years": "Renewal cadence (years)",
        "mode_renewal": "Renewal mode",
        "mode_uniform": "Uniform annual (averaged)",
        "mode_batch": "Batch in replacement year",
        "tunnel_size": "Tunnel size (to convert to #)",
        "costs": "💸 Costs & currency",
        "currency": "Currency",
        "fx": "COP per USD (if using USD)",
        "tunnel_unit_cost": "Cost per tunnel (COP/unit)",
        "tc11": "Apply +11% (TC) to tunnel",
        "irrig_capex": "Irrigation CAPEX per STOCK ha (COP/ha)",
        "irrig_opex": "Irrigation OPEX per year (COP/ha/yr) — optional",
        "ciat_pkg": "🤝 Assistance / partnership package (CIAT)",
        "pkg_select": "Select level",
        "include_pkg": "Include package cost in total",
        "kpis_main": ["🎯 Target footprint (ha)", "🌱 Required stock (ha, with irrigation)", "🧪 Plants in stock"],
        "dim_tunnels": "📦 TUNNELS sizing",
        "distributed": "Distributed ({m} mo/yr)",
        "window_uniform": "Window (uniform, {m} mo)",
        "window_peak": "Window (peak year, {m} mo)",
        "cost_compare": "💰 Cost comparator — Multiplication to sustain the target",
        "A_title": "A) **Irrigation + tunnels (distributed)**",
        "B_title": "B) **Tunnels-only (window)**",
        "area_tunnels": "Tunnel area",
        "capex_tunnels": "Tunnels CAPEX",
        "capex_irrig": "Irrigation CAPEX (stock {ha:.1f} ha)",
        "opex_irrig": "Irrigation OPEX per year (reference)",
        "total_capex": "**Total CAPEX**",
        "cost_per_ha": "Cost per target ha ≈ {x}",
        "diff_A_better": "Given these inputs, **A) Irrigation + tunnels** needs **{x} less** CAPEX than **B) Tunnels-only**.",
        "diff_B_better": "Given these inputs, **B) Tunnels-only** needs **{x} less** CAPEX than **A) Irrigation + tunnels**.",
        "graph_scale_title": "Scaling: target (ha) → required stock (ha)",
        "graph_scale_x": "Target footprint (ha)",
        "graph_scale_y": "Required stock (ha)",
        "timeline": "🗓️ Minimal timeline (12–24 months)",
        "timeline_note": "Stock cohorts must be **≥ {L} months** before feeding each month of the commercial window. With irrigation, plant exactly {L} months earlier; without irrigation, shift planting to the **previous rainy month** in the stock window.",
        "timeline_stock": "Stock cohorts (planting)",
        "timeline_maturity": "Stock reaches maturity (≥{L} mo)",
        "timeline_deploy": "Commercial planting (window)",
        "formulas": "📘 Formulas",
        "footer": "© 2025 — Sizing, costs and timeline. Adjust to local conditions. Authors: Alejandro Taborda, Roosevelt Escobar, Sean Fenstemaker"
    }
}

MONTHS = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
MONTHS_ES = ["Ene","Feb","Mar","Abr","May","Jun","Jul","Ago","Sep","Oct","Nov","Dic"]

def roll_months(start_idx, ref):
    return ref[start_idx:] + ref[:start_idx]

lang = st.sidebar.selectbox("Language / Idioma", ["ES","EN"], index=0)
T = LANGS[lang]

st.title(T["title"])
st.caption(T["caption"])

st.sidebar.header(T["sidebar_main"])
H_target = st.sidebar.number_input(T["meta"], min_value=50, max_value=10000, value=1500, step=50)
rho = st.sidebar.number_input(T["rho"], min_value=5000, max_value=20000, value=10000, step=500)

st.sidebar.markdown("---")
st.sidebar.subheader(T["stock_prod"])
cuts_per_plant_year = st.sidebar.slider(T["cuts"], 4, 12, 8, step=1)
s_stock = st.sidebar.slider(T["s_stock"], 60, 100, 100, step=1) / 100.0

st.sidebar.markdown("---")
st.sidebar.subheader(T["tunnels_prod"])
r_cut = st.sidebar.slider(T["r_cut"], 60, 150, 100, step=5)
tau = st.sidebar.slider(T["tau"], 1, 6, 3, step=1)
s_tunnel = st.sidebar.slider(T["s_tunnel"], 60, 100, 85, step=1) / 100.0

st.sidebar.markdown("---")
st.sidebar.subheader(T["calendar"])
ref_months = MONTHS_ES if lang=="ES" else MONTHS
start_month_name = st.sidebar.selectbox("Start / Inicio", ref_months, index=0)
irrigation = st.sidebar.toggle(T["irrigation"], value=True)

# Windows
def preset_months(choice, lang="ES"):
    if "Mar-May" in choice:
        return ["Mar","Abr","May"] if lang=="ES" else ["Mar","Apr","May"]
    if "May-Aug" in choice:
        return ["May","Jun","Jul","Ago"] if lang=="ES" else ["May","Jun","Jul","Aug"]
    return []

commercial_options = ["Mar-May (Caribe)","May-Aug (Llanos)","Custom"] if lang=="ES" else ["Mar-May (Caribbean)","May-Aug (Llanos)","Custom"]
stock_options = commercial_options

cw_choice = st.sidebar.selectbox(T["commercial_window"], commercial_options, index=0)
sw_choice = st.sidebar.selectbox(T["stock_window"], stock_options, index=0)

cw = preset_months(cw_choice, lang=lang)
sw = preset_months(sw_choice, lang=lang)

if cw_choice=="Custom":
    cw = st.sidebar.multiselect(T["commercial_window"]+" (Custom)", ref_months, default=(["Mar","Abr","May"] if lang=="ES" else ["Mar","Apr","May"]))
if not irrigation and sw_choice=="Custom":
    sw = st.sidebar.multiselect(T["stock_window"]+" (Custom)", ref_months, default=(["Mar","Abr","May"] if lang=="ES" else ["Mar","Apr","May"]))

L_stock_min = st.sidebar.slider(T["L_stock_min"], 3, 12, 6, step=1)
m_prod_distrib = st.sidebar.slider(T["prod_months_distrib"], 1, 12, 12, step=1)
m_prod_ventana = st.sidebar.slider(T["prod_months_window"], 1, 6, 3, step=1)

st.sidebar.markdown("---")
st.sidebar.subheader(T["renewal"])
k_years = st.sidebar.select_slider(T["k_years"], options=[1,2,3,4,5], value=1)
mode_renewal = st.sidebar.selectbox(T["mode_renewal"], [T["mode_uniform"], T["mode_batch"]], index=0)

st.sidebar.markdown("---")
st.sidebar.subheader(T["tunnel_size"])
tunnel_size = st.sidebar.selectbox("Tunnel size", ["27 m²","36.75 m²"], index=0)
tunnel_m2 = 27.0 if tunnel_size.startswith("27") else 36.75

st.sidebar.markdown("---")
st.sidebar.subheader(T["costs"])
currency = st.sidebar.selectbox(T["currency"], ["COP","USD"], index=0)
fx_rate = st.sidebar.number_input(T["fx"], min_value=1000, max_value=20000, value=4200, step=100)
cost_per_tunnel_unit_COP = st.sidebar.number_input(T["tunnel_unit_cost"], min_value=0, max_value=200_000_000, value=8_000_000, step=200_000)
apply_TC_11pct = st.sidebar.toggle(T["tc11"], value=False)
cost_irrigation_per_ha_COP = st.sidebar.number_input(T["irrig_capex"], min_value=0, max_value=50_000_000, value=6_500_000, step=250_000)
opex_irrigation_per_ha_COP = st.sidebar.number_input(T["irrig_opex"], min_value=0, max_value=10_000_000, value=0, step=100_000)

# Packages
st.sidebar.subheader(T["ciat_pkg"])
pkg_map_usd = {
    ("ES","Básico — Genética limpia (USD 20k)"): 20000,
    ("ES","Intermedio — Multiplicación & asistencia (USD 50k)"): 50000,
    ("ES","Full — Genética + Seed system + Extension (USD 95k)"): 95000,
    ("EN","Basic — Clean genetics (USD 20k)"): 20000,
    ("EN","Intermediate — Multiplication & TA (USD 50k)"): 50000,
    ("EN","Full — Genetics + Seed system + Extension (USD 95k)"): 95000,
}
pkg_options = [k[1] for k in pkg_map_usd.keys() if k[0]==lang]
pkg_choice = st.sidebar.selectbox(T["pkg_select"], pkg_options, index=0)
include_pkg = st.sidebar.toggle(T["include_pkg"], value=True)

def to_mode(x_cop):
    return x_cop / fx_rate if currency=="USD" else x_cop

def fmt_money(x_cop):
    unit = "USD" if currency=="USD" else "COP"
    return f"${to_mode(x_cop):,.0f} {unit}"

# Sizing
stakes_per_year_needed = H_target * rho
plants_stock_needed = stakes_per_year_needed / max(cuts_per_plant_year * s_stock, 1e-9)
stock_ha = plants_stock_needed / rho

q_m2_month = (r_cut / max(tau, 1)) * s_tunnel
q_m2_year_distrib = q_m2_month * m_prod_distrib
q_m2_year_window = q_m2_month * m_prod_ventana

annual_stock_plants_uniform = plants_stock_needed / k_years
T_m2_uniform_distrib = annual_stock_plants_uniform / max(q_m2_year_distrib, 1e-9)
T_m2_uniform_window  = annual_stock_plants_uniform / max(q_m2_year_window,  1e-9)
T_m2_batch_window    = plants_stock_needed / max(q_m2_year_window, 1e-9)

def tunnels_needed(area_m2, tunnel_m2):
    import math
    return math.ceil(area_m2 / max(tunnel_m2, 1e-9))

n_tun_uniform_distrib = tunnels_needed(T_m2_uniform_distrib, tunnel_m2)
n_tun_uniform_window  = tunnels_needed(T_m2_uniform_window,  tunnel_m2)
n_tun_batch_window    = tunnels_needed(T_m2_batch_window,    tunnel_m2)

# Costs
cost_per_m2_tunnel_COP = cost_per_tunnel_unit_COP / max(tunnel_m2, 1e-9)
if apply_TC_11pct:
    cost_per_m2_tunnel_COP *= 1.11

A_T_m2 = T_m2_uniform_distrib
A_n_tun = n_tun_uniform_distrib
A_capex_tunnels_COP = A_T_m2 * cost_per_m2_tunnel_COP
A_capex_irrig_COP = stock_ha * cost_irrigation_per_ha_COP
A_total_capex_COP = A_capex_tunnels_COP + A_capex_irrig_COP
A_opex_irrig_annual_COP = stock_ha * opex_irrigation_per_ha_COP

B_T_m2 = (T_m2_uniform_window if mode_renewal==T["mode_uniform"] else T_m2_batch_window)
B_n_tun = (n_tun_uniform_window if mode_renewal==T["mode_uniform"] else n_tun_batch_window)
B_capex_tunnels_COP = B_T_m2 * cost_per_m2_tunnel_COP
B_total_capex_COP = B_capex_tunnels_COP

pkg_usd = pkg_map_usd[(lang, pkg_choice)]
pkg_cop = pkg_usd * fx_rate
pkg_text = f"{pkg_choice} — ${pkg_usd:,.0f} USD"

if include_pkg:
    A_total_capex_COP += pkg_cop
    B_total_capex_COP += pkg_cop

# KPIs
k1, k2, k3 = st.columns(3)
k1.metric(T["kpis_main"][0], f"{H_target:,}")
k2.metric(T["kpis_main"][1], f"{stock_ha:,.1f}")
k3.metric(T["kpis_main"][2], f"{int(plants_stock_needed):,}")

st.markdown("---")
st.subheader(T["dim_tunnels"])
c1, c2, c3 = st.columns(3)
c1.metric(T["distributed"].format(m=m_prod_distrib), f"{T_m2_uniform_distrib:,.0f} m²")
c1.metric("≈ # tunnels", f"{n_tun_uniform_distrib:,} @ {tunnel_m2} m²")
c2.metric(T["window_uniform"].format(m=m_prod_ventana), f"{T_m2_uniform_window:,.0f} m²")
c2.metric("≈ # tunnels", f"{n_tun_uniform_window:,} @ {tunnel_m2} m²")
c3.metric(T["window_peak"].format(m=m_prod_ventana), f"{T_m2_batch_window:,.0f} m²")
c3.metric("≈ # tunnels", f"{n_tun_batch_window:,} @ {tunnel_m2} m²")

st.markdown("---")
st.subheader(T["cost_compare"])
colA, colB = st.columns(2)
with colA:
    st.markdown("### " + T["A_title"])
    st.metric(T["area_tunnels"], f"{A_T_m2:,.0f} m²  →  ≈ {A_n_tun:,} túneles")
    st.write(f"- {T['capex_tunnels']}: **{fmt_money(A_capex_tunnels_COP)}**")
    st.write(f"- {T['capex_irrig'].format(ha=stock_ha)}: **{fmt_money(A_capex_irrig_COP)}**")
    if A_opex_irrig_annual_COP > 0:
        st.write(f"- {T['opex_irrig']}: **{fmt_money(A_opex_irrig_annual_COP)}**")
    if include_pkg:
        st.write(f"- {pkg_text}")
    st.success(f"{T['total_capex']}: {fmt_money(A_total_capex_COP)}")
    st.caption(T["cost_per_ha"].format(x=fmt_money(A_total_capex_COP/max(H_target,1))))

with colB:
    st.markdown("### " + T["B_title"])
    st.metric(T["area_tunnels"], f"{B_T_m2:,.0f} m²  →  ≈ {B_n_tun:,} túneles")
    st.write(f"- {T['capex_tunnels']}: **{fmt_money(B_capex_tunnels_COP)}**")
    if include_pkg:
        st.write(f"- {pkg_text}")
    st.success(f"{T['total_capex']}: {fmt_money(B_total_capex_COP)}")
    st.caption(T["cost_per_ha"].format(x=fmt_money(B_total_capex_COP/max(H_target,1))))

diff = B_total_capex_COP - A_total_capex_COP
if diff != 0:
    st.markdown("---")
    if diff > 0:
        st.success(T["diff_A_better"].format(x=fmt_money(diff)))
    else:
        st.warning(T["diff_B_better"].format(x=fmt_money(-diff)))

# Graph: scaling
xs = np.array([100,200,400,600,800,1000,1200,1500,2000,2500])
ys = xs / max(cuts_per_plant_year * s_stock, 1e-9)
fig = go.Figure()
fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines+markers", name="Stock (ha)"))
fig.add_hline(y=stock_ha, line=dict(dash="dot"), annotation_text=f"{stock_ha:,.1f} ha")
fig.add_vline(x=H_target, line=dict(dash="dot"), annotation_text=f"{H_target:,} ha")
fig.update_layout(title=T["graph_scale_title"],
                  xaxis_title=T["graph_scale_x"],
                  yaxis_title=T["graph_scale_y"],
                  margin=dict(l=40,r=40,t=60,b=40))
st.plotly_chart(fig, use_container_width=True)

# Timeline
st.markdown("---")
st.subheader(T["timeline"])
st.caption(T["timeline_note"].format(L=L_stock_min))

start_idx = ref_months.index(start_month_name)
months24 = [ref_months[(start_idx+i)%12] + f"-{1+(start_idx+i)//12}" for i in range(24)]

def indices_of(month_names, ref):
    return [ref.index(m) for m in month_names if m in ref]

cw_idx = indices_of(cw, ref_months)
sw_idx = indices_of(sw, ref_months) if not irrigation else list(range(12))

events = []
for cm in cw_idx:
    if cm >= start_idx:
        abs_cm = cm - start_idx
    else:
        abs_cm = (12 - start_idx) + cm
    abs_stock = abs_cm - L_stock_min
    if abs_stock < 0:
        abs_stock += 12
    if not irrigation:
        while (abs_stock % 12) not in sw_idx and abs_stock > 0:
            abs_stock -= 1
    abs_maturity = abs_stock + L_stock_min
    abs_stock = max(0, min(23, abs_stock))
    abs_maturity = max(0, min(23, abs_maturity))
    abs_cm = max(0, min(23, abs_cm))
    events.append(("stock", abs_stock))
    events.append(("maturity", abs_maturity))
    events.append(("commercial", abs_cm))

y_stock = np.zeros(24); y_mat = np.zeros(24); y_com = np.zeros(24)
for typ, idx in events:
    if 0 <= idx < 24:
        if typ=="stock": y_stock[idx]+=1
        if typ=="maturity": y_mat[idx]+=1
        if typ=="commercial": y_com[idx]+=1

tl = go.Figure()
tl.add_trace(go.Bar(x=months24, y=y_stock, name=T["timeline_stock"]))
tl.add_trace(go.Bar(x=months24, y=y_mat, name=T["timeline_maturity"]))
tl.add_trace(go.Bar(x=months24, y=y_com, name=T["timeline_deploy"]))
tl.update_layout(barmode="stack", margin=dict(l=40,r=40,t=60,b=40))

shapes = []
for i, lab in enumerate(months24):
    mon = lab.split("-")[0]
    if mon in cw:
        shapes.append(dict(type="rect", xref="x", yref="paper",
                           x0=lab, x1=lab, y0=0, y1=1,
                           line=dict(width=0), fillcolor="rgba(100,149,237,0.12)"))
    if (not irrigation) and (mon in sw):
        shapes.append(dict(type="rect", xref="x", yref="paper",
                           x0=lab, x1=lab, y0=0, y1=1,
                           line=dict(width=0), fillcolor="rgba(60,179,113,0.10)"))
tl.update_layout(shapes=shapes, xaxis_title="Mes / Month", yaxis_title="Cohortes")
st.plotly_chart(tl, use_container_width=True)

with st.expander(T["formulas"]):
    st.markdown(f"""
- Annual cuttings required: `H_target × ρ`.
- Plants in STOCK: `(H_target × ρ) / (cuts_per_plant_year × s_stock)` → `stock_ha = H_target / (cuts_per_plant_year × s_stock)`.
- Tunnels monthly productivity: `(r_cut/τ) × s_tunnel` → yearly: × months (`{m_prod_distrib}` distributed, `{m_prod_ventana}` window).
- Renewal **{k_years}y** — {mode_renewal}.
- Timeline: stock cohorts must be **≥ {L_stock_min} months** old at commercial month; if no irrigation, shift planting to previous rainy month in stock window.
- CIAT/partnership packages: stakeholder-dependent scope (clean genetics / multiplication TA / full package). Cost added if toggled.
""")

st.caption(T["footer"])
