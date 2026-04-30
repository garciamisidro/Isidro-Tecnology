# Isidro-Tecnology
Esta APP permite tener un seguimiento de la obra.
import streamlit as st
import pandas as pd
from datetime import date
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Seguimiento de Obra", layout="centered")

# 1. Incorporar logo de la empresa
# st.image("logo_empresa.png", width=200) 
st.title("🏗️ Sistema de Seguimiento de Obra")

# --- FORMULARIO DE ENTRADA ---
with st.form("formulario_obra"):
    col1, col2 = st.columns(2)
    
    with col1:
        trabajador = st.text_input("Nombre del Trabajador")
        fecha = st.date_input("Fecha de envío", date.today())
    
    # 2. Desplegable de tareas
    tareas = [
        "Trazado y marcado de cajas, tubos y cuadros", "Ejecución rozas en paredes y techos",
        "Montaje de soportes", "Colocación tubos y conductos", "Tendido de cables",
        "Identificación y etiquetado", "Conexionado de cables en bornes o regletas",
        "Instalación y conexionado de mecanismos", "Fijación de carril DIN y mecanismos en cuadro eléctrico",
        "Cableado interno del cuadro eléctrico", "Configuración de equipos domóticos y/o automáticos",
        "Conexionado de sensores/actuadores de equipos domóticos/automáticos", "Pruebas de continuidad",
        "Pruebas de aislamiento", "Verificación de tierras", "Programación del automatismo", "Pruebas de funcionamiento"
    ]
    tarea_sel = st.selectbox("Seleccione la Tarea:", tareas)
    
    # 3. Desplegable de estado
    estados = [
        "Avance de la tarea en torno al 25% aprox.", "Avance de la tarea en torno al 50% aprox.",
        "Avance de la tarea en torno al 75% aprox.", "OK, finalizado sin errores",
        "Finalizado, pero con errores pendientes de corregir", "Finalizado y corregidos los errores"
    ]
    estado_sel = st.selectbox("Estado de la tarea:", estados)
    
    enviado = st.form_submit_button("Registrar Datos")

# --- GESTIÓN DE DATOS (Pandas) ---
if "datos_obra" not in st.session_state:
    st.session_state.datos_obra = pd.DataFrame(columns=["Fecha", "Trabajador", "Tarea", "Estado"])

if enviado:
    nuevo_registro = {"Fecha": fecha, "Trabajador": trabajador, "Tarea": tarea_sel, "Estado": estado_sel}
    st.session_state.datos_obra = pd.concat([st.session_state.datos_obra, pd.DataFrame([nuevo_registro])], ignore_index=True)
    st.success("Registro añadido localmente.")

# Mostrar tabla actual
st.dataframe(st.session_state.datos_obra)

# --- EXPORTACIÓN Y ENVÍO ---
# Generar Excel
nombre_archivo = "reporte_obra.xlsx"
st.session_state.datos_obra.to_excel(nombre_archivo, index=False)

with open(nombre_archivo, "rb") as f:
    st.download_button("📥 Descargar Excel", f, file_name=nombre_archivo)

# Botón para envío por correo
if st.button("📧 Enviar Reporte por Correo"):
    # Aquí iría la lógica de smtplib usando st.secrets para la seguridad
    st.info("Función de envío activada (Configurar SMTP con Secrets de Streamlit)")
