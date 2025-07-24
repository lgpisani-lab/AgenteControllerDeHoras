
import streamlit as st
import pandas as pd
import openai

openai.api_key = st.secrets["OPENAI_API_KEY"]

st.set_page_config(page_title="Agente de Horas", layout="centered")
st.title("🧠 Agente de Consulta de Horas - Sesión Administrada")

# Bloque para carga de archivo (solo admin lo debería hacer)
archivo = st.file_uploader("🔐 Solo el administrador debe subir el archivo de horas", type=["xlsx"])

if archivo and "df" not in st.session_state:
    try:
        df = pd.read_excel(archivo, sheet_name="Detalle")
        df["NombreCompleto"] = df["Nombre"].str.strip() + " " + df["Apellido"].str.strip()
        st.session_state["df"] = df
        st.success("✅ Archivo cargado correctamente. Ya podés hacer consultas.")
    except Exception as e:
        st.error(f"Error al leer el archivo: {e}")

# Verificamos si hay datos cargados
if "df" in st.session_state:
    df = st.session_state["df"]

    st.write("Escribí tu consulta en lenguaje natural sobre el archivo cargado:")
    pregunta = st.text_input("📥 Consulta:")

    def generar_consulta(pregunta):
        prompt = f"""
Tenés una tabla con las siguientes columnas: Cliente, Proyecto, Tarea, Apellido, Nombre, NombreCompleto, HorasImputadas, Año, Mes.

Convertí la siguiente pregunta del usuario en código Python para filtrar un DataFrame de pandas llamado df.
Devolvé solo el código Python entre triple backticks, sin explicaciones.

Pregunta: {pregunta}
"""
        respuesta = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{ "role": "user", "content": prompt }],
            temperature=0
        )
        contenido = respuesta.choices[0].message["content"]
        if "```" in contenido:
            return contenido.split("```")[1].strip()
        return contenido.strip()

    if pregunta:
        with st.spinner("Interpretando tu consulta..."):
            try:
                codigo = generar_consulta(pregunta)
                st.code(codigo, language="python")
                resultado = eval(codigo, {"df": df})
                if isinstance(resultado, pd.DataFrame):
                    st.dataframe(resultado)
                    st.success(f"Se encontraron {len(resultado)} registros.")
                elif isinstance(resultado, (float, int)):
                    st.success(f"Resultado: {resultado:.2f} horas")
                else:
                    st.write(resultado)
            except Exception as e:
                st.error(f"Error al ejecutar la consulta: {e}")
else:
    st.info("⚠️ Aún no se ha cargado ningún archivo de datos. Subilo para comenzar.")
