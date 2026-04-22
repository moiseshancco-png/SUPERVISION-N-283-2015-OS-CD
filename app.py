import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# Configuración de la página web
st.set_page_config(page_title="Proyección de Supervisión", layout="wide")

st.title("Calculadora de Supervisión de Redes de Gas Natural")
st.markdown("Distribución de muestreo según **Resolución N° 283-2015-OS/CD**")

# 1. Constantes normativas
t_alpha = 1.645
d = 0.05
S2h = 0.25  # Varianza máxima asumida
C = (t_alpha**2) * S2h
asintota_max = C / (d**2)

# 2. Interfaz de usuario (Panel Lateral)
st.sidebar.header("Ingreso de Datos")
num_estratos = st.sidebar.number_input("Cantidad de estratos/diámetros:", min_value=1, max_value=10, value=2, step=1)

datos_estratos = {}
tope_de_obra_m = 0.0

for i in range(int(num_estratos)):
    col1, col2 = st.sidebar.columns(2)
    with col1:
        diametro = st.text_input(f"Diámetro {i+1} [mm]:", value=f"{110 if i==0 else 63}", key=f"d_{i}")
    with col2:
        metros = st.number_input(f"Longitud [m]:", min_value=0.0, value=1000.0 if i==0 else 500.0, step=100.0, key=f"m_{i}")
    
    if diametro and metros > 0:
        datos_estratos[diametro] = metros
        tope_de_obra_m += metros

# 3. Cálculos y Resultados
if tope_de_obra_m > 0:
    n_supervisar = C / ((d**2) + (C / tope_de_obra_m))
    porcentaje_fijo = (n_supervisar / tope_de_obra_m) * 100

    # Resumen principal
    st.subheader("=== RESUMEN FINAL DEL EXPEDIENTE ===")
    col_res1, col_res2, col_res3 = st.columns(3)
    col_res1.metric("Total del proyecto (N)", f"{tope_de_obra_m:,.2f} m")
    col_res2.metric("Total físico a supervisar (n)", f"{n_supervisar:,.2f} m")
    col_res3.metric("Porcentaje a auditar", f"{porcentaje_fijo:.2f} %")

    # Tabla de afijación proporcional
    st.markdown("### === DISTRIBUCIÓN POR ESTRATOS ===")
    
    tabla_datos = []
    for diam, met in datos_estratos.items():
        Wh = met / tope_de_obra_m
        nh = n_supervisar * Wh
        porc_nh = (nh / tope_de_obra_m) * 100
        
        tabla_datos.append({
            "Diámetro (mm)": diam, 
            "Población (N_h)": f"{met:,.2f} m",  
            "A Supervisar (n_h)": f"{nh:,.2f} m",
            "% del Total": f"{porc_nh:.2f} %"
        })
        
    st.table(tabla_datos)

    # 4. Gráfica (Respetando tus modificaciones exactas)
    #st.markdown("### Proyección de Supervisión")
    
    # Tu ajuste en el eje X
    x_max_grafica = max(tope_de_obra_m, tope_de_obra_m * 1.5)
    N_valores = np.linspace(10, x_max_grafica, 1000)
    n_valores = C / ((d**2) + (C / N_valores))

    fig, ax = plt.subplots(figsize=(11, 6))

    # Curva de cálculo con tu etiqueta
    ax.plot(N_valores, n_valores, color='#1f77b4', linewidth=3, label='Curva de muestreo ($n$)')

    # Asíntota
    ax.axhline(y=asintota_max, color='red', linestyle='--', linewidth=2, alpha=0.8,
                label=f'Asíntota (Cota Máx: ~{asintota_max:.1f} m)')

    # Punto específico de tu proyecto
    ax.plot(tope_de_obra_m, n_supervisar, marker='o', markersize=9, color='black', zorder=5)

    # Líneas punteadas guía para el punto
    ax.vlines(x=tope_de_obra_m, ymin=0, ymax=n_supervisar, color='gray', linestyle=':', alpha=0.7)
    ax.hlines(y=n_supervisar, xmin=0, xmax=tope_de_obra_m, color='gray', linestyle=':', alpha=0.7)

    # Caja de texto explicativa con tus textos exactos
    texto_punto = (
        f'Tu Expediente:\n'
        f'• Total (N): {tope_de_obra_m:,.0f} m\n'
        f'• Muestreo (n): {n_supervisar:.1f} m\n'
        f'• % Supervisión: {porcentaje_fijo:.2f} %'
    )

    offset_x = -0.15 if tope_de_obra_m > (x_max_grafica * 0.7) else 0.03

    ax.annotate(texto_punto,
                 xy=(tope_de_obra_m, n_supervisar),
                 xytext=(tope_de_obra_m + (x_max_grafica * offset_x), n_supervisar - 60),
                 bbox=dict(boxstyle="round,pad=0.5", fc="#f8f9fa", ec="gray", lw=1.5),
                 arrowprops=dict(arrowstyle="->", connectionstyle="arc3", color='black', lw=1.5),
                 fontsize=10)

    # Formato visual del gráfico con tus títulos
    ax.set_title('Proyección de Supervisión', fontsize=14, pad=15, fontweight='bold')
    ax.set_xlabel('Total del Proyecto ($N$ en metros)', fontsize=12)
    ax.set_ylabel('Muestreo de Cantidad Supervisada ($n$)', fontsize=12)

    # Fijar límites
    ax.set_xlim(0, x_max_grafica)
    ax.set_ylim(0, asintota_max * 1.2)

    ax.grid(True, linestyle='--', alpha=0.5)
    ax.legend(loc='lower right', fontsize=11)

    # Enviar la figura a Streamlit
    st.pyplot(fig)

else:
    st.info("👈 Por favor, ingresa los datos del expediente en el panel lateral para generar el reporte y la proyección.")
