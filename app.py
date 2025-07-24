
import streamlit as st
import pandas as pd
import openai
import os

# Configurar clave de OpenAI
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Cargar el archivo Excel
@st.cache_data
def cargar_datos():
    df = pd.read_excel("BASE_DE_DATOS_DE_HORAS.xlsx", sheet_name="Detalle")
    df["NombreCompleto"] = df["Nombre"].str.strip() + " " + df["Apellido"].str.strip()
    return df

df = cargar_datos()

# Función para generar un filtro a partir de una pregunta usando OpenAI
def generar_consulta(pregunta):
    prompt = f"""
Tenés una tabla con las siguientes columnas: Cliente, Proyecto, Tarea, Apellido, Nombre, NombreCompleto, HorasImputadas, Año, Mes.

Convertí la siguiente pregunta de usuario en instrucciones claras de filtrado para aplicar sobre un DataFrame de pandas. Devolveme solo el código Python dentro de triple backticks.

Pregunta: {pregunta}
"""
    respuesta = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{ "role": "user", "content": prompt }],
        temperature=0
    )

    contenido = respuesta.choices[0].message["content"]

    # Extraer código entre ```
    if "```" in contenido:
        codigo = contenido.split("```")[1]
    else:
        codigo = contenido
    return codigo.strip()

# Interfaz de usuario
st.title("🧠 Agente de Consulta de Horas (versión inteligente)")
st.write("Consultá en lenguaje natural sobre la base de imputaciones de horas.")

pregunta = st.text_input("Escribí tu pregunta:")

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
            st.error(f"Hubo un error al procesar la consulta: {e}")
