import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# Configuración de la página web
st.set_page_config(page_title="Supervisión de Redes GN", layout="wide")

st.title("Calculadora de Supervisión de Redes de Gas Natural")
st.markdown("Gestión de Dossier y Muestreo según **Resolución N° 283-2015-OS/CD**")

# 1. Constantes normativas
t_alpha = 1.645
d = 0.05
S2h = 0.25  # Varianza máxima asumida
C = (t_alpha**2) * S2h
asintota_max = C / (d**2)

# ==========================================
# 2. INTERFAZ DE USUARIO (PANEL LATERAL)
# ==========================================
st.sidebar.header("Configuración del Proyecto")

# Entrada maestra: Total Actas Minem
n_poblacion_total = st.sidebar.number_input("Total Actas (Minem) [m]:", min_value=0.0, value=2021.06, format="%g")

# --- CONJUNTO 1: TIPO DE TERRENO ---
st.sidebar.subheader("Estratos: Tipo de Terreno")
opciones_terreno = ["Normal", "Arenoso", "Semirocoso", "Rocoso"]
datos_terreno = {}

for t in opciones_terreno:
    if st.sidebar.checkbox(f"Terreno {t}", value=True if t=="Normal" else False, key=f"chk_t_{t}"):
        val = st.sidebar.number_input(f"Metros - {t}:", min_value=0.0, value=0.0, format="%g", key=f"val_t_{t}")
        if val > 0: datos_terreno[t] = val

# --- CONJUNTO 2: TIPO DE PAVIMENTO ---
st.sidebar.subheader("Estratos: Tipo de Pavimento")
opciones_pavimento = ["Afirmado", "Flexible", "Rígido", "Mixto"]
datos_pavimento = {}

for p in opciones_pavimento:
    if st.sidebar.checkbox(f"Pavimento {p}", value=True if p=="Flexible" else False, key=f"chk_p_{p}"):
        val = st.sidebar.number_input(f"Metros - {p}:", min_value=0.0, value=0.0, format="%g", key=f"val_p_{p}")
        if val > 0: datos_pavimento[p] = val

# ==========================================
# 3. VALIDACIÓN Y CÁLCULOS
# ==========================================
if n_poblacion_total > 0:
    suma_t = sum(datos_terreno.values())
    suma_p = sum(datos_pavimento.values())
    
    # Validamos que las sumas coincidan con el total de Actas
    error_margen = 0.01
    terreno_ok = abs(suma_t - n_poblacion_total) < error_margen
    pavimento_ok = abs(suma_p - n_poblacion_total) < error_margen

    if not (terreno_ok and pavimento_ok):
        st.warning("⚠️ **Inconsistencia en los metrados:**")
        col_err1, col_err2, col_err3 = st.columns(3)
        col_err1.write(f"**Actas (Minem):** {n_poblacion_total:,.2f} m")
        col_err2.error(f"**Suma Terrenos:** {suma_t:,.2f} m")
        col_err3.error(f"**Suma Pavimentos:** {suma_p:,.2f} m")
        st.info("Ajusta los valores para que ambas sumas igualen el total de Actas Minem.")
    else:
        # Cálculo del n supervisar (único para el proyecto)
        n_supervisar = C / ((d**2) + (C / n_poblacion_total))
        porcentaje_fijo = (n_supervisar / n_poblacion_total) * 100

        # Resumen Principal
        st.subheader("=== RESUMEN FINAL DEL EXPEDIENTE ===")
        c1, c2, c3 = st.columns(3)
        c1.metric("Población Confirmada (N)", f"{n_poblacion_total:,.2f} m")
        c2.metric("Total a Supervisar (n)", f"{n_supervisar:,.2f} m")
        c3.metric("Porcentaje Global", f"{porcentaje_fijo:.2f} %")

        # ==========================================
        # 4. LAS DOS MATRICES (LADO A LADO)
        # ==========================================
        st.divider()
        col_mat1, col_mat2 = st.columns(2)

        with col_mat1:
            st.markdown("### Matrix A: Tipo de Terreno")
            filas_t = []
            for k, v in datos_terreno.items():
                wh = v / n_poblacion_total
                nh = n_supervisar * wh
                filas_t.append({"Terreno": k, "Población (Nh)": f"{v:,.2f} m", "Muestra (nh)": f"{nh:,.2f} m", "%": f"{(nh/v)*100:.2f}%"})
            st.table(pd.DataFrame(filas_t))

        with col_mat2:
            st.markdown("### Matrix B: Tipo de Pavimento")
            filas_p = []
            for k, v in datos_pavimento.items():
                wh = v / n_poblacion_total
                nh = n_supervisar * wh
                filas_p.append({"Pavimento": k, "Población (Nh)": f"{v:,.2f} m", "Muestra (nh)": f"{nh:,.2f} m", "%": f"{(nh/v)*100:.2f}%"})
            st.table(pd.DataFrame(filas_p))

        # ==========================================
        # 5. GRÁFICO ÚNICO DE PROYECCIÓN
        # ==========================================
        st.divider()
        st.markdown("### Proyección de Supervisión del Proyecto")
        
        x_max = max(n_poblacion_total, n_poblacion_total * 1.5)
        N_vals = np.linspace(10, x_max, 1000)
        n_vals = C / ((d**2) + (C / N_vals))

        fig, ax = plt.subplots(figsize=(11, 5))
        ax.plot(N_vals, n_vals, color='#1f77b4', lw=3, label='Curva de muestreo ($n$)')
        ax.axhline(y=asintota_max, color='red', ls='--', lw=2, alpha=0.8, label=f'Asíntota Máx: ~{asintota_max:.1f} m')
        ax.plot(n_poblacion_total, n_supervisar, 'ko', ms=9, zorder=5)
        
        ax.vlines(n_poblacion_total, 0, n_supervisar, color='gray', ls=':', alpha=0.7)
        ax.hlines(n_supervisar, 0, n_poblacion_total, color='gray', ls=':', alpha=0.7)

        texto = f'Proyecto Actual:\nN: {n_poblacion_total:,.0f} m\nn: {n_supervisar:.1f} m\n%: {porcentaje_fijo:.2f}%'
        off_x = -0.15 if n_poblacion_total > (x_max * 0.7) else 0.03
        ax.annotate(texto, xy=(n_poblacion_total, n_supervisar), 
                    xytext=(n_poblacion_total + (x_max * off_x), n_supervisar - 60),
                    bbox=dict(boxstyle="round,pad=0.5", fc="#f8f9fa", ec="gray", lw=1.5),
                    arrowprops=dict(arrowstyle="->", color='black', lw=1.5))

        ax.set_title('Proyección de Supervisión', fontsize=14, fontweight='bold')
        ax.set_xlabel('Total del Proyecto (N en metros)', fontsize=11)
        ax.set_ylabel('Cantidad Supervisada (n)', fontsize=11)
        ax.set_xlim(0, x_max)
        ax.set_ylim(0, asintota_max * 1.2)
        ax.grid(True, ls='--', alpha=0.5)
        ax.legend(loc='lower right')

        st.pyplot(fig)
else:
    st.info("👈 Ingrese el Total de Actas (Minem) para iniciar el cálculo.")
