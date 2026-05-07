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

# --- ANÁLISIS DE DATOS Y PREDICCIÓN ---
if not st.session_state.datos_obra.empty:
    st.divider()
    st.subheader("📊 Panel de Control e IA de Seguimiento")

    # 1. Mapeo de estados a valores numéricos para cálculo
    valor_estado = {
        "Avance de la tarea en torno al 25% aprox.": 25,
        "Avance de la tarea en torno al 50% aprox.": 50,
        "Avance de la tarea en torno al 75% aprox.": 75,
        "OK, finalizado sin errores": 100,
        "Finalizado, pero con errores pendientes de corregir": 90,
        "Finalizado y corregidos los errores": 100
    }

    # Calculamos el progreso medio de todas las tareas registradas
    progreso_total = st.session_state.datos_obra["Estado"].map(valor_estado).mean()

    # 2. Barra de carga visual
    st.write(f"**Progreso acumulado de la obra:** {progreso_total:.1f}%")
    st.progress(progreso_total / 100)

    # 3. Cálculo de Predicción de Finalización (IA Sencilla)
    # Suponemos que cada 1% de progreso toma un tiempo determinado desde la fecha inicial
    fecha_inicio = pd.to_datetime(st.session_state.datos_obra["Fecha"]).min().date()
    hoy = date.today()
    dias_transcurridos = (hoy - fecha_inicio).days + 1 # +1 para evitar división por cero

    if progreso_total > 0:
        # Velocidad actual: % por día
        velocidad = progreso_total / dias_transcurridos
        # Días restantes para llegar al 100%
        dias_restantes = (100 - progreso_total) / velocidad
        
        fecha_estimada = hoy + pd.Timedelta(days=int(dias_restantes))
        
        # Mostrar métricas
        col_m1, col_m2 = st.columns(2)
        col_m1.metric("Días trabajados", dias_transcurridos)
        col_m2.metric("Fecha fin estimada", fecha_estimada.strftime("%d/%m/%Y"))
        
        st.info(f"💡 **Análisis Predictivo:** Al ritmo actual ({velocidad:.1f}% diario), la obra finalizará aproximadamente el {fecha_estimada.strftime('%d de %B de %Y')}.")
    else:
        st.warning("Aún no hay suficiente avance para calcular una predicción.")

# --- EXPORTACIÓN Y ENVÍO ---
# Generar Excel
nombre_archivo = "reporte_presupuesto.xlsx"
st.session_state.datos_presupuesto.to_excel(nombre_archivo, index=False)

col_descarga, col_correo = st.columns(2)

with col_descarga:
    with open(nombre_archivo, "rb") as f:
        st.download_button("📥 Descargar Excel", f, file_name=nombre_archivo)

with col_correo:
    if st.button("📧 Enviar por Correo"):
        try:
            # 1. Recuperar credenciales de los Secrets
            usuario = st.secrets["email"]["user"]
            password = st.secrets["email"]["pass"]
            profe = st.secrets["email"]["profe"]

            # 2. Configurar el mensaje
            msg = MIMEMultipart()
            msg['From'] = usuario
            msg['To'] = f"{profe}, {usuario}"  # Envía a ambos
            msg['Subject'] = f"Reporte Presupuesto - {trabajador}"

            # Cuerpo del mensaje
            cuerpo = f"Se adjunta el reporte de presupuesto generado el {fecha} por {trabajador}."
            msg.attach(MIMEText(cuerpo, 'plain'))

            # 3. Adjuntar el archivo Excel
            with open(nombre_archivo, "rb") as adjunto:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(adjunto.read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', f"attachment; filename= {nombre_archivo}")
                msg.attach(part)

            # 4. Envío por servidor SMTP (Gmail por defecto)
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(usuario, password)
            server.send_message(msg)
            server.quit()

            st.success("✅ Correo enviado con éxito a la profesora y a tu cuenta.")
        
        except Exception as e:
            st.error(f"❌ Error al enviar: {e}")
            st.info("Asegúrate de haber configurado los 'Secrets' en Streamlit Cloud.")

# Botón para envío por correo
if st.button("📧 Enviar Reporte por Correo"):
    # Aquí iría la lógica de smtplib usando st.secrets para la seguridad
    st.info("Función de envío activada (Configurar SMTP con Secrets de Streamlit)")
