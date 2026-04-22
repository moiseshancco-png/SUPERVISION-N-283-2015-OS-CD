import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# Configuración de la página
st.set_page_config(page_title="Calculadora Supervisión GN", layout="wide")

st.title("Calculadora de Supervisión: Redes de Polietileno")
st.markdown("Distribución de muestra según **Resolución N° 283-2015-OS/CD**")

# 1. Constantes normativas
t_alpha = 1.645
d = 0.05
S2h = 0.25
C = (t_alpha**2) * S2h
asintota_max = C / (d**2)

# 2. Interfaz de usuario (Inputs web)
st.sidebar.header("Ingreso de Datos")
num_estratos = st.sidebar.number_input("Cantidad de diámetros (estratos):", min_value=1, max_value=10, value=2, step=1)

datos_estratos = {}
tope_de_obra_m = 0.0

for i in range(int(num_estratos)):
    col1, col2 = st.sidebar.columns(2)
    with col1:
        diametro = st.text_input(f"Diámetro {i+1} (mm):", value=f"PE {110 if i==0 else 63}", key=f"d_{i}")
    with col2:
        metros = st.number_input(f"Metros:", min_value=0.0, value=1000.0 if i==0 else 500.0, step=100.0, key=f"m_{i}")
    
    if diametro and metros > 0:
        datos_estratos[diametro] = metros
        tope_de_obra_m += metros

# 3. Cálculos y Gráfica (Solo se ejecuta si hay datos)
if tope_de_obra_m > 0:
    n_supervisar = C / ((d**2) + (C / tope_de_obra_m))
    porcentaje_fijo = (n_supervisar / tope_de_obra_m) * 100

    # Contenedores para mostrar resultados
    st.subheader("Resultados de la Muestra")
    col_res1, col_res2, col_res3 = st.columns(3)
    col_res1.metric("Población Total (N)", f"{tope_de_obra_m:,.2f} m")
    col_res2.metric("Meta Física (n)", f"{n_supervisar:,.2f} m")
    col_res3.metric("Porcentaje a Auditar", f"{porcentaje_fijo:.2f} %")

    # Tabla de afijación proporcional
    st.markdown("### Distribución por Afijación Proporcional ($W_h$)")
    
    # Creamos listas para armar la tabla
    tabla_datos = []
    distribucion_nh = {}
    
    for diam, met in datos_estratos.items():
        Wh = met / tope_de_obra_m
        nh = n_supervisar * Wh
        distribucion_nh[diam] = nh
        tabla_datos.append({"Diámetro": diam, "Población (m)": met, "Peso (Wh)": round(Wh, 4), "Meta Física (m)": round(nh, 2)})
        
    st.table(tabla_datos)

    # Gráfica
    st.markdown("### Comportamiento Asintótico")
    x_max_grafica = max(15000, tope_de_obra_m * 1.5)
    N_valores = np.linspace(10, x_max_grafica, 1000)
    n_valores = C / ((d**2) + (C / N_valores))

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(N_valores, n_valores, color='#1f77b4', linewidth=3, label='Curva de cálculo ($n$)')
    ax.axhline(y=asintota_max, color='red', linestyle='--', linewidth=2, alpha=0.8, label=f'Asíntota Máx: ~{asintota_max:.1f} m')
    ax.plot(tope_de_obra_m, n_supervisar, marker='o', markersize=9, color='black', zorder=5)
    
    # Líneas guía
    ax.vlines(x=tope_de_obra_m, ymin=0, ymax=n_supervisar, color='gray', linestyle=':', alpha=0.7)
    ax.hlines(y=n_supervisar, xmin=0, xmax=tope_de_obra_m, color='gray', linestyle=':', alpha=0.7)

    # Anotación
    texto_punto = f'Expediente:\nN: {tope_de_obra_m:,.0f} m\nn: {n_supervisar:.1f} m'
    offset_x = -0.15 if tope_de_obra_m > (x_max_grafica * 0.7) else 0.03
    ax.annotate(texto_punto, xy=(tope_de_obra_m, n_supervisar), 
                xytext=(tope_de_obra_m + (x_max_grafica * offset_x), n_supervisar - 50),
                bbox=dict(boxstyle="round,pad=0.5", fc="#f8f9fa", ec="gray", lw=1.5),
                arrowprops=dict(arrowstyle="->", color='black', lw=1.5))

    ax.set_title('Evaluación de Supervisión', fontsize=12)
    ax.set_xlabel('Población Total ($N$ en metros)')
    ax.set_ylabel('Metros Físicos a Supervisar ($n$)')
    ax.set_xlim(0, x_max_grafica)
    ax.set_ylim(0, asintota_max * 1.2)
    ax.grid(True, linestyle='--', alpha=0.5)
    ax.legend(loc='lower right')

    # Enviar gráfica a la web
    st.pyplot(fig)
else:
    st.info("Ingresa los datos del proyecto en el panel lateral izquierdo para calcular.")
