
import streamlit as st
import pandas as pd
import openai

# Clave de API desde secretos de Streamlit
openai.api_key = st.secrets["OPENAI_API_KEY"]

st.title("🧠 Agente de Consulta de Horas - Seguro")
st.write("Cargá tu archivo Excel y hacé preguntas en lenguaje natural.")

# Subida de archivo
archivo = st.file_uploader("Subí el archivo Excel (.xlsx)", type=["xlsx"])

if archivo:
    try:
        df = pd.read_excel(archivo, sheet_name="Detalle")
        df["NombreCompleto"] = df["Nombre"].str.strip() + " " + df["Apellido"].str.strip()

        pregunta = st.text_input("Escribí tu pregunta:")

        def generar_consulta(pregunta):
            prompt = f"""
Tenés una tabla con las siguientes columnas: Cliente, Proyecto, Tarea, Apellido, Nombre, NombreCompleto, HorasImputadas, Año, Mes.

Convertí la siguiente pregunta del usuario en código Python para filtrar un DataFrame de pandas llamado df. Mostrá solo el código entre triple backticks.

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
                    codigo_filtro = generar_consulta(pregunta)
                    st.code(codigo_filtro, language="python")
                    resultado = eval(codigo_filtro, {"df": df})
                    if isinstance(resultado, pd.DataFrame):
                        st.dataframe(resultado)
                        st.success(f"Se encontraron {len(resultado)} registros.")
                    elif isinstance(resultado, (float, int)):
                        st.success(f"Resultado: {resultado:.2f} horas")
                    else:
                        st.write(resultado)
                except Exception as e:
                    st.error(f"Error al ejecutar la consulta: {e}")
    except Exception as ex:
        st.error(f"No se pudo leer el archivo Excel: {ex}")
else:
    st.info("Esperando que cargues un archivo Excel...")
