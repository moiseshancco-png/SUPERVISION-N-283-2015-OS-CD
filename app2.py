import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# Configuración de la página web
st.set_page_config(page_title="Supervisión: Terreno y Pavimento", layout="wide")

st.title("Dossier de Supervisión: Terrenos y Pavimentos")
st.markdown("Distribución de muestreo según **Resolución N° 283-2015-OS/CD**")

# 1. Constantes normativas
t_alpha = 1.645
d = 0.05
S2h = 0.25  # Varianza máxima asumida
C = (t_alpha**2) * S2h

# ==========================================
# PANEL LATERAL: INGRESO DE DATOS Y CHECKLISTS
# ==========================================
st.sidebar.header("1. Población Total")
actas_minem = st.sidebar.number_input("Total Actas (Minem) [m]:", min_value=0.0, value=2021.06, format="%g")

# --- Estratos de Terreno ---
st.sidebar.header("2. Tipo de Terreno")
st.sidebar.caption("Marca los que apliquen y define su longitud:")
opciones_terreno = ["(1) Normal", "(2) Arenoso", "(3) Semirocoso", "(4) Rocoso"]
datos_terreno = {}

for t in opciones_terreno:
    # Checkbox para activar el estrato
    if st.sidebar.checkbox(t, value=True if t == "(1) Normal" else False, key=f"chk_t_{t}"):
        # Si está activado, mostramos el input de metros
        val = st.sidebar.number_input(f"Metros de {t}:", min_value=0.0, value=0.0, format="%g", key=f"val_t_{t}")
        if val > 0:
            datos_terreno[t] = val

# --- Estratos de Pavimento ---
st.sidebar.header("3. Tipo de Pavimento")
st.sidebar.caption("Marca los que apliquen y define su longitud:")
opciones_pavimento = ["(1) Afirmado", "(2) Flexible", "(3) Rígido", "(4) Mixto"]
datos_pavimento = {}

for p in opciones_pavimento:
    if st.sidebar.checkbox(p, value=True if p == "(2) Flexible" else False, key=f"chk_p_{p}"):
        val = st.sidebar.number_input(f"Metros de {p}:", min_value=0.0, value=0.0, format="%g", key=f"val_p_{p}")
        if val > 0:
            datos_pavimento[p] = val

# ==========================================
# LÓGICA DE VALIDACIÓN Y CÁLCULOS
# ==========================================
if actas_minem > 0:
    suma_terreno = sum(datos_terreno.values())
    suma_pavimento = sum(datos_pavimento.values())
    
    # Tolerancia de 2 decimales para evitar errores de redondeo interno de la PC
    terreno_valido = round(suma_terreno, 2) == round(actas_minem, 2)
    pavimento_valido = round(suma_pavimento, 2) == round(actas_minem, 2)

    if not (terreno_valido and pavimento_valido):
        # Mensaje de Error si no cuadran las sumas
        st.error("⚠️ **Alerta de Inconsistencia:** Las sumas de los estratos no coinciden con la Población Total.")
        st.markdown(f"""
        Para proceder con el cálculo oficial, los tres valores deben ser idénticos:
        * **Total Actas (Minem):** `{actas_minem:,.2f} m`
        * **Suma Tipo de Terreno:** `{suma_terreno:,.2f} m` 
        * **Suma Tipo de Pavimento:** `{suma_pavimento:,.2f} m`
        
        👉 *Ajusta los valores en el panel izquierdo para balancear el proyecto.*
        """)
    else:
        # Si todo es correcto, hacemos el cálculo
        st.success("✅ **Validación Exitosa:** Los metrados cuadran perfectamente. Procediendo con el cálculo de muestreo.")
        
        # Muestra total (n) basada en Actas Minem (N)
        n_supervisar = C / ((d**2) + (C / actas_minem))
        porcentaje_fijo = (n_supervisar / actas_minem) * 100

        # Resumen Global
        col_r1, col_r2, col_r3 = st.columns(3)
        col_r1.metric("Población Confirmada (N)", f"{actas_minem:,.2f} m")
        col_r2.metric("Muestra Física a Auditar (n)", f"{n_supervisar:,.2f} m")
        col_r3.metric("Porcentaje de Supervisión", f"{porcentaje_fijo:.2f} %")

        st.divider()

        # Función para crear matriz y gráfico para no repetir código
        def generar_reporte_estrato(titulo, datos_dict, color_grafico):
            st.subheader(f"Distribución por {titulo}")
            
            # Construcción de la matriz (DataFrame)
            filas_tabla = []
            etiquetas = []
            valores_n = []
            
            for estrato, metros in datos_dict.items():
                Wh = metros / actas_minem
                nh = n_supervisar * Wh
                
                etiquetas.append(estrato)
                valores_n.append(nh)
                
                filas_tabla.append({
                    "Categoría": estrato,
                    "Longitud Declarada (m)": f"{metros:,.2f}",
                    "Peso Estrato (Wh)": f"{Wh:.4f}",
                    "Meta Física a Supervisar (nh)": f"{nh:,.2f}"
                })
            
            # Mostrar Tabla
            df = pd.DataFrame(filas_tabla)
            st.table(df)
            
            # Mostrar Gráfico de Barras
            fig, ax = plt.subplots(figsize=(8, 4))
            barras = ax.bar(etiquetas, valores_n, color=color_grafico, edgecolor='black', alpha=0.8)
            
            # Poner etiquetas de datos sobre cada barra
            for bar in barras:
                yval = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2, yval + (max(valores_n)*0.02), f'{yval:.1f} m', ha='center', fontweight='bold')
                
            ax.set_ylabel('Metros a Supervisar (nh)', fontsize=10)
            ax.set_title(f'Muestreo Físico: {titulo}', fontsize=12, fontweight='bold')
            ax.grid(axis='y', linestyle=':', alpha=0.7)
            
            # Ajuste de diseño
            plt.tight_layout()
            st.pyplot(fig)

        # Dividimos la pantalla en dos columnas para mostrar ambos reportes lado a lado
        col_izq, col_der = st.columns(2)
        
        with col_izq:
            generar_reporte_estrato("Tipo de Terreno", datos_terreno, '#2ca02c') # Verde
            
        with col_der:
            generar_reporte_estrato("Tipo de Pavimento", datos_pavimento, '#ff7f0e') # Naranja

else:
    st.info("👈 Por favor, ingresa un valor mayor a 0 en el Total de Actas (Minem).")
