import streamlit as st
import pandas as pd
from datetime import date
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

# --- 1. CONFIGURACIÓN DE PÁGINA Y ESTADO ---
st.set_page_config(page_title="Seguimiento de Obra PRO", layout="centered")

if "datos_obra" not in st.session_state:
    st.session_state.datos_obra = pd.DataFrame(columns=["Fecha", "Trabajador", "Tarea", "Estado"])

st.title("🏗️ Seguimiento de Obra Inteligente")

# --- 2. FORMULARIO DE ENTRADA ---
with st.form("formulario_registro", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        trabajador = st.text_input("Nombre del Trabajador")
        fecha_envio = st.date_input("Fecha de envío", date.today())
    
    tareas_lista = [
        "Trazado y marcado de cajas, tubos y cuadros", "Ejecución rozas en paredes y techos",
        "Montaje de soportes", "Colocación tubos y conductos", "Tendido de cables",
        "Identificación y etiquetado", "Conexionado de cables en bornes o regletas",
        "Instalación y conexionado de mecanismos", "Fijación de carril DIN y mecanismos en cuadro eléctrico",
        "Cableado interno del cuadro eléctrico", "Configuración de equipos domóticos y/o automáticos",
        "Conexionado de sensores/actuadores de equipos domóticos/automáticos", "Pruebas de continuidad",
        "Pruebas de aislamiento", "Verificación de tierras", "Programación del automatismo", "Pruebas de funcionamiento"
    ]
    tarea_sel = st.selectbox("Seleccione la tarea:", tareas_lista)
    
    estados_lista = [
        "Avance de la tarea en torno al 25% aprox.", "Avance de la tarea en torno al 50% aprox.",
        "Avance de la tarea en torno al 75% aprox.", "OK, finalizado sin errores",
        "Finalizado, pero con errores pendientes de corregir", "Finalizado y corregidos los errores"
    ]
    estado_sel = st.selectbox("Estado de la tarea:", estados_lista)
    
    boton_registro = st.form_submit_button("Registrar Informe")

if boton_registro and trabajador:
    nuevo_registro = {"Fecha": fecha_envio, "Trabajador": trabajador, "Tarea": tarea_sel, "Estado": estado_sel}
    st.session_state.datos_obra = pd.concat([st.session_state.datos_obra, pd.DataFrame([nuevo_registro])], ignore_index=True)
    st.success("✅ Registro añadido.")

# --- 3. DASHBOARD Y PREDICCIÓN (RA3 + RA4) ---
if not st.session_state.datos_obra.empty:
    st.divider()
    st.subheader("📊 Análisis de Progreso y Predicción")

    # Mapeo para cálculos
    valor_estado = {
        "Avance de la tarea en torno al 25% aprox.": 25,
        "Avance de la tarea en torno al 50% aprox.": 50,
        "Avance de la tarea en torno al 75% aprox.": 75,
        "OK, finalizado sin errores": 100,
        "Finalizado, pero con errores pendientes de corregir": 90,
        "Finalizado y corregidos los errores": 100
    }

    # Cálculo de progreso
    progreso_medio = st.session_state.datos_obra["Estado"].map(valor_estado).mean()
    st.write(f"**Progreso total de la obra:** {progreso_medio:.1f}%")
    st.progress(progreso_medio / 100)

    # Lógica Predictiva (IA Sencilla)
    fecha_inicio = pd.to_datetime(st.session_state.datos_obra["Fecha"]).min().date()
    dias_transcurridos = (date.today() - fecha_inicio).days + 1
    
    if progreso_medio > 0:
        velocidad = progreso_medio / dias_transcurridos
        dias_restantes = (100 - progreso_medio) / velocidad
        fecha_fin = date.today() + pd.Timedelta(days=int(dias_restantes))
        
        c1, c2 = st.columns(2)
        c1.metric("Días trabajados", dias_transcurridos)
        c2.metric("Fecha estimada de fin", fecha_fin.strftime("%d/%m/%Y"))
        st.info(f"💡 Al ritmo actual ({velocidad:.1f}% diario), se estima terminar el {fecha_fin.strftime('%d/%m/%Y')}.")

    # --- 4. EXPORTACIÓN Y ENVÍO ---
    st.divider()
    st.dataframe(st.session_state.datos_obra)
    
    nombre_archivo = "reporte_obra.xlsx"
    st.session_state.datos_obra.to_excel(nombre_archivo, index=False)

    col_b1, col_b2 = st.columns(2)
    with col_b1:
        with open(nombre_archivo, "rb") as f:
            st.download_button("📥 Descargar Excel", f, file_name=nombre_archivo)
    with col_b2:
        if st.button("📧 Enviar por Correo"):
            try:
                u, p, prof = st.secrets["email"]["user"], st.secrets["email"]["pass"], st.secrets["email"]["profe"]
                msg = MIMEMultipart()
                msg['From'], msg['To'], msg['Subject'] = u, f"{prof}, {u}", "Reporte Obra Actualizado"
                msg.attach(MIMEText("Se adjunta el seguimiento de obra.", 'plain'))
                with open(nombre_archivo, "rb") as a:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(a.read())
                    encoders.encode_base64(part)
                    part.add_header('Content-Disposition', f"attachment; filename={nombre_archivo}")
                    msg.attach(part)
                s = smtplib.SMTP('smtp.gmail.com', 587)
                s.starttls()
                s.login(u, p)
                s.send_message(msg)
                s.quit()
                st.success("✅ Enviado correctamente.")
            except Exception as e:
                st.error(f"Error: {e}")
else:
    st.info("👋 Registra una tarea para ver el análisis de progreso y predicción.")
