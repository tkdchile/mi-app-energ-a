import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# ============================================================================
# 1. CONFIGURACIÓN DE PÁGINA Y ESTILOS (SCROLLYTELLING)
# ============================================================================
st.set_page_config(
    page_title="Monitor Energético: Latinoamérica y el Mundo",
    page_icon="🌎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos Web & Tipografía (Diseño V7)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Lato:wght@300;400;700&display=swap');
    
    html, body, [class*="css"] { font-family: 'Lato', sans-serif; color: #1e293b; }
    
    /* Estilos de Títulos Narrativos */
    .chapter-number { 
        color: #3b82f6; font-weight: 700; letter-spacing: 2px; font-size: 0.9rem; text-transform: uppercase; margin-top: 2rem;
    }
    .chapter-title { 
        color: #0f172a; font-size: 2.5rem; font-weight: 700; margin-bottom: 1.5rem; border-left: 6px solid #3b82f6; padding-left: 20px; 
    }
    
    /* Tarjetas de KPI */
    .kpi-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        border: 1px solid #e2e8f0; border-radius: 16px; padding: 25px;
        text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        transition: transform 0.2s;
    }
    .kpi-card:hover { transform: translateY(-3px); }
    .kpi-val { font-size: 2.2rem; font-weight: 800; color: #2563eb; margin: 0; }
    .kpi-lbl { font-size: 0.9rem; color: #64748b; text-transform: uppercase; letter-spacing: 1px; margin-top: 5px; }
    
    /* Cajas de Insights */
    .insight-box {
        background-color: #f0fdf4; border-left: 5px solid #22c55e;
        padding: 1.2rem; border-radius: 0 8px 8px 0; margin: 1.5rem 0;
        font-size: 1.05rem; color: #14532d;
    }
    
    /* Ocultar elementos nativos para look App */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ============================================================================
# 2. CARGA DE DATOS ROBUSTA
# ============================================================================
@st.cache_data
def load_data():
    if not os.path.exists('owid-energy-data.csv'):
        return None
    
    df = pd.read_csv('owid-energy-data.csv')
    
    # Limpieza: Eliminar regiones agregadas (World, Africa, etc.) usando ISO Code
    df_clean = df[df['iso_code'].notna()].copy()
    
    # Pre-cálculo: Dependencia Fósil
    fossil_cols = ['coal_share_energy', 'oil_share_energy', 'gas_share_energy']
    if all(c in df_clean.columns for c in fossil_cols):
        df_clean['fossil_share_total'] = df_clean[fossil_cols].sum(axis=1, min_count=1)
        
    return df_clean

df = load_data()

if df is None:
    st.error("⚠️ Error Crítico: No se encuentra 'owid-energy-data.csv'.")
    st.stop()

# ============================================================================
# 3. SIDEBAR: CONTROL DE ÁMBITO Y NAVEGACIÓN
# ============================================================================
st.sidebar.title("🧭 Navegación")

# 1. Navegación Scrollytelling
step = st.sidebar.radio(
    "Capítulos:",
    ["1. Introducción & Volumen", "2. Velocidad de Transición", "3. Eficiencia Económica", "4. Conclusiones"]
)
st.sidebar.progress({"1. Introducción & Volumen": 25, "2. Velocidad de Transición": 50, "3. Eficiencia Económica": 75, "4. Conclusiones": 100}[step])

st.sidebar.markdown("---")
st.sidebar.header("🌍 Filtro de Ámbito")

# 2. Filtro Regional
region_mode = st.sidebar.selectbox(
    "Selecciona la Región de Análisis:",
    ["OCDE (Economías Maduras)", "Latinoamérica", "Global (Todos los Países)"]
)

# LISTAS DE PAÍSES (Ampliadas y Revisadas)
oecd_list = ['Australia', 'Austria', 'Belgium', 'Canada', 'Chile', 'Colombia', 'Costa Rica', 
             'Czechia', 'Denmark', 'Estonia', 'Finland', 'France', 'Germany', 'Greece', 
             'Hungary', 'Iceland', 'Ireland', 'Israel', 'Italy', 'Japan', 'South Korea', 
             'Latvia', 'Lithuania', 'Luxembourg', 'Mexico', 'Netherlands', 'New Zealand', 
             'Norway', 'Poland', 'Portugal', 'Slovakia', 'Slovenia', 'Spain', 'Sweden', 
             'Switzerland', 'Turkey', 'United Kingdom', 'United States']

# LATAM COMPLETA (20 Países)
latam_list = [
    'Argentina', 'Bolivia', 'Brazil', 'Chile', 'Colombia', 'Costa Rica', 'Cuba', 
    'Dominican Republic', 'Ecuador', 'El Salvador', 'Guatemala', 'Haiti', 'Honduras', 
    'Mexico', 'Nicaragua', 'Panama', 'Paraguay', 'Peru', 'Uruguay', 'Venezuela'
]

# Lógica de Filtrado
if region_mode == "OCDE (Economías Maduras)":
    target_countries = oecd_list
elif region_mode == "Latinoamérica":
    target_countries = latam_list
else:
    target_countries = df['country'].unique()

# DataFrame Maestro Filtrado (df_scope)
df_scope = df[df['country'].isin(target_countries)]

# Feedback Visual
count_countries = len(df_scope['country'].unique())
st.sidebar.success(f"✅ Analizando **{count_countries}** países")

# ============================================================================
# 4. NARRATIVA INTERACTIVA (SCROLLYTELLING)
# ============================================================================

# HEADER PRINCIPAL
st.markdown(f"""
<div style="text-align: center; padding: 3rem 0;">
    <h1 style="font-size: 3.5rem; color: #1e3a8a; font-weight: 800; margin-bottom: 0;">La Transición Energética</h1>
    <h3 style="font-size: 1.5rem; color: #3b82f6; margin-top: 10px;">Enfoque: {region_mode}</h3>
    <p style="font-size: 1.2rem; color: #64748b; margin-top: 20px;">Un viaje interactivo desde la demanda física hasta la eficiencia económica.</p>
</div>
""", unsafe_allow_html=True)

st.divider()

# --- CAPÍTULO 1: VOLUMEN ---
if step == "1. Introducción & Volumen":
    st.markdown('<div class="chapter-number">CAPÍTULO 1</div>', unsafe_allow_html=True)
    st.markdown('<div class="chapter-title">La Realidad Física (TWh)</div>', unsafe_allow_html=True)
    
    st.markdown("""
    Los porcentajes cuentan historias de cambio, pero los **volúmenes (TWh)** cuentan historias de infraestructura. 
    Para entender el desafío, primero debemos medir la demanda total absoluta.
    """)

    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("### 🏳️ Foco País")
        # Selector Dinámico Seguro
        opts = sorted(df_scope['country'].unique())
        # Default inteligente: Intenta Chile, si no, el primero
        def_ix = opts.index("Chile") if "Chile" in opts else 0
        
        country_sel = st.selectbox("Analizar Demanda de:", opts, index=def_ix)
        
        # KPI Card
        c_data = df[df['country'] == country_sel]
        if not c_data.empty:
            last = c_data.iloc[-1]
            st.markdown(f"""
            <br>
            <div class="kpi-card">
                <div class="kpi-val">{last['primary_energy_consumption']:,.0f} TWh</div>
                <div class="kpi-lbl">Consumo Total ({int(last['year'])})</div>
            </div>
            """, unsafe_allow_html=True)

    with col2:
        # Gráfico de Área
        plot_df = df[(df['country'] == country_sel) & (df['year'] >= 1990)].fillna(0)
        sources = ['coal_consumption', 'oil_consumption', 'gas_consumption', 'nuclear_consumption', 'renewables_consumption']
        labels = {'coal_consumption': 'Carbón', 'oil_consumption': 'Petróleo', 'gas_consumption': 'Gas', 'nuclear_consumption': 'Nuclear', 'renewables_consumption': 'Renovables'}
        
        if not plot_df.empty:
            # Solo graficar fuentes que existen
            valid_src = [s for s in sources if s in plot_df.columns]
            
            fig = px.area(plot_df, x='year', y=valid_src,
                          color_discrete_sequence=px.colors.qualitative.Safe,
                          labels={'value': 'TWh', 'variable': 'Fuente'})
            
            # Formato narrativo
            fig.for_each_trace(lambda t: t.update(name = labels.get(t.name, t.name)))
            fig.update_layout(title=f"Matriz Histórica: {country_sel}", hovermode="x unified", legend=dict(orientation="h", y=1.1))
            st.plotly_chart(fig, use_container_width=True)

    st.markdown("""
    <div class="insight-box">
    <strong>💡 Hallazgo:</strong> Observe la diferencia de escala. Si cambia entre un país desarrollado y uno en desarrollo, 
    verá que en los primeros la curva suele aplanarse, mientras que en Latam sigue en ascenso por la necesidad de industrialización.
    </div>
    """, unsafe_allow_html=True)

# --- CAPÍTULO 2: VELOCIDAD ---
elif step == "2. Velocidad de Transición":
    st.markdown('<div class="chapter-number">CAPÍTULO 2</div>', unsafe_allow_html=True)
    st.markdown('<div class="chapter-title">La Velocidad del Cambio (%)</div>', unsafe_allow_html=True)
    
    st.markdown("¿Qué países están acelerando más rápido su adopción de energías variables (Solar + Eólica)?")

    recent_df = df_scope[df_scope['year'] >= 2010].copy()
    
    if not recent_df.empty:
        # Defaults Seguros (Que existan en Latam si se selecciona Latam)
        opts = sorted(recent_df['country'].unique())
        wanted = ["Chile", "Brazil", "Mexico", "Germany", "China"] # Lista de deseos
        defaults = [c for c in wanted if c in opts] # Intersección segura
        
        sel = st.multiselect("Comparar Curvas de Adopción:", opts, default=defaults[:3]) # Max 3 por defecto
        
        if sel:
            subset = recent_df[recent_df['country'].isin(sel)].copy()
            subset['var_renewables'] = subset['solar_share_energy'].fillna(0) + subset['wind_share_energy'].fillna(0)
            
            fig = px.line(subset, x='year', y='var_renewables', color='country', markers=True,
                          title="Cuota Solar + Eólica en Energía Primaria (%)",
                          color_discrete_sequence=px.colors.qualitative.Bold)
            fig.update_layout(yaxis_tickformat=".1f%", hovermode="x unified")
            st.plotly_chart(fig, use_container_width=True)
            
            st.success("🚀 **Chile en el Liderazgo:** Note cómo la pendiente de Chile suele ser más pronunciada que la de sus vecinos, indicando una penetración agresiva de renovables no convencionales.")
    else:
        st.warning("No hay datos recientes para esta región.")

# --- CAPÍTULO 3: EFICIENCIA ---
elif step == "3. Eficiencia Económica":
    st.markdown('<div class="chapter-number">CAPÍTULO 3</div>', unsafe_allow_html=True)
    st.markdown('<div class="chapter-title">Matriz de Eficiencia (Desacoplamiento)</div>', unsafe_allow_html=True)
    
    st.markdown(f"Análisis de correlación (2000-2022) para **{count_countries} países**.")

    # Cálculo Robusto
    def calc_eff(dframe):
        res = []
        for c in dframe['country'].unique():
            cd = dframe[dframe['country'] == c]
            try:
                # Lógica: Base 2000 vs Último Dato Válido
                base = cd[cd['year'] == 2000]
                valid = cd[(cd['year'] >= 2019) & (cd['gdp'].notna()) & (cd['primary_energy_consumption'].notna())]
                
                if base.empty or valid.empty: continue
                
                curr = valid.iloc[-1]
                g0, e0 = base['gdp'].values[0], base['primary_energy_consumption'].values[0]
                
                # Evitar división por cero
                if g0 == 0 or e0 == 0: continue

                g_chg = (curr['gdp'] - g0)/g0 * 100
                e_chg = (curr['primary_energy_consumption'] - e0)/e0 * 100
                
                cat = "Eficiente (Desacoplado)" if (g_chg > 0 and e_chg < 0) else "Convencional (Acoplado)"
                res.append({'País': c, 'PIB %': g_chg, 'Energía %': e_chg, 'Tipo': cat, 'Pop': curr['population']})
            except: continue
        return pd.DataFrame(res)

    eff_df = calc_eff(df_scope)

    if not eff_df.empty:
        col1, col2 = st.columns([3, 1])
        with col1:
            fig = px.scatter(eff_df, x='PIB %', y='Energía %', color='Tipo', size='Pop', hover_name='País',
                             color_discrete_map={"Eficiente (Desacoplado)": "#10b981", "Convencional (Acoplado)": "#ef4444"},
                             size_max=60, title=f"Mapa de Desacoplamiento: {region_mode}")
            
            # Líneas de referencia
            fig.add_hline(y=0, line_dash="dash", annotation_text="Límite Crecimiento Energía")
            fig.add_vline(x=0, line_dash="dash", annotation_text="Límite Recesión")
            fig.update_layout(template="plotly_white", height=500)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            n_eff = len(eff_df[eff_df['Tipo']=='Eficiente (Desacoplado)'])
            st.markdown(f"""
            <div class="kpi-card" style="padding:15px;">
                <div class="kpi-val" style="color:#10b981;">{n_eff}</div>
                <div class="kpi-lbl">Países Eficientes</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("### 📋 Top Rankings")
            if region_mode == "Latinoamérica":
                 st.markdown("En Latam, el desacoplamiento absoluto es raro debido a la fase de desarrollo.")
            
            # Tabla Top
            top = eff_df[eff_df['Tipo']=='Eficiente (Desacoplado)'].sort_values('Energía %').head(5)
            if not top.empty:
                st.dataframe(top[['País', 'Energía %']], hide_index=True)
    else:
        st.info("Datos insuficientes para cálculo histórico en esta selección.")

# --- CAPÍTULO 4: CONCLUSIONES ---
elif step == "4. Conclusiones":
    st.markdown('<div class="chapter-number">CIERRE</div>', unsafe_allow_html=True)
    st.markdown('<div class="chapter-title">Conclusiones y Futuro</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        ### 📌 Hallazgos del Estudio
        1. **Latinoamérica vs OCDE:** Mientras Europa busca reducir consumo (eficiencia), Latinoamérica busca limpiar su crecimiento (transición), ya que su demanda sigue aumentando.
        2. **Velocidad Solar:** Chile destaca como un caso de éxito global en la velocidad de adopción solar, superando promedios de la OCDE en la última década.
        """)
    
    with col2:
        st.markdown("""
        ### 🚀 Siguientes Pasos
        * **Análisis de Seguridad:** Integrar datos de importación/exportación para medir la independencia energética.
        * **Modelo Predictivo:** Usar series temporales (ARIMA) para proyectar si Chile alcanzará su meta de Carbono Neutralidad 2050.
        """)