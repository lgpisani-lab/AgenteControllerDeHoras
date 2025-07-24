
import streamlit as st
import pandas as pd
import openai

openai.api_key = st.secrets["OPENAI_API_KEY"]

st.set_page_config(page_title="Agente de Horas", layout="centered")
st.title("🧠 Agente de Consulta de Horas (desde Google Drive)")

# Link directo al archivo exportado como .xlsx
EXCEL_URL = "https://docs.google.com/spreadsheets/d/1sHvcvlO_86qHpwX7wNFHLEgwaBemUHs7/export?format=xlsx"

# Cargar Excel directamente desde Google Drive
try:
    df = pd.read_excel(EXCEL_URL, sheet_name="Detalle")
    df["NombreCompleto"] = df["Nombre"].str.strip() + " " + df["Apellido"].str.strip()
    st.success("✅ Archivo cargado desde Google Drive.")
except Exception as e:
    st.error(f"❌ Error al cargar el archivo desde Google Drive: {e}")
    st.stop()

# Entrada de consulta
st.write("Escribí tu consulta en lenguaje natural:")
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
